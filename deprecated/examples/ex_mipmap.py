# coding=utf-8
"""Using mipmaps"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
from PIL import Image
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
from grafica.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True


# global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 1200
    height = 600

    window = glfw.create_window(width, height, "No-Mipmap vs Mipmap", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader program
    pipeline = es.SimpleTextureTransformShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Shape on CPU memory
    shapeTextureQuad = bs.createTextureQuad(1, 1)
    
    # Shapes on GPU memory
    gpuShapeWithoutMipmap = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShapeWithoutMipmap)
    gpuShapeWithoutMipmap.fillBuffers(shapeTextureQuad.vertices, shapeTextureQuad.indices, GL_STATIC_DRAW)
    gpuShapeWithoutMipmap.texture = es.textureSimpleSetup(getAssetPath("red_woodpecker.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    
    # Since we want to draw the same shape, but with mipmaps in its texture, there is no need to duplicate
    # the information in the GPU, we can just use the same buffers...
    gpuShapeWithMipmap = es.GPUShape()
    gpuShapeWithMipmap.vao = gpuShapeWithoutMipmap.vao
    gpuShapeWithMipmap.vbo = gpuShapeWithoutMipmap.vbo
    gpuShapeWithMipmap.ebo = gpuShapeWithoutMipmap.ebo
    gpuShapeWithMipmap.size = gpuShapeWithoutMipmap.size
    
    # ... but with a different texture
    textureWithMipmap = es.textureSimpleSetup(getAssetPath("red_woodpecker.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR_MIPMAP_NEAREST, GL_LINEAR)
    glGenerateMipmap(GL_TEXTURE_2D)  # <---- Here we generate mipmaps for the binded texture.

    gpuShapeWithMipmap.texture = textureWithMipmap

    print("Here we can verify that we are using the same GPU buffers, but with a different texture")
    print("Shape without mipmaps : ", gpuShapeWithoutMipmap)
    print("Shape with mipmaps    : ", gpuShapeWithMipmap)
       
    t0 = glfw.get_time()
    scale = 1.0

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        if ((glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS) or\
            (glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS)) and\
            scale > 0.1:
            scale -= 2 * dt

        if ((glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS) or\
            (glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS)) and\
            scale < 1.0:
            scale += 2 * dt

        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing shapes
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
                tr.translate(-0.5, 0, 0),
                tr.scale(scale, 2*scale, 1)
                ]))
        pipeline.drawCall(gpuShapeWithoutMipmap)

        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
                tr.translate(0.5, 0, 0),
                tr.scale(scale, 2*scale, 1)
                ]))
        pipeline.drawCall(gpuShapeWithMipmap)
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuShapeWithoutMipmap.clear()
    #gpuShapeWithMipmap.clear()
    
    glfw.terminate()
