import math
import numpy as np
import matplotlib.pyplot as plt
import logging

from opentps.core.data.images import CTImage
from opentps.core.processing.imageSimulation.ForwardProjectorTigre import forwardProjectionTigre

logger = logging.getLogger(__name__)

def run():

    # GENERATE SYNTHETIC CT IMAGE
    im = np.full((170, 170, 100), -1000)
    im[20:150, 70:130, :] = 0
    im[30:70, 80:120, 20:] = -800
    im[100:140, 80:120, 20:] = -800
    im[45:55, 95:105, 30:40] = 0
    im[80:90, 115:125, :] = 800
    im[:, 130:140, :] = 100  # couch
    ct = CTImage(imageArray=im, name='fixed', origin=[0, 0, 0], spacing=[2, 2.5, 3])

    # Compute projections
    angles = np.array([0,90,180])*2*math.pi/360
    DRR_no_noise = forwardProjectionTigre(ct, angles, axis='Z', poissonNoise=None, gaussianNoise=None)
    DRR_realistic = forwardProjectionTigre(ct, angles, axis='Z')
    DRR_high_noise = forwardProjectionTigre(ct, angles, axis='Z', poissonNoise=3e4, gaussianNoise=30)

    # Compute error
    error_realistic_projections = np.abs(DRR_realistic-DRR_no_noise)
    error_realistic_projections_high_noise = np.abs(DRR_high_noise-DRR_no_noise)

    # Display results
    fig, ax = plt.subplots(3, 5)
    ax[0,0].imshow(DRR_no_noise[0][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[0,1].imshow(DRR_realistic[0][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[0,2].imshow(error_realistic_projections[0][::-1, ::1], cmap='gray', origin='upper', vmin=0, vmax=np.max(DRR_no_noise)/100)
    ax[0,3].imshow(DRR_high_noise[0][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[0,4].imshow(error_realistic_projections_high_noise[0][::-1, ::1], cmap='gray', origin='upper', vmin=0, vmax=np.max(DRR_no_noise)/100)
    ax[1,0].imshow(DRR_no_noise[1][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[1,1].imshow(DRR_realistic[1][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[1,2].imshow(error_realistic_projections[1][::-1, ::1], cmap='gray', origin='upper', vmin=0, vmax=np.max(DRR_no_noise)/100)
    ax[1,3].imshow(DRR_high_noise[1][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[1,4].imshow(error_realistic_projections_high_noise[1][::-1, ::1], cmap='gray', origin='upper', vmin=0, vmax=np.max(DRR_no_noise)/100)
    ax[2,0].imshow(DRR_no_noise[2][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[2,1].imshow(DRR_realistic[2][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[2,2].imshow(error_realistic_projections[2][::-1, ::1], cmap='gray', origin='upper', vmin=0, vmax=np.max(DRR_no_noise)/100)
    ax[2,3].imshow(DRR_high_noise[2][::-1, ::1], cmap='gray', origin='upper', vmin=np.min(DRR_no_noise), vmax=np.max(DRR_no_noise))
    ax[2,4].imshow(error_realistic_projections_high_noise[2][::-1, ::1], cmap='gray', origin='upper', vmin=0, vmax=np.max(DRR_no_noise)/100)
    ax[0,0].title.set_text('Perfect DRR')
    ax[0,1].title.set_text('DRR with moderate noise')
    ax[0,2].title.set_text('Moderate noise')
    ax[0,3].title.set_text('DRR with high noise')
    ax[0,4].title.set_text('High noise')
    plt.show()

    print('TIGRE DRR example completed')

if __name__ == "__main__":
    run()