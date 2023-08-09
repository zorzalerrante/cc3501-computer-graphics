# coding=utf-8
"""Ilustrating different transformations"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# Transformation states that will operate over the shape
TR_STANDARD      = 0
TR_ROTATE_ZP     = 1
TR_ROTATE_ZM     = 2
TR_TRANSLATE     = 3
TR_UNIFORM_SCALE = 4
TR_NONUNIF_SCALE = 5
TR_REFLEX_Y      = 6
TR_SHEARING_XY   = 7


# Shapes
SP_TRIANGLE   = 0
SP_QUAD       = 1
SP_CUBE       = 2
SP_CIRCLE     = 3


# A class to store the application control
class Controller:
    showTransform = TR_STANDARD
    fillPolygon = True
    shape = SP_TRIANGLE
    animated = False


# we will use the global controller as communication with the callback function
controller = Controller()


def getTransform(showTransform, theta):

    if showTransform == TR_STANDARD:
        return tr.identity()

    elif showTransform == TR_ROTATE_ZP:
        return tr.rotationZ(theta)

    elif showTransform == TR_ROTATE_ZM:
        return tr.rotationZ(-theta)

    elif showTransform == TR_TRANSLATE:
        return tr.translate(0.3 * np.cos(theta), 0.3 * np.cos(theta), 0)

    elif showTransform == TR_UNIFORM_SCALE:
        return tr.uniformScale(0.7 + 0.5 * np.cos(theta))

    elif showTransform == TR_NONUNIF_SCALE:
        return tr.scale(
            1.0 - 0.5 * np.cos(1.5 * theta),
            1.0 + 0.5 * np.cos(2 * theta),
            1.0)

    elif showTransform == TR_REFLEX_Y:
        return tr.scale(1,-1,1)

    elif showTransform == TR_SHEARING_XY:
        return tr.shearing(0.3 * np.cos(theta), 0, 0, 0, 0, 0)
    
    else:
        # This should NEVER happend
        raise Exception()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_0:
        print("No transformations applied")
        controller.showTransform = TR_STANDARD

    elif key == glfw.KEY_1:
        print('Rotation Z+')
        controller.showTransform = TR_ROTATE_ZP

    elif key == glfw.KEY_2:
        print('Rotation Z-')
        controller.showTransform = TR_ROTATE_ZM

    elif key == glfw.KEY_3:
        print('Uniform Scaling')
        controller.showTransform = TR_UNIFORM_SCALE

    elif key == glfw.KEY_4:
        print('Non-uniform Scaling')
        controller.showTransform = TR_NONUNIF_SCALE

    elif key == glfw.KEY_5:
        print('Translation')
        controller.showTransform = TR_TRANSLATE

    elif key == glfw.KEY_6:
        print('Shearing XY')
        controller.showTransform = TR_SHEARING_XY

    elif key == glfw.KEY_7:
        print('Reflexion Y')
        controller.showTransform = TR_REFLEX_Y

    elif key == glfw.KEY_Q:
        print('Showing triangle')
        controller.shape = SP_TRIANGLE

    elif key == glfw.KEY_W:
        print('Showing quad')
        controller.shape = SP_QUAD

    elif key == glfw.KEY_E:
        print('Showing cube')
        controller.shape = SP_CUBE

    elif key == glfw.KEY_R:
        print('Showing circle')
        controller.shape = SP_CIRCLE

    elif key == glfw.KEY_A:
        print('Toggling animated')
        controller.animated = not controller.animated

    elif key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key. Try small numbers!')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Basic Linear Transformations - Modern OpenGL", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    shapeTriangle = bs.createRainbowTriangle()
    gpuTriangle = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTriangle)
    gpuTriangle.fillBuffers(shapeTriangle.vertices, shapeTriangle.indices, GL_STATIC_DRAW)

    shapeQuad = bs.createRainbowQuad()
    gpuQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuad)
    gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)

    shapeCube = bs.createRainbowCube()
    gpuCube = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCube)
    gpuCube.fillBuffers(shapeCube.vertices, shapeCube.indices, GL_STATIC_DRAW)

    shapeCircle = bs.createRainbowCircle(20)
    gpuCircle = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuCircle)
    gpuCircle.fillBuffers(shapeCircle.vertices, shapeCircle.indices, GL_STATIC_DRAW)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if controller.animated:
            # Using the time as the theta parameter
            theta = glfw.get_time()
        else:
            theta = np.pi / 6
        
        transform = getTransform(controller.showTransform, theta)

        if (controller.shape == SP_TRIANGLE):
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, transform)
            pipeline.drawCall(gpuTriangle)

        elif (controller.shape == SP_QUAD):
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, transform)
            pipeline.drawCall(gpuQuad)

        elif (controller.shape == SP_CUBE):
            Rx = tr.rotationX(np.pi/3)
            Ry = tr.rotationY(np.pi/3)
            transform = tr.matmul([Ry, Rx, transform])
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, transform)
            pipeline.drawCall(gpuCube)

        elif (controller.shape == SP_CIRCLE):
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, transform)
            pipeline.drawCall(gpuCircle)

        else:
            # This should never happen
            raise Exception()

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuTriangle.clear()
    gpuQuad.clear()
    gpuCube.clear()
    gpuCircle.clear()
    
    glfw.terminate()