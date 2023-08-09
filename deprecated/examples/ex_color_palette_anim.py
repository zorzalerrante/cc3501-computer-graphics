# coding=utf-8
"""Animation changing the color palette  while simulating an indirect color scheme with matplotlib"""

from ex_color_palette import *
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"

def updatePalette(colorPalette, t):

    newPalette = []

    for color in colorPalette:
        # Generating a new color changing the RGB order...
        newColor = np.array([
            color[0],
            color[1] * t,
            color[2] * t],
            dtype=np.float)
        newPalette += [newColor]

    return newPalette


if __name__ == "__main__":

    # Reading an image into a numpy array
    originalImage = mpl.imread(getAssetPath("santiago.png"))

    # Removing alpha channel if present
    if originalImage.shape[2] == 4:
        originalImage = originalImage[:,:,0:3]

    # Obtaining all different colors in the image and the indexed image
    indexedImage, colorPalette = getColorPalette(originalImage)

    # Reconstructing image
    animatedImage = assignColors(indexedImage, colorPalette)

    fig, ax = mpl.subplots()
    im = ax.imshow(originalImage, animated=True)

    time = 0

    def updateFig(*args):
        global time
        time += 0.1
        param = np.abs(np.sin(time))
        newColorPalette = updatePalette(colorPalette, param)
        updatedImage = assignColors(indexedImage, newColorPalette)
        im.set_array(updatedImage)
        return im,

    ani = animation.FuncAnimation(fig, updateFig, interval=50, blit=True)
    mpl.show()