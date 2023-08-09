# coding=utf-8
"""Transforming vertices in the CPU to create shapes."""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# A class to store the application control
class Controller:
    fillPolygon = True


# we will use the global controller as communication with the callback function
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


def createShape():
    """
    Generating a circle, where the vertices at the border are generated via matrix
    transformations.
    """

    # Adding the vertex at the center, white color to identify it
    #            position       color
    vertices = [ 0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
    indices = []

    # This vector will be used as reference to be transformed
    xt = np.array([1,0,0,1])

    # We iterate generating vertices over the circle border
    for i in range(0,30):

        # attempt 1: modifying manually each vertex.
        #         positions                                                        colors
        #vertices += [r * np.cos(0.1 *i * np.pi), r * np.sin(0.1 *i * np.pi), 0.0,    1,0,0]

        # attempt 2: using matrix transformations
        transformation = tr.rotationZ(0.1 *i * np.pi)
        xtp = np.matmul(transformation, xt)

        # returning to cartesian coordinates from homogeneous coordinates
        xtr = np.array([xtp[0], xtp[1], xtp[2]]) / xtp[3]

        # Adding the new vertex in clue color
        #            position                color
        vertices += [xtr[0], xtr[1], xtr[2], 0.0, 0.0, 1.0]

        # do not forget the indices!
        indices += [0, i+1, i+2]


    # removing the last spare vertex
    indices.pop()

    return bs.Shape(vertices, indices)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Transforming vertices in the CPU", None, None)

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

    # Creating shapes on GPU memory
    shape = createShape()
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    # We do not need to update the transform in every frame, so we can do it here
    transform = tr.translate(0,-0.5,0)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, transform)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen and drawing
        glClear(GL_COLOR_BUFFER_BIT)
        pipeline.drawCall(gpuShape)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuShape.clear()
    
    glfw.terminate()