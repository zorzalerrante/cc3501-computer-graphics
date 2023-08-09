# coding=utf-8
"""Simulating an indirect color scheme with matplotlib"""

import numpy as np
import matplotlib.pyplot as mpl
import matplotlib.animation as animation
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"

# Extract the different colors from an image
def getColorPalette(image):

    # 3 dimensions: row, column and color
    assert len(image.shape) == 3

    # color must have 3 components (RGB)
    assert image.shape[2] == 3

    # Here we will construct the indexed image, the index is only 8 bits long representing a positive integer number
    indexedImage = np.zeros(shape=(image.shape[0], image.shape[1]), dtype=np.uint8)

    # A helper dictionary to associate colors and indices easily
    colorsDict = {}
    # A list to associate indices and colors easily
    colorsPalette = []

    # Checking each row
    for i in range(image.shape[0]):
        # Checking each column
        for j in range(image.shape[1]):
            # The value image[i,j,X] corresponds to the pixel located at i,j.
            # X could be 0, 1 or 2, refering to the color component Read, Green or Blue respectively.
            # The color component value is float value between 0 and 1.

            # converting the numpy array into a python tuple, which can be used as index in a python dictionary
            pixelColor = (image[i,j,0], image[i,j,1], image[i,j,2])

            # if the color is not in the palette, it is added
            if pixelColor not in colorsDict:
                # Getting an index for the new color
                colorIndex = len(colorsDict)
                # Storing the index in the dictionary for further queries
                colorsDict[pixelColor] = colorIndex
                # Storing the color associated with a given color index
                colorsPalette += [image[i,j,:]]
            
            # storing the index in the indexed image
            #print("pp", colorsDict, pixelColor)
            indexedImage[i,j] = colorsDict[pixelColor]
    
    # returning indexed image and its colors
    return indexedImage, colorsPalette


def assignColors(indexedImage, colorsPalette):

    # 2 dimensions: row and column
    assert len(indexedImage.shape) == 2

    # Here we will construct the image
    image = np.zeros(shape=(indexedImage.shape[0], indexedImage.shape[1], 3), dtype=np.float)

    # Checking each row
    for i in range(indexedImage.shape[0]):
        # Checking each column
        for j in range(indexedImage.shape[1]):
            # Painting the image with the color in the palette
            colorIndex = indexedImage[i,j]
            image[i,j,:] = colorsPalette[colorIndex]
    
    return image


def modifyPalette(colorPalette):

    newPalette = []

    for color in colorPalette:
        # Generating a new color changing the RGB order...
        newColor = np.array([color[1], color[2], color[0]], dtype=np.float)
        newPalette += [newColor]

    return newPalette


if __name__ == "__main__":

    # Reading an image into a numpy array
    originalImage = mpl.imread(getAssetPath("santiago.png"))

    print("Shape of the image: ", originalImage.shape)
    print("Example of pixel value:", originalImage[1,2,:])

    # Removing alpha channel if present
    if originalImage.shape[2] == 4:
        originalImage = originalImage[:,:,0:3]

        print("Alpha channel removed")
        print("Shape of the image: ", originalImage.shape)
        print("Example of pixel value:", originalImage[1,2,:])

    # Obtaining all different colors in the image and the indexed image
    indexedImage, colorsPalette = getColorPalette(originalImage)

    # Modifying the color palette
    newColorPalette = modifyPalette(colorsPalette)

    # Reconstructing image
    reconstructedImage = assignColors(indexedImage, newColorPalette)

    # Arranging the original and modified images
    fig, axs = mpl.subplots(2, 1)
    axs[0].imshow(originalImage)
    axs[1].imshow(reconstructedImage)
    fig.suptitle('Indirect Color Example')

    # Displaying the figure
    mpl.show()