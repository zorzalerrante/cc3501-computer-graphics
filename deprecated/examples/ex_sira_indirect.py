# coding=utf-8
"""Using an indirect color scheme with sira"""

import os, sys
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sira

__author__ = "Daniel Calderon"
__license__ = "MIT"


if __name__ == "__main__":
    
    windowSize = (600,600)
    
    S = 100
    W = 6
    H = 4
    windowSize = (W*S, H*S)

    colorPalette = np.ndarray((4,3), dtype=np.uint8)
    colorPalette[0] = np.array([0,50,0], dtype=np.uint8)
    colorPalette[1] = np.array([0,100,0], dtype=np.uint8)
    colorPalette[2] = np.array([0,150,0], dtype=np.uint8)
    colorPalette[3] = np.array([0,200,0], dtype=np.uint8)

    imgData = np.ndarray((W,H), dtype=np.uint8)
    imgData[:,0] = 0
    imgData[:,1] = 1
    imgData[:,2] = 2
    imgData[:,3] = 3
    
    display = sira.IndirectRGBRasterDisplay(windowSize, (W,H), "Indirect RGB Raster Display")

    display.setColorPalette(colorPalette)
    display.setMatrix(imgData)
    display.draw()

