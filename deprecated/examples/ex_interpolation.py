import numpy as np
import matplotlib.pyplot as plt

__author__ = "Ivan Sipiran"
__license__ = "MIT"

if __name__ == "__main__":
    topLeft = [0,0,0]
    topRight = [255, 0, 0]
    bottomLeft = [0, 255, 0]
    bottomRight = [0, 0, 255]

    resolution = 4

    redVerticalLeft = np.linspace(topLeft[0], bottomLeft[0], resolution)
    greenVerticalLeft = np.linspace(topLeft[1], bottomLeft[1], resolution)
    blueVerticalLeft = np.linspace(topLeft[2], bottomLeft[2], resolution)

    redVerticalRight = np.linspace(topRight[0], bottomRight[0], resolution)
    greenVerticalRight = np.linspace(topRight[1], bottomRight[1], resolution)
    blueVerticalRight = np.linspace(topRight[2], bottomRight[2], resolution)

    resultImage = np.zeros((resolution, resolution, 3), dtype=np.uint8)

    for indexRow in range(resolution):
        redHorizontal = np.linspace(redVerticalLeft[indexRow], redVerticalRight[indexRow], resolution)
        greenHorizontal = np.linspace(greenVerticalLeft[indexRow], greenVerticalRight[indexRow], resolution)
        blueHorizontal = np.linspace(blueVerticalLeft[indexRow], blueVerticalRight[indexRow], resolution)

        for indexCol in range(resolution):
            resultImage[indexRow,indexCol,:] = [redHorizontal[indexCol],greenHorizontal[indexCol], blueHorizontal[indexCol]]

    plt.imshow(resultImage)
    plt.axis('off')
    plt.show()
    


