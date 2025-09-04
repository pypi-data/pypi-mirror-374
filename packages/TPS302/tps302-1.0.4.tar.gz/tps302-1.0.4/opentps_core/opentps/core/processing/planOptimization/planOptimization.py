import logging
import math
from typing import Iterable

import numpy as np
import scipy.sparse as sp

from opentps.core.processing.planOptimization.objectives.doseFidelity import DoseFidelity

try:
    import sparse_dot_mkl
    use_MKL = 0  # Currently deactivated on purpose because sparse_dot_mkl generates seg fault
except:
    use_MKL = 0

cupy_available = False
try:
    import cupy as cp
    import cupyx as cpx
    cupy_available = True
except:
    cupy_available = False

from opentps.core.data.plan._rtPlan import RTPlan
from opentps.core.processing.planOptimization.solvers import scipyOpt, bfgs, localSearch, fista, gradientDescent
from opentps.core.processing.planOptimization import planPreprocessing
from scipy.sparse import csc_matrix
from opentps.core.data.images._doseImage import DoseImage

logger = logging.getLogger(__name__)


class PlanOptimizer:
    """
    This class is used to optimize a plan.

    Attributes
    ----------
    plan : RTPlan
        The plan to optimize.
    opti_params : dict
        The optimization parameters.
    functions : list
        The list of functions to optimize.
    solver : Solver (default: scipyOpt.ScipyOpt('L-BFGS-B'))
        The solver to use. By default, no bounds are set. Machine delivery constraints can (and should) be enforced
        by setting the bounds.
    thresholdSpotRemoval : float
        The threshold weight below which spots are removed from the plan and beamlet matrix.
    xSquared : bool
        If True, the weights are squared. True by default to avoid negative weights.
    GPU_acceleration : bool (default : False)
        If True, the evaluation of the doseFidelity function is done with cupy (this attribute should only
        be modified with the "use_GPU_acceleration" function)
    """
    def __init__(self, plan:RTPlan, **kwargs):

        self.solver = scipyOpt.ScipyOpt('L-BFGS-B')
        planPreprocessing.extendPlanLayers(plan)
        self.plan = plan
        self.opti_params = kwargs
        self.functions = []
        self._xSquared = True
        self.thresholdSpotRemoval = 1e-6
        self.GPU_acceleration = False

    @property
    def xSquared(self):
        return self._xSquared

    @xSquared.setter
    def xSquared(self, x2):
        self._xSquared = x2

    def use_GPU_acceleration(self):
        """
        Enable the uses of the GPU via cupy and cupyx (both library need to be installed as well as CUDA).
        """
        if cupy_available:
            self.GPU_acceleration = True
            logger.info('cupy imported in planOptimization module')
            logger.info('abnormal used memory: {}'.format(cp.get_default_memory_pool().used_bytes()))
        else:
            logger.info('Unable to import CUPY, please configure CUPY to enable GPU acceleration')
            self.GPU_acceleration = False

    def stop_GPU_accelration(self):
        """
        stop the use of GPU acceleration
        """
        self.GPU_acceleration = False
        logger.info('GPU accelerations deactivated')

    def initializeWeights(self):
        """
        Initialize the weights.

        Returns
        -------
        x0 : numpy.ndarray
            The weights.
        """
        # Total Dose calculation
        totalDose = self.computeDose().imageArray
        maxDose = np.max(totalDose)
        try:
            x0 = self.opti_params['init_weights']
            logger.info('Initial weights are given by user')
        except KeyError:
            if isinstance(self.plan.planDesign.objectives.targetPrescription, Iterable):
                normFactor = self.plan.planDesign.objectives.targetPrescription[0] / maxDose
            else:
                normFactor = self.plan.planDesign.objectives.targetPrescription / maxDose
            if self.xSquared:
                normFactor = math.sqrt(normFactor)
            x0 = normFactor * np.ones(self.plan.planDesign.beamlets.shape[1], dtype=np.float32)

        return x0

    def _get_sparse_from_any(self, maybe_wrapper):
        """
        Helper to get a scipy.sparse.csc_matrix from either a beamlet wrapper (with toSparseMatrix)
        or a plain scipy sparse matrix already.
        """
        if maybe_wrapper is None:
            return None, False
        # wrapper?
        if hasattr(maybe_wrapper, 'toSparseMatrix') and callable(maybe_wrapper.toSparseMatrix):
            return maybe_wrapper.toSparseMatrix(), True
        # already a sparse matrix
        if sp.issparse(maybe_wrapper):
            return maybe_wrapper, False
        raise TypeError("beamletsLET must be either a Beamlets-like object with toSparseMatrix() or a scipy.sparse matrix")

    def _set_unitary_on_any(self, target, new_csc):
        """
        Mirror of setUnitaryBeamlets for LET if present as wrapper; otherwise just return the csc.
        """
        if hasattr(target, 'setUnitaryBeamlets') and callable(target.setUnitaryBeamlets):
            target.setUnitaryBeamlets(new_csc)
            return target, True
        # if it's a plain sparse matrix, we just return the cropped matrix
        return new_csc, False

    def initializeFidObjectiveFunction(self):
        """
        Initialize the dose fidelity objective function (+ optional LET).
        """
        self.plan.planDesign.setScoringParameters()
        # crop on ROI
        roiObjectives = np.zeros(len(self.plan.planDesign.objectives.fidObjList[0].maskVec)).astype(bool)
        roiRobustObjectives = np.zeros(len(self.plan.planDesign.objectives.fidObjList[0].maskVec)).astype(bool)
        robust = False
        for objective in self.plan.planDesign.objectives.fidObjList:
            if objective.robust:
                robust = True
                roiRobustObjectives = np.logical_or(roiRobustObjectives, objective.maskVec)
            else:
                roiObjectives = np.logical_or(roiObjectives, objective.maskVec)
        roiObjectives = np.logical_or(roiObjectives, roiRobustObjectives)

        # --- crop dose beamlets as before ---
        if use_MKL == 1:
            beamletMatrix = sparse_dot_mkl.dot_product_mkl(
                sp.diags(roiObjectives.astype(np.float32), format='csc'), self.plan.planDesign.beamlets.toSparseMatrix())
        else:
            beamletMatrix = sp.csc_matrix.dot(sp.diags(roiObjectives.astype(np.float32), format='csc'),
                                              self.plan.planDesign.beamlets.toSparseMatrix())
        self.plan.planDesign.beamlets.setUnitaryBeamlets(beamletMatrix)

        # --- crop LET beamlets if enabled and provided (nominal only; no robust LET per requirement) ---
        useLET = bool(self.opti_params.get('useLET', False))
        let_wrapper = getattr(self.plan.planDesign, 'beamletsLET', None)
        let_csc, let_is_wrapper = (None, False)
        if useLET and let_wrapper is not None:
            let_csc, _ = self._get_sparse_from_any(let_wrapper)
            if let_csc is not None:
                if use_MKL == 1:
                    let_cropped = sparse_dot_mkl.dot_product_mkl(
                        sp.diags(roiObjectives.astype(np.float32), format='csc'), let_csc)
                else:
                    let_cropped = sp.csc_matrix.dot(sp.diags(roiObjectives.astype(np.float32), format='csc'), let_csc)
                # write back cropped LET
                new_obj, _ = self._set_unitary_on_any(let_wrapper, let_cropped)
                # If plain matrix, store back for later use by DoseFidelity through plan.planDesign.beamletsLET
                if not hasattr(new_obj, 'toSparseMatrix'):
                    self.plan.planDesign.beamletsLET = new_obj

        # --- for robust dose beamlets (unchanged) ---
        if robust:
            for s in range(len(self.plan.planDesign.robustness.scenarios)):
                if use_MKL == 1:
                    beamletMatrix = sparse_dot_mkl.dot_product_mkl(
                        sp.diags(roiRobustObjectives.astype(np.float32), format='csc'),
                        self.plan.planDesign.robustness.scenarios[s].toSparseMatrix())
                else:
                    beamletMatrix = sp.csc_matrix.dot(
                        sp.diags(roiRobustObjectives.astype(np.float32), format='csc'),
                        self.plan.planDesign.robustness.scenarios[s].toSparseMatrix())
                self.plan.planDesign.robustness.scenarios[s].setUnitaryBeamlets(beamletMatrix)

        objectiveFunction = DoseFidelity(
            self.plan,
            self.xSquared,
            self.GPU_acceleration,
            useLET=useLET  # <--- pass switch to fidelity
        )
        self.functions.append(objectiveFunction)

    def computeDose(self):
        assert hasattr(self.plan, 'planDesign')
        assert hasattr(self.plan.planDesign.beamlets, '_sparseBeamlets')
        assert self.plan.planDesign.beamlets._sparseBeamlets is not None

        beamlets = self.plan.planDesign.beamlets
        weights = np.array(self.plan.spotMUs, dtype=np.float32)
        if use_MKL == 1:
            totalDose = sparse_dot_mkl.dot_product_mkl(beamlets._sparseBeamlets, weights) * self.plan.numberOfFractionsPlanned
        else:
            totalDose = csc_matrix.dot(beamlets._sparseBeamlets, weights) * self.plan.numberOfFractionsPlanned

        totalDose = np.reshape(totalDose, beamlets._gridSize, order='F')
        totalDose = np.flip(totalDose, 0)
        totalDose = np.flip(totalDose, 1)

        doseImage = DoseImage(imageArray=totalDose, origin=beamlets._origin, spacing=beamlets._spacing,
                              angles=beamlets._orientation)

        return doseImage

    def optimize(self):
        """
        Optimize the plan.

        Returns
        -------
        numpy.ndarray
            The optimized weights.
        numpy.ndarray
            The total dose.
        float
            The cost.
        """
        logger.info('Prepare optimization ...')
        if self.GPU_acceleration:
            logger.info('abnormal used memory: {}'.format(cp.get_default_memory_pool().used_bytes()))
        self.initializeFidObjectiveFunction()
        x0 = self.initializeWeights()

        try:
            bounds = self.opti_params['bounds']
            logger.info('Bounds are given by user')
        except:
            bounds = None

        # Optimization
        result = self.solver.solve(self.functions, x0, bounds=bounds)

        if self.GPU_acceleration:
            self.functions[0].unload_blGPU()
            cp._default_memory_pool.free_all_blocks()

        return self.postProcess(result)

    def postProcess(self, result):
        """
        Post-process the optimization result. !! The spots and the according weight bellow the thresholdSpotRemoval are removed from the plan and beamlet matrix !!
        The optimized weights are saved in self.plan.spotMUs
        """
        # Remove unnecessary attributs in plan
        try:
            del self.plan._spots
            del self.plan._layers
        except:
            pass

        weights = result['sol']
        crit = result['crit']
        self.niter = result['niter']
        self.time = result['time']
        self.cost = result['objective']

        if self.niter <= 0:
            self.niter = 1

        logger.info(
            ' {} terminated in {} Iter, x = {}, f(x) = {}, time elapsed {}, time per iter {}'
            .format(self.solver.__class__.__name__, self.niter, weights, self.cost, self.time, self.time / self.niter))

        # unload scenario beamlets
        for s in range(len(self.plan.planDesign.robustness.scenarios)):
            self.plan.planDesign.robustness.scenarios[s].unload()

        # total dose
        logger.info("Total dose calculation ...")
        if self.xSquared:
            self.plan.spotMUs = np.square(weights).astype(np.float32) / self.plan.numberOfFractionsPlanned
        else:
            self.plan.spotMUs = weights.astype(np.float32) / self.plan.numberOfFractionsPlanned

        MU_before_simplify = self.plan.spotMUs.copy()
        self.plan.simplify(threshold=self.thresholdSpotRemoval)  # remove spots below self.thresholdSpotRemoval
        if self.plan.planDesign.beamlets.shape[1] != len(self.plan.spotMUs):
            # Beamlet matrix has not removed zero weight column
            ind_to_keep = MU_before_simplify > self.thresholdSpotRemoval
            assert np.sum(ind_to_keep) == len(self.plan.spotMUs)
            self.plan.planDesign.beamlets.setUnitaryBeamlets(self.plan.planDesign.beamlets._sparseBeamlets[:, ind_to_keep])

        totalDose = self.computeDose()
        logger.info('Optimization done.')

        return totalDose, self.cost

    def getConvergenceData(self, method):
        dct = {}
        if 'Scipy' in method:
            dct['func_0'] = self.cost[:-1]
        elif method == 'LP':
            raise NotImplementedError('No convergence data is available for LP')
        else:
            nFunctions = len(self.cost[0])
            for i in range(nFunctions):
                dct['func_%s' % i] = [itm[i] for itm in self.cost[:-1]]
        dct['time'] = self.time
        dct['nIter'] = self.niter
        return dct


class IMPTPlanOptimizer(PlanOptimizer):
    """
    IMPT optimizer; see base class for details.
    """
    def __init__(self, method, plan:RTPlan, **kwargs):
        super().__init__(plan, **kwargs)
        self.method = method
        if "Scipy" in self.method:
            algo = self.method.split('_')[1]
            self.solver = scipyOpt.ScipyOpt(algo, **kwargs)
        elif self.method == 'Gradient':
            self.solver = gradientDescent.GradientDescent(**kwargs)
        elif self.method == 'BFGS':
            self.solver = bfgs.BFGS(**kwargs)
        elif self.method == "LBFGS":
            self.solver = bfgs.LBFGS(**kwargs)
        elif self.method == "FISTA":
            self.solver = fista.FISTA(**kwargs)
        elif self.method == "LP":
            from opentps.core.processing.planOptimization.solvers import lp
            self.xSquared = False
            self.solver = lp.LP(self.plan, **kwargs)
        else:
            logger.error(
                'Method {} is not implemented. Pick among ["Scipy-BFGS", "Scipy-LBFGS", "Scipy-SLSQP", "Scipy-COBYLA", "Scipy-trust-constr", "Gradient", "BFGS", "LBFGS", "FISTA", "LP]'.format(
                    self.method))

    def getConvergenceData(self):
        return super().getConvergenceData(self.method)


class BoundConstraintsOptimizer(PlanOptimizer):
    """
    Optimizer with bound constraints.
    """
    def __init__(self, plan: RTPlan, method='Scipy_L-BFGS-B', bounds=(0.02, 250), **kwargs):
        super().__init__(plan, **kwargs)
        self.bounds = bounds
        if method == 'Scipy_L-BFGS-B':
            self.method = method
            self.solver = scipyOpt.ScipyOpt('L-BFGS-B', **kwargs)
        else:
            raise NotImplementedError(f'Method {method} does not accept bound constraints')

    @property
    def xSquared(self):
        return False

    def formatBoundsForSolver(self, bounds=None):
        if bounds is None:
            bounds = self.bounds
        bound_min = bounds[0] * self.plan.numberOfFractionsPlanned
        bound_max = bounds[1] * self.plan.numberOfFractionsPlanned
        return [(bound_min, bound_max)] * self.plan.planDesign.beamlets.shape[1]

    def optimize(self, nIterations=None):
        self.initializeFidObjectiveFunction()
        x0 = self.initializeWeights()

        if self.bounds[0] == 0:
            result = self.solver.solve(self.functions, x0, bounds=self.formatBoundsForSolver(self.bounds), maxit=self.opti_params.get('maxiter', 1000))
        elif self.bounds[0] < 0:
            raise ValueError("Bounds cannot be negative")
        else:
            if nIterations is not None:
                nit1, nit2 = nIterations[0], nIterations[1]
            else:
                nit1 = self.opti_params.get('maxiter', 1000) // 2
                nit2 = self.opti_params.get('maxiter', 1000) // 2

            # First Optimization with lower bound = 0
            self.solver.params['maxiter'] = nit1
            result = self.solver.solve(self.functions, x0, bounds=self.formatBoundsForSolver((0, self.bounds[1])))
            x0 = np.array(result['sol'])
            ind_to_keep = np.full(x0.shape, False)
            ind_to_keep[x0 >= self.bounds[0]] = True
            x0 = x0[ind_to_keep]

            self.functions = []  # to avoid a beamlet copy with different size
            self.plan.planDesign.beamlets.setUnitaryBeamlets(self.plan.planDesign.beamlets._sparseBeamlets[:, ind_to_keep])
            objectiveFunction = DoseFidelity(self.plan, self.xSquared)
            self.functions.append(objectiveFunction)

            # second optimization with lower bound = self.bounds[0]
            self.solver.params['maxiter'] = nit2
            result = self.solver.solve(self.functions, x0, bounds=self.formatBoundsForSolver(self.bounds))
            result_weights = np.zeros(ind_to_keep.shape, dtype=np.float32)  # reintroduce filtered spots at zero MU
            result_weights[ind_to_keep] = result['sol']
            result['sol'] = result_weights

            self.thresholdSpotRemoval = 1e-6  # zero spot MUs are removed in the postProcess with plan.simplify(self.thresholdSpotRemoval)

        return self.postProcess(result)

    def getConvergenceData(self):
        return super().getConvergenceData(self.method)


class ARCPTPlanOptimizer(PlanOptimizer):
    """
    ARCPT optimizer.
    """
    def __init__(self, method, plan, **kwargs):
        super(ARCPTPlanOptimizer, self).__init__(plan, **kwargs)
        if method == 'FISTA':
            self.solver = fista.FISTA()
        elif method == 'LS':
            self.solver = localSearch.LS()
        elif method == 'MIP':
            from opentps.core.processing.planOptimization.solvers import mip
            self.xSquared = False
            self.solver = mip.MIP(self.plan, **kwargs)
        else:
            logger.error(
                'Method {} is not implemented. Pick among ["FISTA","LS","MIP","SPArcling"]'.format(self.method))
