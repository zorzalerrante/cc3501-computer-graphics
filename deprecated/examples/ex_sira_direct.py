# coding=utf-8
"""Using a direct color scheme with sira"""

import os, sys
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sira

__author__ = "Daniel Calderon"
__license__ = "MIT"

if __name__ == "__main__":
    
    S = 100
    W = 6
    H = 4
    windowSize = (W*S, H*S)
    imgData = np.zeros((W, H, 3), dtype=np.uint8)
    imgData[0:2, 0:2, :] = np.array([0,0,255], dtype=np.uint8)
    imgData[0:6, 2:4, :] = np.array([255,0,0], dtype=np.uint8)
    imgData[2:6, 0:2, :] = np.array([255,255,255], dtype=np.uint8)
    
    display = sira.DirectRGBRasterDisplay(windowSize, imgData.shape, "Direct RGB Raster Display")
    display.setMatrix(imgData)
    display.draw()
