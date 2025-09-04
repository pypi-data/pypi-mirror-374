"""
This example shows how two different python environnements can be used together.
A parent script launches a child script which uses a different python
environement but shares the same image data.

Key features:
- The parent script launches a child script which use a different python environnement
- Share RAM memory space between 2 scripts without the need to save and load data on/from hard drives.
"""

import matplotlib.pyplot as plt
import numpy as np
import subprocess
from multiprocessing import shared_memory

from opentps.core.examples.syntheticData import createSynthetic3DCT

## set the child script environnement path and child scrip file path
script2EnvPath = 'python.exe'  ## example: 'C:/Users/johnsmith/anaconda3/envs/myEnv/python.exe
script2Path = 'sharedMemoryChild.py'

# create test image to share between scripts
ct = createSynthetic3DCT()
sliceToShow = 100

# initialize shared memory and copy image array to this space
print(ct.imageArray.shape) ## these must be either passed to the child script as arguments or fixed and known
print(ct.imageArray.dtype)
print(ct.imageArray.nbytes)
shm = shared_memory.SharedMemory(create=True, size=ct.imageArray.nbytes, name='sharedArray')
sharedTestArray = np.ndarray(ct.imageArray.shape, dtype=ct.imageArray.dtype, buffer=shm.buf)
sharedTestArray[:] = ct.imageArray[:]

## plot image before child script call
plt.figure()
plt.title("Before subprocess")
plt.imshow(ct.imageArray[:, sliceToShow, :])
plt.show()

## Call to child script
subprocess.call(script2EnvPath + ' ' + script2Path)

## Copy shared memory space to test image array
ct.imageArray[:] = sharedTestArray[:]

## Plot image after child script call
plt.figure()
plt.title("After subprocess")
plt.imshow(ct.imageArray[:, sliceToShow, :])
plt.show()

## Close the shared memory
shm.close()
shm.unlink()




