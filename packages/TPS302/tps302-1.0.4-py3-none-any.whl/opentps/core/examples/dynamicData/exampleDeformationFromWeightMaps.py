import numpy as np
import matplotlib.pyplot as plt
import logging

from opentps.core.processing.imageProcessing import resampler3D
from opentps.core.data.dynamicData._dynamic3DModel import Dynamic3DModel
from opentps.core.examples.syntheticData import createSynthetic4DCT
from opentps.core.processing.deformableDataAugmentationToolBox.weightMaps import generateDeformationFromTrackers, generateDeformationFromTrackersAndWeightMaps

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    # GENERATE SYNTHETIC 4D INPUT SEQUENCE
    CT4D = createSynthetic4DCT(numberOfPhases=10)

    # CREATE TRACKER POSITIONS
    trackers = [[30, 75, 40],
                [70, 75, 40],
                [100, 75, 40],
                [140, 75, 40]]

    # GENERATE MIDP
    Model4D = Dynamic3DModel()
    Model4D.computeMidPositionImage(CT4D, 0, tryGPU=True)

    # GENERATE ADDITIONAL PHASES
    df1, wm = generateDeformationFromTrackers(Model4D, [0, 0, 2/4, 2/4], [1, 1, 1, 1], trackers)
    im1 = df1.deformImage(Model4D.midp, fillValue='closest')
    df2, wm = generateDeformationFromTrackers(Model4D, [0.5/4, 0.5/4, 1.5/4, 1.5/4], [1, 1, 1, 1], trackers)
    im2 = df2.deformImage(Model4D.midp, fillValue='closest')
    df3 = generateDeformationFromTrackersAndWeightMaps(Model4D, [0, 0, 2/4, 2/4], [2, 2, 2, 2], wm)
    im3 = df3.deformImage(Model4D.midp, fillValue='closest')

    # RESAMPLE WEIGHT MAPS TO IMAGE RESOLUTION
    for i in range(len(trackers)):
        resampler3D.resampleImage3DOnImage3D(wm[i], Model4D.midp, inPlace=True, fillValue=-1024.)

    # DISPLAY RESULTS
    fig, ax = plt.subplots(2, 5)
    ax[0,0].imshow(Model4D.midp.imageArray[:, 50, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    s0 = wm[0].imageArray[:, 50, :].T[::-1, ::1]
    s1 = wm[1].imageArray[:, 50, :].T[::-1, ::1]
    s2 = wm[2].imageArray[:, 50, :].T[::-1, ::1]
    s3 = wm[3].imageArray[:, 50, :].T[::-1, ::1]
    ax[0,1].imshow(s0, cmap='Reds', origin='upper', vmin=0, vmax=1)
    ax[0,2].imshow(s1, cmap='Reds', origin='upper', vmin=0, vmax=1)
    ax[0,3].imshow(s2, cmap='Blues', origin='upper', vmin=0, vmax=1)
    ax[0,4].imshow(s3, cmap='Blues', origin='upper', vmin=0, vmax=1)
    ax[0,0].plot(trackers[0][0],100-trackers[0][2],'ro')
    ax[0,0].plot(trackers[1][0],100-trackers[1][2],'ro')
    ax[0,0].plot(trackers[2][0],100-trackers[2][2],'bo')
    ax[0,0].plot(trackers[3][0],100-trackers[3][2],'bo')
    ax[0,1].plot(trackers[0][0],100-trackers[0][2],'ro')
    ax[0,2].plot(trackers[1][0],100-trackers[1][2],'ro')
    ax[0,3].plot(trackers[2][0],100-trackers[2][2],'bo')
    ax[0,4].plot(trackers[3][0],100-trackers[3][2],'bo')

    ax[1,0].imshow(Model4D.midp.imageArray[:, :, 50].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    s0 = wm[0].imageArray[:, :, 50].T[::-1, ::1]
    s1 = wm[1].imageArray[:, :, 50].T[::-1, ::1]
    s2 = wm[2].imageArray[:, :, 50].T[::-1, ::1]
    s3 = wm[3].imageArray[:, :, 50].T[::-1, ::1]
    ax[1,1].imshow(s0, cmap='Reds', origin='upper', vmin=0, vmax=1)
    ax[1,2].imshow(s1, cmap='Reds', origin='upper', vmin=0, vmax=1)
    ax[1,3].imshow(s2, cmap='Blues', origin='upper', vmin=0, vmax=1)
    ax[1,4].imshow(s3, cmap='Blues', origin='upper', vmin=0, vmax=1)
    ax[1,0].plot(trackers[0][0],trackers[0][1],'ro')
    ax[1,0].plot(trackers[1][0],trackers[1][1],'ro')
    ax[1,0].plot(trackers[2][0],trackers[2][1],'bo')
    ax[1,0].plot(trackers[3][0],trackers[3][1],'bo')
    ax[1,1].plot(trackers[0][0],trackers[0][1],'ro')
    ax[1,2].plot(trackers[1][0],trackers[1][1],'ro')
    ax[1,3].plot(trackers[2][0],trackers[2][1],'bo')
    ax[1,4].plot(trackers[3][0],trackers[3][1],'bo')
    ax[0,0].title.set_text('MidP and trackers')
    ax[0,1].title.set_text('Tracker 1')
    ax[0,2].title.set_text('Tracker 2')
    ax[0,3].title.set_text('Tracker 3')
    ax[0,4].title.set_text('Tracker 4')

    fig, ax = plt.subplots(2, 4)
    fig.tight_layout()
    y_slice = round(Model4D.midp.imageArray.shape[1]/2)-1
    ax[0,0].imshow(CT4D.dyn3DImageList[0].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0,0].title.set_text('Phase 0')
    ax[0,1].imshow(CT4D.dyn3DImageList[1].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0,1].title.set_text('Phase 1')
    ax[0,2].imshow(CT4D.dyn3DImageList[2].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0,2].title.set_text('Phase 2')
    ax[0,3].imshow(CT4D.dyn3DImageList[3].imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[0,3].title.set_text('Phase 3')
    ax[1,0].imshow(Model4D.midp.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1,0].imshow(wm[0].imageArray[:, y_slice, :].T[::-1, ::1] + wm[1].imageArray[:, y_slice, :].T[::-1, ::1], cmap='Reds', origin='upper', vmin=0, vmax=1, alpha=0.3)
    ax[1,0].imshow(wm[2].imageArray[:, y_slice, :].T[::-1, ::1] + wm[3].imageArray[:, y_slice, :].T[::-1, ::1], cmap='Blues', origin='upper', vmin=0, vmax=1, alpha=0.3)
    ax[1, 0].plot(trackers[0][0],100-trackers[0][2], 'ro')
    ax[1, 0].plot(trackers[1][0],100-trackers[1][2], 'ro')
    ax[1, 0].plot(trackers[2][0],100-trackers[2][2], 'bo')
    ax[1, 0].plot(trackers[3][0],100-trackers[3][2], 'bo')
    ax[1,0].title.set_text('MidP and weight maps')
    ax[1,1].imshow(im1.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1,1].title.set_text('phases [0,2] - amplitude 1')
    ax[1,2].imshow(im2.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1,2].title.set_text('phases [0.5,1.5] - amplitude 1')
    ax[1,3].imshow(im3.imageArray[:, y_slice, :].T[::-1, ::1], cmap='gray', origin='upper', vmin=-1000, vmax=1000)
    ax[1,3].title.set_text('phases [0,2] - amplitude 2')

    plt.show()

    print('done')
    print(' ')
