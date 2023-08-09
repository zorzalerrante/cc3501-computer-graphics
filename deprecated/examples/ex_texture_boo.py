# coding=utf-8
"""Textures and transformations in 2D"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
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

    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Boo!", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # A simple shader program with position and texture coordinates as inputs.
    pipeline = es.SimpleTextureTransformShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating shapes on GPU memory
    shapeBoo = bs.createTextureQuad(1,1)
    gpuBoo = GPUShape().initBuffers()
    pipeline.setupVAO(gpuBoo)
    gpuBoo.fillBuffers(shapeBoo.vertices, shapeBoo.indices, GL_STATIC_DRAW)
    gpuBoo.texture = es.textureSimpleSetup(
        getAssetPath("boo.png"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_NEAREST, GL_NEAREST)

    shapeQuestionBoxes = bs.createTextureQuad(10,1)
    gpuQuestionBoxes = GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuestionBoxes)
    gpuQuestionBoxes.fillBuffers(shapeQuestionBoxes.vertices, shapeQuestionBoxes.indices, GL_STATIC_DRAW)
    gpuQuestionBoxes.texture = es.textureSimpleSetup(
        getAssetPath("cg_box.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)
    
    questionBoxesTransform = np.matmul(tr.translate(0, -0.8, 0), tr.scale(2, 0.2, 1))
    

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        theta = glfw.get_time()
        tx = 0.7 * np.sin(0.5 * theta)
        ty = 0.2 * np.sin(5 * theta)
    
        # derivative of tx give us the direction
        dtx = 0.7 * 0.5 * np.cos(0.5 * theta)
        if dtx > 0:
            reflex = tr.identity()
        else:
            reflex = tr.scale(-1, 1, 1)

        # Drawing the shapes
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
                tr.translate(tx, ty, 0),
                tr.scale(0.5, 0.5, 1.0),
                reflex]))
        pipeline.drawCall(gpuBoo)
        
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, questionBoxesTransform)
        pipeline.drawCall(gpuQuestionBoxes)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuBoo.clear()
    #gpuQuestionBoxes.clear()

    glfw.terminate()
