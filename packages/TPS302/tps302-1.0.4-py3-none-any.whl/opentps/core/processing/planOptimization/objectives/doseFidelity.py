import numpy as np
import scipy.sparse as sp
from copy import copy
import logging
logger = logging.getLogger(__name__)

try:
    import sparse_dot_mkl
    use_MKL = 0
except:
    use_MKL = 0

cupy_available = False
try:
    import cupy as cp
    import cupyx as cpx
    cupy_available = True
except:
    cupy_available = False

from opentps.core.processing.planOptimization.objectives.baseFunction import BaseFunc
from opentps.core.data._dvh import DVH


class DoseFidelity(BaseFunc):
    """
    Dose fidelity objective class with optional LET terms (non-robust only).

    Parameters
    ----------
    plan : RTPlan
    xSquare : bool
    GPU_acceleration : bool
    useLET : bool, default False
        Switch to enable LET objectives. Requires plan.planDesign.beamletsLET (same shape as dose beamlets).
    """
    def __init__(self, plan, xSquare=True, GPU_acceleration=False, useLET=False):
        super(DoseFidelity, self).__init__()
        self.list = plan.planDesign.objectives.fidObjList
        self.xSquare = xSquare
        self.beamlets = plan.planDesign.beamlets.toSparseMatrix()
        self.GPU_acceleration = GPU_acceleration
        self.useLET = bool(useLET)

        # LET beamlets (nominal only)
        self.let_beamlets = None
        if self.useLET and hasattr(plan.planDesign, 'beamletsLET') and plan.planDesign.beamletsLET is not None:
            if hasattr(plan.planDesign.beamletsLET, 'toSparseMatrix'):
                self.let_beamlets = plan.planDesign.beamletsLET.toSparseMatrix()
            else:
                # assume already a scipy.sparse matrix
                self.let_beamlets = plan.planDesign.beamletsLET

        if GPU_acceleration:
            if cupy_available:
                logger.info('cupy imported and will be used in dosefidelity with version : {}'.format(cp.__version__))
                self.beamlets_gpu = cpx.scipy.sparse.csc_matrix(self.beamlets.astype(np.float32))
                if self.useLET and self.let_beamlets is not None:
                    self.let_beamlets_gpu = cpx.scipy.sparse.csc_matrix(self.let_beamlets.astype(np.float32))
                else:
                    self.let_beamlets_gpu = None
            else:
                self.GPU_acceleration = False

        if plan.planDesign.robustness.scenarios:
            self.scenariosBL = [plan.planDesign.robustness.scenarios[s].toSparseMatrix() for s in
                                range(len(plan.planDesign.robustness.scenarios))]
        else:
            self.scenariosBL = []

        self.savedWorstCase = (None, None)

    def unload_blGPU(self):
        if hasattr(self, 'beamlets_gpu'):
            del self.beamlets_gpu
        if hasattr(self, 'let_beamlets_gpu'):
            del self.let_beamlets_gpu
        if cupy_available:
            cp._default_memory_pool.free_all_blocks()

    # ---------- helpers for LET ----------
    def _has_any_let_objective(self):
        try:
            from opentps.core.data.plan._objectivesList import FidObjective
            LETM = FidObjective.Metrics
        except Exception:
            return False
        for obj in self.list:
            if obj.metric in (LETM.LETMIN, LETM.LETMAX, LETM.LETMEAN):
                return True
        return False

    def _compute_total(self, matrix, weights, on_gpu=False):
        if on_gpu:
            return cp.sparse.csc_matrix.dot(matrix, weights)
        elif use_MKL == 1:
            return sparse_dot_mkl.dot_product_mkl(matrix, weights)
        else:
            return sp.csc_matrix.dot(matrix, weights)

    # ------------------------------------

    def computeFidelityFunction(self, x, returnWorstCase=False):
        """
        Computes the fidelity function (dose + optional LET). LET is evaluated only on nominal.
        """
        if self.xSquare:
            weights = (cp.asarray(np.square(x).astype(np.float32)) if self.GPU_acceleration
                       else np.square(x).astype(np.float32))
        else:
            weights = (cp.asarray(x.astype(np.float32)) if self.GPU_acceleration
                       else x.astype(np.float32))

        fTot = 0.0
        fTotScenario = 0.0
        scenarioList = []

        # ---- nominal dose ----
        if self.GPU_acceleration:
            doseTotal = cp.sparse.csc_matrix.dot(self.beamlets_gpu, weights)
        elif use_MKL == 1:
            doseTotal = sparse_dot_mkl.dot_product_mkl(self.beamlets, weights)
        else:
            doseTotal = sp.csc_matrix.dot(self.beamlets, weights)

        # ---- nominal LET (only if requested & provided) ----
        letTotal = None
        doLET = self.useLET and self._has_any_let_objective() and (self.let_beamlets is not None)
        if doLET:
            if self.GPU_acceleration and hasattr(self, 'let_beamlets_gpu') and self.let_beamlets_gpu is not None:
                letTotal = cp.sparse.csc_matrix.dot(self.let_beamlets_gpu, weights)
            else:
                letTotal = sp.csc_matrix.dot(self.let_beamlets, weights)

        # Evaluate objectives (nominal)
        for objective in self.list:
            # ---- dose-based metrics ----
            if objective.metric == objective.Metrics.DMAX:
                f = np.mean(np.maximum(0, (doseTotal[objective.maskVec].get() if self.GPU_acceleration else doseTotal[objective.maskVec]) - objective.limitValue) ** 2)
            elif objective.metric == objective.Metrics.DMEAN:
                if self.GPU_acceleration:
                    f = np.maximum(0, np.mean(doseTotal[objective.maskVec].get(), dtype=np.float32) - objective.limitValue) ** 2
                else:
                    f = np.maximum(0, np.mean(doseTotal[objective.maskVec], dtype=np.float32) - objective.limitValue) ** 2
            elif objective.metric == objective.Metrics.DMIN:
                f = np.mean(np.minimum(0, (doseTotal[objective.maskVec].get() if self.GPU_acceleration else doseTotal[objective.maskVec]) - objective.limitValue) ** 2)
            elif objective.metric == objective.Metrics.DUNIFORM:
                if self.GPU_acceleration:
                    f = np.mean((doseTotal[objective.maskVec].get() - objective.limitValue) ** 2)
                else:
                    f = np.mean((doseTotal[objective.maskVec] - objective.limitValue) ** 2)
            elif objective.metric == objective.Metrics.DFALLOFF:
                if self.GPU_acceleration:
                    f = np.mean(np.maximum(0, doseTotal[objective.maskVec].get() - objective.voxelwiseLimitValue) ** 2)
                else:
                    f = np.mean(np.maximum(0, doseTotal[objective.maskVec] - objective.voxelwiseLimitValue) ** 2)
            elif objective.metric == objective.Metrics.DVHMIN:
                if self.GPU_acceleration:
                    deviation = doseTotal[objective.maskVec].get() - objective.limitValue
                    DAV = self._calcInverseDVH(objective.volume, doseTotal[objective.maskVec]).get()
                    deviation[(doseTotal[objective.maskVec].get() > objective.limitValue) | (doseTotal[objective.maskVec].get() < DAV)] = 0
                    f = np.mean(deviation**2)
                else:
                    deviation = doseTotal[objective.maskVec] - objective.limitValue
                    DAV = self._calcInverseDVH(objective.volume, doseTotal[objective.maskVec])
                    deviation[(doseTotal[objective.maskVec] > objective.limitValue) | (doseTotal[objective.maskVec] < DAV)] = 0
                    f = np.mean(deviation**2)
            elif objective.metric == objective.Metrics.DVHMAX:
                if self.GPU_acceleration:
                    deviation = doseTotal[objective.maskVec].get() - objective.limitValue
                    DAV = self._calcInverseDVH(objective.volume, doseTotal[objective.maskVec]).get()
                    deviation[(doseTotal[objective.maskVec].get() < objective.limitValue) | (doseTotal[objective.maskVec].get() > DAV)] = 0
                    f = np.mean(deviation**2)
                else:
                    deviation = doseTotal[objective.maskVec] - objective.limitValue
                    DAV = self._calcInverseDVH(objective.volume, doseTotal[objective.maskVec])
                    deviation[(doseTotal[objective.maskVec] < objective.limitValue) | (doseTotal[objective.maskVec] > DAV)] = 0
                    f = np.mean(deviation**2)
            elif objective.metric == objective.Metrics.EUDMAX:
                if self.GPU_acceleration:
                    DVH_a = np.mean(doseTotal[objective.maskVec].get() ** objective.EUDa) ** (1/objective.EUDa)
                else:
                    DVH_a = np.mean(doseTotal[objective.maskVec] ** objective.EUDa) ** (1/objective.EUDa)
                f = max(0, DVH_a - objective.limitValue) ** 2
            elif objective.metric == objective.Metrics.EUDMIN:
                if self.GPU_acceleration:
                    DVH_a = np.mean(doseTotal[objective.maskVec].get() ** objective.EUDa) ** (1/objective.EUDa)
                else:
                    DVH_a = np.mean(doseTotal[objective.maskVec] ** objective.EUDa) ** (1/objective.EUDa)
                f = min(0, DVH_a - objective.limitValue) ** 2
            elif objective.metric == objective.Metrics.EUDUNIFORM:
                if self.GPU_acceleration:
                    DVH_a = np.mean(doseTotal[objective.maskVec].get() ** objective.EUDa) ** (1/objective.EUDa)
                else:
                    DVH_a = np.mean(doseTotal[objective.maskVec] ** objective.EUDa) ** (1/objective.EUDa)
                f = (DVH_a - objective.limitValue) ** 2

            # ---- LET-based metrics (nominal only, no robust) ----
            elif doLET and objective.metric == objective.Metrics.LETMAX:
                vec = letTotal[objective.maskVec]
                vec = vec.get() if self.GPU_acceleration and hasattr(vec, 'get') else vec
                f = np.mean(np.maximum(0, vec - objective.limitValue) ** 2)
                f = float(f)
            elif doLET and objective.metric == objective.Metrics.LETMIN:
                vec = letTotal[objective.maskVec]
                vec = vec.get() if self.GPU_acceleration and hasattr(vec, 'get') else vec
                f = np.mean(np.minimum(0, vec - objective.limitValue) ** 2)
                f = float(f)
            elif doLET and objective.metric == objective.Metrics.LETMEAN:
                vec = letTotal[objective.maskVec]
                vec = vec.get() if self.GPU_acceleration and hasattr(vec, 'get') else vec
                f = np.maximum(0, np.mean(vec, dtype=np.float32) - objective.limitValue) ** 2
                f = float(f)

            else:
                raise Exception(str(objective.metric) + ' is not supported as an objective metric')

            if not objective.robust:
                fTot += objective.weight * f
            else:
                fTotScenario += objective.weight * f

        # prevent OOM
        if self.GPU_acceleration:
            del weights, doseTotal
            if doLET:
                del letTotal
            cp._default_memory_pool.free_all_blocks()

        scenarioList.append(fTotScenario)

        # robust scenarios only for dose (unchanged)
        robust = any([obj.robust for obj in self.list])
        if self.scenariosBL == [] or not robust:
            if not returnWorstCase:
                return fTot
            else:
                return fTot, -1

        for ScenarioBL in self.scenariosBL:
            fTotScenario = 0.0
            if use_MKL == 1:
                doseTotal = sparse_dot_mkl.dot_product_mkl(ScenarioBL, weights)
            else:
                doseTotal = sp.csc_matrix.dot(ScenarioBL, weights)

            for objective in self.list:
                if not objective.robust:
                    continue
                if objective.metric == objective.Metrics.DMAX:
                    f = np.mean(np.maximum(0, doseTotal[objective.maskVec] - objective.limitValue) ** 2)
                elif objective.metric == objective.Metrics.DMEAN:
                    f = np.maximum(0, np.mean(doseTotal[objective.maskVec], dtype=np.float32) - objective.limitValue) ** 2
                elif objective.metric == objective.Metrics.DMIN:
                    f = np.mean(np.minimum(0, doseTotal[objective.maskVec] - objective.limitValue) ** 2)
                elif objective.metric == objective.Metrics.DUNIFORM:
                    f = np.mean((doseTotal[objective.maskVec] - objective.limitValue) ** 2)
                elif objective.metric == objective.Metrics.DFALLOFF:
                    f = np.mean(np.maximum(0, doseTotal[objective.maskVec] - objective.voxelwiseLimitValue) ** 2)
                elif objective.metric == objective.Metrics.DVHMIN:
                    deviation = doseTotal[objective.maskVec] - objective.limitValue
                    DAV = self._calcInverseDVH(objective.volume, doseTotal[objective.maskVec])
                    deviation[(doseTotal[objective.maskVec] > objective.limitValue) | (doseTotal[objective.maskVec] < DAV)] = 0
                    f = np.mean(deviation**2)
                elif objective.metric == objective.Metrics.DVHMAX:
                    deviation = doseTotal[objective.maskVec] - objective.limitValue
                    DAV = self._calcInverseDVH(objective.volume, doseTotal[objective.maskVec])
                    deviation[(doseTotal[objective.maskVec] < objective.limitValue) | (doseTotal[objective.maskVec] > DAV)] = 0
                    f = np.mean(deviation**2)
                elif objective.metric == objective.Metrics.EUDMAX:
                    DVH_a = np.mean(doseTotal[objective.maskVec] ** objective.EUDa) ** (1/objective.EUDa)
                    f = max(0, DVH_a - objective.limitValue) ** 2
                elif objective.metric == objective.Metrics.EUDMIN:
                    DVH_a = np.mean(doseTotal[objective.maskVec] ** objective.EUDa) ** (1/objective.EUDa)
                    f = min(0, DVH_a - objective.limitValue) ** 2
                elif objective.metric == objective.Metrics.EUDUNIFORM:
                    DVH_a = np.mean(doseTotal[objective.maskVec] ** objective.EUDa) ** (1/objective.EUDa)
                    f = (DVH_a - objective.limitValue) ** 2
                else:
                    raise Exception(str(objective.metric) + ' is not supported as an objective metric')

                fTotScenario += objective.weight * f

            scenarioList.append(fTotScenario)

        fTot += max(scenarioList)
        worstCaseIndex = scenarioList.index(max(scenarioList)) - 1
        self.savedWorstCase = (copy(x), worstCaseIndex)

        if not returnWorstCase:
            return fTot
        else:
            return fTot, worstCaseIndex

    def computeFidelityGradient(self, x):
        """
        Computes gradient for dose and optional LET (nominal only for LET).
        """
        # worst case (dose robust only)
        if len(self.scenariosBL) > 0:
            if np.array_equal(x, self.savedWorstCase[0]):
                worstCase = self.savedWorstCase[1]
            else:
                _, worstCase = self.computeFidelityFunction(x, returnWorstCase=True)
        else:
            worstCase = -1

        if self.xSquare:
            weights = (cp.asarray(np.square(x).astype(np.float32)) if self.GPU_acceleration
                       else np.square(x).astype(np.float32))
        else:
            weights = (cp.asarray(x.astype(np.float32)) if self.GPU_acceleration
                       else x.astype(np.float32))

        if self.GPU_acceleration:
            xDiag = cpx.scipy.sparse.diags(x.astype(np.float32), format='csc')
        else:
            xDiag = sp.diags(x.astype(np.float32), format='csc')

        # dose nominal & BL
        if self.GPU_acceleration:
            doseNominal = cp.sparse.csc_matrix.dot(self.beamlets_gpu, weights)
            doseNominalBL = cp.sparse.csc_matrix.dot(self.beamlets_gpu, xDiag) if self.xSquare else self.beamlets_gpu
            if worstCase != -1:
                doseScenario = cp.sparse.csc_matrix.dot(self.scenariosBL[worstCase], weights)
                doseScenarioBL = cp.sparse.csc_matrix.dot(self.scenariosBL[worstCase], xDiag)
            dfTot = np.zeros((1, len(x)), dtype=np.float32)
        elif use_MKL == 1:
            doseNominal = sparse_dot_mkl.dot_product_mkl(self.beamlets, weights)
            doseNominalBL = sparse_dot_mkl.dot_product_mkl(self.beamlets, xDiag) if self.xSquare else self.beamlets
            if worstCase != -1:
                doseScenario = sparse_dot_mkl.dot_product_mkl(self.scenariosBL[worstCase], weights)
                doseScenarioBL = sparse_dot_mkl.dot_product_mkl(self.scenariosBL[worstCase], xDiag)
            dfTot = np.zeros((1, len(x)), dtype=np.float32)
        else:
            doseNominal = sp.csc_matrix.dot(self.beamlets, weights)
            doseNominalBL = sp.csc_matrix.dot(self.beamlets, xDiag) if self.xSquare else self.beamlets
            doseNominalBL = sp.csc_matrix.transpose(doseNominalBL)
            if worstCase != -1:
                doseScenario = sp.csc_matrix.dot(self.scenariosBL[worstCase], weights)
                doseScenarioBL = sp.csc_matrix.dot(self.scenariosBL[worstCase], xDiag)
                doseScenarioBL = sp.csc_matrix.transpose(doseScenarioBL)
            dfTot = np.zeros((len(x), 1), dtype=np.float32)

        # LET nominal & BL (only if enabled)
        doLET = self.useLET and self._has_any_let_objective() and (self.let_beamlets is not None)
        if doLET:
            if self.GPU_acceleration and hasattr(self, 'let_beamlets_gpu') and self.let_beamlets_gpu is not None:
                letNominal = cp.sparse.csc_matrix.dot(self.let_beamlets_gpu, weights)
                letNominalBL = cp.sparse.csc_matrix.dot(self.let_beamlets_gpu, xDiag) if self.xSquare else self.let_beamlets_gpu
            else:
                letNominal = sp.csc_matrix.dot(self.let_beamlets, weights)
                letNominalBL = sp.csc_matrix.dot(self.let_beamlets, xDiag) if self.xSquare else self.let_beamlets
                letNominalBL = sp.csc_matrix.transpose(letNominalBL)

        for objective in self.list:
            # choose dose context (robust or nominal)
            if worstCase != -1 and objective.robust:
                doseTotal = doseScenario
                doseBL = doseScenarioBL
            else:
                doseTotal = doseNominal
                doseBL = doseNominalBL

            # ----- Dose metrics (unchanged) -----
            if objective.metric == objective.Metrics.DMAX:
                if self.GPU_acceleration:
                    maskVec_gpu = cp.asarray(objective.maskVec)
                    limitValue_gpu = cp.asarray(objective.limitValue)
                    f = cp.maximum(0, doseTotal[maskVec_gpu] - limitValue_gpu.astype(cp.float32))
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[maskVec_gpu, :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = np.maximum(0, doseTotal[objective.maskVec] - objective.limitValue).astype(np.float32)
                    f = sp.diags(f, format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = np.maximum(0, doseTotal[objective.maskVec] - objective.limitValue)
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.DMEAN:
                if self.GPU_acceleration:
                    maskVec_gpu = cp.asarray(objective.maskVec)
                    f = cp.maximum(0, cp.mean(doseTotal[maskVec_gpu], dtype=cp.float32) - cp.asarray(objective.limitValue, dtype=cp.float32))
                    df = cpx.scipy.sparse.csr_matrix.multiply(doseBL[maskVec_gpu, :], float(f))
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = np.maximum(0, np.mean(doseTotal[objective.maskVec], dtype=np.float32) - objective.limitValue)
                    df = sp.csr_matrix.multiply(doseBL[objective.maskVec, :], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = np.maximum(0, np.mean(doseTotal[objective.maskVec], dtype=np.float32) - objective.limitValue)
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.DMIN:
                if self.GPU_acceleration:
                    maskVec_gpu = cp.asarray(objective.maskVec)
                    f = cp.minimum(0, doseTotal[maskVec_gpu] - cp.asarray(objective.limitValue, dtype=cp.float32))
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[maskVec_gpu, :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = np.minimum(0, doseTotal[objective.maskVec] - objective.limitValue).astype(np.float32)
                    f = sp.diags(f, format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = np.minimum(0, doseTotal[objective.maskVec] - objective.limitValue)
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.DUNIFORM:
                if self.GPU_acceleration:
                    maskVec_gpu = cp.asarray(objective.maskVec)
                    f = doseTotal[maskVec_gpu] - cp.asarray(objective.limitValue, dtype=cp.float32)
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[maskVec_gpu, :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = (doseTotal[objective.maskVec] - objective.limitValue).astype(np.float32)
                    f = sp.diags(f, format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = doseTotal[objective.maskVec] - objective.limitValue
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.DFALLOFF:
                if self.GPU_acceleration:
                    maskVec_gpu = cp.asarray(objective.maskVec)
                    limitValue_gpu = cp.asarray(objective.voxelwiseLimitValue).astype(cp.float32)
                    f = cp.maximum(0, doseTotal[maskVec_gpu] - limitValue_gpu)
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[maskVec_gpu, :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = np.maximum(0, doseTotal[objective.maskVec] - objective.voxelwiseLimitValue).astype(np.float32)
                    f = sp.diags(f, format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = np.maximum(0, doseTotal[objective.maskVec] - objective.voxelwiseLimitValue)
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.DVHMIN:
                d_ref = self._calcInverseDVH(objective.volume, doseTotal[objective.maskVec])
                if self.GPU_acceleration:
                    maskVec_gpu = cp.asarray(objective.maskVec)
                    f = cp.minimum(0, doseTotal[maskVec_gpu] - cp.asarray(objective.limitValue, dtype=cp.float32))
                    f[doseTotal[maskVec_gpu] < d_ref] = 0
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[maskVec_gpu, :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = np.minimum(0, doseTotal[objective.maskVec] - objective.limitValue).astype(np.float32)
                    f[doseTotal[objective.maskVec] < d_ref] = 0
                    f = sp.diags(f, format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = np.minimum(0, doseTotal[objective.maskVec] - objective.limitValue)
                    f[doseTotal[objective.maskVec] < d_ref] = 0
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.DVHMAX:
                d_ref = self._calcInverseDVH(objective.volume, doseTotal[objective.maskVec])
                if self.GPU_acceleration:
                    maskVec_gpu = cp.asarray(objective.maskVec)
                    f = cp.maximum(0, doseTotal[maskVec_gpu] - cp.asarray(objective.limitValue, dtype=cp.float32))
                    f[doseTotal[maskVec_gpu] > d_ref] = 0
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[maskVec_gpu, :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = np.maximum(0, doseTotal[objective.maskVec] - objective.limitValue).astype(np.float32)
                    f[doseTotal[objective.maskVec] > d_ref] = 0
                    f = sp.diags(f, format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = np.maximum(0, doseTotal[objective.maskVec] - objective.limitValue)
                    f[doseTotal[objective.maskVec] > d_ref] = 0
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.EUDMAX:
                power_dose = doseTotal[objective.maskVec] ** objective.EUDa
                EUD_a = (np.mean(power_dose.get()) if self.GPU_acceleration else np.mean(power_dose)) ** (1/objective.EUDa)
                if self.GPU_acceleration:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (cp.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        doseTotal[objective.maskVec] ** (objective.EUDa - 1) * \
                        max(0, EUD_a - objective.limitValue)
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[cp.asarray(objective.maskVec), :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (np.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        (doseTotal[objective.maskVec] ** (objective.EUDa - 1)) * \
                        max(0, EUD_a - objective.limitValue)
                    f = sp.diags(f.astype(np.float32), format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (np.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        (doseTotal[objective.maskVec] ** (objective.EUDa - 1)) * \
                        max(0, EUD_a - objective.limitValue)
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.EUDMIN:
                power_dose = doseTotal[objective.maskVec] ** objective.EUDa
                EUD_a = (np.mean(power_dose.get()) if self.GPU_acceleration else np.mean(power_dose)) ** (1/objective.EUDa)
                if self.GPU_acceleration:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (cp.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        doseTotal[objective.maskVec] ** (objective.EUDa - 1) * \
                        min(0, EUD_a - objective.limitValue)
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[cp.asarray(objective.maskVec), :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (np.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        (doseTotal[objective.maskVec] ** (objective.EUDa - 1)) * \
                        min(0, EUD_a - objective.limitValue)
                    f = sp.diags(f.astype(np.float32), format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (np.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        (doseTotal[objective.maskVec] ** (objective.EUDa - 1)) * \
                        min(0, EUD_a - objective.limitValue)
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            elif objective.metric == objective.Metrics.EUDUNIFORM:
                power_dose = doseTotal[objective.maskVec] ** objective.EUDa
                EUD_a = (np.mean(power_dose.get()) if self.GPU_acceleration else np.mean(power_dose)) ** (1/objective.EUDa)
                if self.GPU_acceleration:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (cp.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        doseTotal[objective.maskVec] ** (objective.EUDa - 1) * \
                        (EUD_a - objective.limitValue)
                    f_diag = cpx.scipy.sparse.diags(f, format='csc')
                    df = cp.sparse.csc_matrix.dot(f_diag, doseBL[cp.asarray(objective.maskVec), :])
                    dfTot += objective.weight * (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                elif use_MKL == 1:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (np.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        (doseTotal[objective.maskVec] ** (objective.EUDa - 1)) * \
                        (EUD_a - objective.limitValue)
                    f = sp.diags(f.astype(np.float32), format='csc')
                    df = sparse_dot_mkl.dot_product_mkl(f, doseBL[objective.maskVec, :])
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=0)
                else:
                    f = (1 / len(objective.maskVec)) ** ((1 - objective.EUDa)/ objective.EUDa) * \
                        (np.sum(power_dose)) ** ((1 - objective.EUDa) / objective.EUDa) * \
                        (doseTotal[objective.maskVec] ** (objective.EUDa - 1)) * \
                        (EUD_a - objective.limitValue)
                    df = sp.csr_matrix.multiply(doseBL[:, objective.maskVec], f)
                    dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            # ----- LET metrics (nominal only, no robust) -----
            elif doLET and objective.metric in (objective.Metrics.LETMAX, objective.Metrics.LETMIN, objective.Metrics.LETMEAN):
                # choose LET context (always nominal)
                if self.GPU_acceleration and hasattr(self, 'let_beamlets_gpu') and self.let_beamlets_gpu is not None:
                    letTotal = letNominal
                    letBL = letNominalBL
                    mask_idx = cp.asarray(objective.maskVec)
                    if objective.metric == objective.Metrics.LETMAX:
                        f = cp.maximum(0, letTotal[mask_idx] - cp.asarray(objective.limitValue, dtype=cp.float32))
                        f_diag = cpx.scipy.sparse.diags(f, format='csc')
                        df = cp.sparse.csc_matrix.dot(f_diag, letBL[mask_idx, :])
                        df_part = (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                    elif objective.metric == objective.Metrics.LETMIN:
                        f = cp.minimum(0, letTotal[mask_idx] - cp.asarray(objective.limitValue, dtype=cp.float32))
                        f_diag = cpx.scipy.sparse.diags(f, format='csc')
                        df = cp.sparse.csc_matrix.dot(f_diag, letBL[mask_idx, :])
                        df_part = (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                    else:  # LETMEAN
                        f = cp.maximum(0, cp.mean(letTotal[mask_idx], dtype=cp.float32) - cp.asarray(objective.limitValue, dtype=cp.float32))
                        df = cpx.scipy.sparse.csr_matrix.multiply(letBL[mask_idx, :], float(f))
                        df_part = (cpx.scipy.sparse.csr_matrix.mean(df, axis=0)).get()
                    dfTot += objective.weight * df_part
                else:
                    letTotal = letNominal
                    letBL = letNominalBL
                    if objective.metric == objective.Metrics.LETMAX:
                        f = np.maximum(0, letTotal[objective.maskVec] - objective.limitValue)
                        df = sp.csr_matrix.multiply(letBL[:, objective.maskVec], f)
                        dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)
                    elif objective.metric == objective.Metrics.LETMIN:
                        f = np.minimum(0, letTotal[objective.maskVec] - objective.limitValue)
                        df = sp.csr_matrix.multiply(letBL[:, objective.maskVec], f)
                        dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)
                    else:  # LETMEAN
                        f = np.maximum(0, np.mean(letTotal[objective.maskVec], dtype=np.float32) - objective.limitValue)
                        df = sp.csr_matrix.multiply(letBL[:, objective.maskVec], f)
                        dfTot += objective.weight * sp.csr_matrix.mean(df, axis=1)

            else:
                raise Exception(str(objective.metric) + ' is not supported as an objective metric')

        if self.xSquare:
            dfTot = 4 * dfTot
        else:
            dfTot = 2 * dfTot
        dfTot = np.squeeze(np.asarray(dfTot)).astype(np.float64)

        if self.GPU_acceleration:
            try:
                del maskVec_gpu, f, df, doseNominal, weights, xDiag
            except Exception:
                pass
            cp._default_memory_pool.free_all_blocks()

        return dfTot

    def _calcInverseDVH(self, volume, dose):
        if self.GPU_acceleration:
            sorted_dose = cp.sort(dose.flatten())
            volume_cupy = cp.asarray(volume)
            index = cp.rint((1 - volume_cupy) * len(sorted_dose)).astype(np.int32)
        else:
            sorted_dose = np.sort(dose.flatten())
            index = int((1 - volume) * len(sorted_dose))
        return sorted_dose[index]

    def _eval(self, x):
        f = self.computeFidelityFunction(x)
        return f

    def _grad(self, x):
        g = self.computeFidelityGradient(x)
        return g
