import numpy as np
import matplotlib.pyplot as plt
import logging

from opentps.core.data.images import CTImage
from opentps.core.data.images import ROIMask
from opentps.core.processing.imageProcessing.syntheticDeformation import applyBaselineShift
from opentps.core.data.dynamicData._dynamic3DModel import Dynamic3DModel
from opentps.core.data.dynamicData._dynamic3DSequence import Dynamic3DSequence
from opentps.core.examples.syntheticData import *

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # GENERATE SYNTHETIC 4DCT
    CT4D = createSynthetic4DCT()

    # GENERATE MASK
    mask = np.full(CT4D.dyn3DImageList[0].gridSize, 0)
    mask[38:52, 87:103, 39:54] = 1
    roi = ROIMask(imageArray=mask, origin=[0, 0, 0], spacing=[1, 1, 1.5])

    # GENERATE MIDP
    Model = Dynamic3DModel()
    Model.computeMidPositionImage(CT4D, 0, tryGPU=True)

    # plt.figure()
    # plt.imshow(Model.midp.imageArray[:, 95, :])
    # plt.imshow(roi.imageArray[:, 95, :], alpha=0.5, cmap='Reds')
    # plt.show()

    # APPLY BASELINE SHIFT
    ModelShifted, maskShifted = applyBaselineShift(Model, roi, [5, 0, 10])

    # REGENERATE 4D SEQUENCES FROM MODELS
    CT4DRegen = Dynamic3DSequence()
    for i in range(len(CT4D.dyn3DImageList)):
        CT4DRegen.dyn3DImageList.append(Model.generate3DImage(i / len(CT4D.dyn3DImageList), amplitude=1))
    CT4DShifted = Dynamic3DSequence()
    for i in range(len(CT4D.dyn3DImageList)):
        CT4DShifted.dyn3DImageList.append(ModelShifted.generate3DImage(i/len(CT4D.dyn3DImageList), amplitude=1))

    # DISPLAY RESULTS
    fig, ax = plt.subplots(3, 7)
    fig.tight_layout()
    y_slice = 95
    ax[1, 0].imshow(Model.midp.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1, 0].title.set_text('MidP')
    ax[2, 0].imshow(ModelShifted.midp.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[2, 0].title.set_text('MidP shifted')

    average = CT4D.dyn3DImageList[0].copy()
    for i in range(len(CT4D.dyn3DImageList)-1):
        average._imageArray += CT4D.dyn3DImageList[i+1]._imageArray
    average._imageArray = average.imageArray/len(CT4D.dyn3DImageList)
    averageRegen = CT4DRegen.dyn3DImageList[0].copy()
    for i in range(len(CT4DRegen.dyn3DImageList) - 1):
        averageRegen._imageArray += CT4DRegen.dyn3DImageList[i + 1]._imageArray
    averageRegen._imageArray = averageRegen.imageArray / len(CT4DRegen.dyn3DImageList)
    averageShifted = CT4DShifted.dyn3DImageList[0].copy()
    for i in range(len(CT4DShifted.dyn3DImageList) - 1):
        averageShifted._imageArray += CT4DShifted.dyn3DImageList[i + 1]._imageArray
    averageShifted._imageArray = averageShifted.imageArray / len(CT4DShifted.dyn3DImageList)

    ax[0, 1].imshow(average.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0, 1].title.set_text('Average')
    ax[1, 1].imshow(averageRegen.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1, 1].title.set_text('Gen average')
    ax[2, 1].imshow(averageShifted.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[2, 1].title.set_text('Gen average shifted')

    averageRegen._imageArray -= average._imageArray
    averageShifted._imageArray -= average._imageArray
    average._imageArray -= average._imageArray
    ax[0, 0].imshow(average.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0, 0].title.set_text('-')
    ax[0, 2].imshow(average.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0, 2].title.set_text('-')
    ax[1, 2].imshow(averageRegen.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1, 2].title.set_text('Gen average diff')
    ax[2, 2].imshow(averageShifted.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[2, 2].title.set_text('Gen average shifted diff')

    ax[0, 3].imshow(CT4D.dyn3DImageList[0].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0, 3].title.set_text('Phase 0')
    ax[1, 3].imshow(CT4DRegen.dyn3DImageList[0].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1, 3].title.set_text('Gen phase 0')
    ax[2, 3].imshow(CT4DShifted.dyn3DImageList[0].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[2, 3].title.set_text('Gen phase 0 shifted')

    ax[0, 4].imshow(CT4D.dyn3DImageList[1].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0, 4].title.set_text('Phase 1')
    ax[1, 4].imshow(CT4DRegen.dyn3DImageList[1].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1, 4].title.set_text('Gen phase 1')
    ax[2, 4].imshow(CT4DShifted.dyn3DImageList[1].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[2, 4].title.set_text('Gen phase 1 shifted')

    ax[0, 5].imshow(CT4D.dyn3DImageList[2].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0, 5].title.set_text('Phase 2')
    ax[1, 5].imshow(CT4DRegen.dyn3DImageList[2].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1, 5].title.set_text('Gen phase 2')
    ax[2, 5].imshow(CT4DShifted.dyn3DImageList[2].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[2, 5].title.set_text('Gen phase 2 shifted')

    ax[0, 6].imshow(CT4D.dyn3DImageList[3].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0, 6].title.set_text('Phase 3')
    ax[1, 6].imshow(CT4DRegen.dyn3DImageList[3].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1, 6].title.set_text('Gen phase 3')
    ax[2, 6].imshow(CT4DShifted.dyn3DImageList[3].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[2, 6].title.set_text('Gen phase 3 shifted')

    plt.show()

    print('done')
