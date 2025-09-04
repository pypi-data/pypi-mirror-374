from __future__ import annotations

__all__ = ['ObjectivesList', 'FidObjective']


import copy
import logging
from enum import Enum

import numpy as np
from typing import Optional, Sequence, Union, Iterable
from scipy import ndimage

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from opentps.core.data.images._ctImage import CTImage

from opentps.core.data.images._roiMask import ROIMask
from opentps.core.processing.imageProcessing import resampler3D

logger = logging.getLogger(__name__)

class ObjectivesList:
    """
    This class is used to store the objectives of a plan.
    A plan can have multiple objectives.
    An objective can be a Fidelity Objective or an Exotic Objective.
    """

    def __init__(self):
        self.fidObjList:Sequence[FidObjective] = []
        self.exoticObjList = []
        self.targetName:Union[str,Sequence[str]] = []
        self.targetPrescription:Union[float,Sequence[float]] = []
        self.targetMask:Union[ROIMask,Sequence[ROIMask]] = []

    def setTarget(self, roiName, roiMask, prescription):
        """Set the targets name and prescription doses (primary + secondary)."""
        self.targetName.append(roiName)
        self.targetMask.append(roiMask)
        self.targetPrescription.append(prescription)

    def append(self, objective):
        if isinstance(objective, FidObjective):
            self.fidObjList.append(objective)
        elif isinstance(objective, ExoticObjective):
            self.exoticObjList.append(objective)
        else:
            raise ValueError(objective.__class__.__name__ + ' is not a valid type for objective')

    def addFidObjective(
        self, roi, metric, limitValue=None, weight=1., kind="Soft", robust=False,
        volume=None, EUDa=None, fallOffDistance=None, fallOffLowDoseLevel=None,
        fallOffHighDoseLevel=None
    ):
        objective = FidObjective(roi=roi, metric=metric, limitValue=limitValue, weight=weight)

        if metric == FidObjective.Metrics.DMIN.value or metric == FidObjective.Metrics.DMIN:
            objective.metric = FidObjective.Metrics.DMIN
            if limitValue is None: raise Exception("Error: objective DMIN is missing a parameter.")

        elif metric == FidObjective.Metrics.DMAX.value or metric == FidObjective.Metrics.DMAX:
            objective.metric = FidObjective.Metrics.DMAX
            if limitValue is None: raise Exception("Error: objective DMAX is missing a parameter.")

        elif metric == FidObjective.Metrics.DMEAN.value or metric == FidObjective.Metrics.DMEAN:
            objective.metric = FidObjective.Metrics.DMEAN
            if limitValue is None: raise Exception("Error: objective DMEAN is missing a parameter.")

        elif metric == FidObjective.Metrics.DUNIFORM.value or metric == FidObjective.Metrics.DUNIFORM:
            objective.metric = FidObjective.Metrics.DUNIFORM
            if limitValue is None: raise Exception("Error: objective DUNIFORM is missing a parameter.")

        elif metric == FidObjective.Metrics.EUDMAX.value or metric == FidObjective.Metrics.EUDMAX:
            objective.metric = FidObjective.Metrics.EUDMAX
            if EUDa is None or limitValue is None:
                raise Exception("Error: objective EUDMAX is missing a parameter.")
            elif EUDa == 0:
                raise Exception("Error: parameter of objective EUDMAX must be different than zero.")
            else:
                objective.EUDa = EUDa

        elif metric == FidObjective.Metrics.EUDMIN.value or metric == FidObjective.Metrics.EUDMIN:
            objective.metric = FidObjective.Metrics.EUDMIN
            if EUDa is None or limitValue is None:
                raise Exception("Error: objective EUDMIN is missing a parameter.")
            elif EUDa == 0:
                raise Exception("Error: parameter of objective EUDMIN must be different than zero.")
            else:
                objective.EUDa = EUDa

        elif metric == FidObjective.Metrics.EUDUNIFORM.value or metric == FidObjective.Metrics.EUDUNIFORM:
            objective.metric = FidObjective.Metrics.EUDUNIFORM
            if EUDa is None or limitValue is None:
                raise Exception("Error: objective EUDUNIFORM is missing a parameter.")
            elif EUDa == 0:
                raise Exception("Error: parameter of objective EUDUNIFORM must be different than zero.")
            else:
                objective.EUDa = EUDa

        elif metric == FidObjective.Metrics.DVHMAX.value or metric == FidObjective.Metrics.DVHMAX:
            objective.metric = FidObjective.Metrics.DVHMAX
            if volume is None or limitValue is None:
                raise Exception("Error: objective DVHMAX is missing a volume argument.")
            else:
                objective.volume = volume/100

        elif metric == FidObjective.Metrics.DVHMIN.value or metric == FidObjective.Metrics.DVHMIN:
            objective.metric = FidObjective.Metrics.DVHMIN
            if volume is None or limitValue is None:
                raise Exception("Error: objective DVHMIN is missing a volume argument.")
            else:
                objective.volume = volume/100

        elif metric == FidObjective.Metrics.DFALLOFF.value or metric == FidObjective.Metrics.DFALLOFF:
            objective.metric = FidObjective.Metrics.DFALLOFF
            logger.warning("Dose fall-off objective only supported for primary tumor volume at the moment")
            if (fallOffDistance is None or fallOffHighDoseLevel is None or
                fallOffLowDoseLevel is None or self.targetMask is None):
                raise Exception("Error: objective DFALLOFF is missing required arguments.")
            else:
                objective.fallOffDistance = fallOffDistance*10  # cm->mm
                objective.fallOffHighDoseLevel = fallOffHighDoseLevel
                objective.fallOffLowDoseLevel = fallOffLowDoseLevel

                if self.targetMask:
                    if isinstance(self.targetMask, Iterable):
                        objective.targetMask = copy.deepcopy(self.targetMask[0])
                    else:
                        objective.targetMask = copy.deepcopy(self.targetMask)
                else:
                    raise Exception("Error: Specify targetMask when using DFallOff objective")

        # --- 新增 LET 约束 ---
        elif metric == FidObjective.Metrics.LETMIN.value or metric == FidObjective.Metrics.LETMIN:
            objective.metric = FidObjective.Metrics.LETMIN
            if limitValue is None:
                raise Exception("Error: objective LETMIN is missing a parameter.")

        elif metric == FidObjective.Metrics.LETMAX.value or metric == FidObjective.Metrics.LETMAX:
            objective.metric = FidObjective.Metrics.LETMAX
            if limitValue is None:
                raise Exception("Error: objective LETMAX is missing a parameter.")

        elif metric == FidObjective.Metrics.LETMEAN.value or metric == FidObjective.Metrics.LETMEAN:
            objective.metric = FidObjective.Metrics.LETMEAN
            if limitValue is None:
                raise Exception("Error: objective LETMEAN is missing a parameter.")

        else:
            raise Exception("Error: objective metric " + str(metric) + " is not supported.")

        objective.kind = kind
        objective.robust = robust
        self.fidObjList.append(objective)

    def addExoticObjective(self, weight):
        objective = ExoticObjective()
        objective.weight = weight
        self.exoticObjList.append(objective)


class FidObjective:
    """
    This class is used to store a Fidelity Objective.
    """

    class Metrics(Enum):
        DMIN = 'DMin'
        DMAX = 'DMax'
        DMEAN = 'DMean'
        DUNIFORM = 'DUniform'
        DVHMIN = 'DVHMin'
        DVHMAX = 'DVHMax'
        DFALLOFF = 'DFallOff'
        EUDMIN = 'EUDMin'
        EUDMAX = 'EUDMax'
        EUDUNIFORM = 'EUDUniform'
        # --- 新增 LET 指标 ---
        LETMIN = 'LETMin'
        LETMAX = 'LETMax'
        LETMEAN = 'LETMean'

    def __init__(self, roi=None, metric=None, limitValue=0., weight=1.,
                 fallOffDistance=0., fallOffLowDoseLevel=0, fallOffHighDoseLevel=100):
        self.metric = metric
        self.limitValue = limitValue
        self.weight = weight
        self.fallOffDistance = fallOffDistance
        self.fallOffLowDoseLevel = fallOffLowDoseLevel
        self.fallOffHighDoseLevel = fallOffHighDoseLevel
        self.voxelwiseLimitValue = []
        self.targetMask = []
        self.robust = False
        self.kind = "Soft"
        self.maskVec = None
        self._roi = roi
        self.volume = None
        self.EUDa = None

    @property
    def roi(self):
        return self._roi

    @roi.setter
    def roi(self, roi):
        self._roi = roi

    @property
    def roiName(self) -> str:
        return self.roi.name

    def _updateMaskVec(self, spacing:Sequence[float], gridSize:Sequence[int], origin:Sequence[float]):
        from opentps.core.data._roiContour import ROIContour

        if isinstance(self.roi, ROIContour):
            mask = self.roi.getBinaryMask(origin=origin, gridSize=gridSize, spacing=spacing)
        elif isinstance(self.roi, ROIMask):
            mask = self.roi
            if not (np.array_equal(mask.gridSize, gridSize) and
                np.allclose(mask.origin, origin, atol=0.01) and
                np.allclose(mask.spacing, spacing, atol=0.01)):
                mask = resampler3D.resampleImage3D(self.roi, gridSize=gridSize, spacing=spacing, origin=origin)
        else:
            raise Exception(self.roi.__class__.__name__ + ' is not a supported class for roi')
        
        if self.metric != self.Metrics.DFALLOFF: 
            self.maskVec = np.flip(mask.imageArray, (0, 1))
            self.maskVec = np.ndarray.flatten(self.maskVec, 'F').astype('bool')

        else: 
            targetMask = self.targetMask
            if isinstance(targetMask, ROIContour):
                targetMask = targetMask.getBinaryMask(origin=origin, gridSize=gridSize, spacing=spacing)
            elif isinstance(targetMask, ROIMask):
                if not (np.array_equal(targetMask.gridSize, gridSize) and
                    np.allclose(targetMask.origin, origin, atol=0.01) and
                    np.allclose(targetMask.spacing, spacing, atol=0.01)):
                    targetMask = resampler3D.resampleImage3D(targetMask, gridSize=gridSize, spacing=spacing, origin=origin)
            
            euclidDist = ndimage.distance_transform_edt(targetMask.imageArray==0, sampling=spacing)
            masknan = copy.deepcopy(mask.imageArray)
            masknan[~masknan] = np.nan
            euclidDistROI = euclidDist * masknan

            voxelsIN = np.logical_and(euclidDistROI > 0, euclidDistROI < self.fallOffDistance)
            self.maskVec = np.flip(voxelsIN, (0,1))
            self.maskVec = np.ndarray.flatten(self.maskVec, 'F')

            doseRate = (self.fallOffHighDoseLevel - self.fallOffLowDoseLevel) / self.fallOffDistance
            self.voxelwiseLimitValue = (self.fallOffHighDoseLevel - euclidDistROI * doseRate)
            self.voxelwiseLimitValue = np.flip(self.voxelwiseLimitValue, (0,1))
            self.voxelwiseLimitValue = np.ndarray.flatten(self.voxelwiseLimitValue, 'F')
            self.voxelwiseLimitValue = self.voxelwiseLimitValue[self.maskVec]


class ExoticObjective:
    """This class is used to store an Exotic Objective."""
    def __init__(self):
        self.weight = ""
