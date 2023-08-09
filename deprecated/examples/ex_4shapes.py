# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr
import grafica.performance_monitor as pm

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so an integer has 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True


# we will use the global controller as communication with the callback function
controller = Controller()

# This function will be executed whenever a key is pressed or released
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

    # Creating a glfw window
    width = 600
    height = 600
    title = "Displaying multiple shapes - Modern OpenGL"
    window = glfw.create_window(width, height, title, None, None)

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
    shapeTriangle = bs.createRainbowTriangle()
    gpuTriangle = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuTriangle)
    gpuTriangle.fillBuffers(shapeTriangle.vertices, shapeTriangle.indices, GL_STATIC_DRAW)

    shapeQuad = bs.createRainbowQuad()
    gpuQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuad)
    gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    # Application loop
    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)

        # Using the time as the theta parameter
        theta = glfw.get_time()

        # Triangle
        triangleTransform = tr.matmul([
            tr.translate(0.5, 0.5, 0),
            tr.rotationZ(2 * theta),
            tr.uniformScale(0.5)
        ])

        # Updating the transform attribute
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, triangleTransform)

        # Drawing function
        pipeline.drawCall(gpuTriangle)

        # Another instance of the triangle
        triangleTransform2 = tr.matmul([
            tr.translate(-0.5, 0.5, 0),
            tr.scale(
                0.5 + 0.2 * np.cos(1.5 * theta),
                0.5 + 0.2 * np.sin(2 * theta),
                0)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, triangleTransform2)
        pipeline.drawCall(gpuTriangle)

        # Quad
        quadTransform = tr.matmul([
            tr.translate(-0.5, -0.5, 0),
            tr.rotationZ(-theta),
            tr.uniformScale(0.7)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, quadTransform)
        pipeline.drawCall(gpuQuad)

        # Another instance of the Quad
        quadTransform2 = tr.matmul([
            tr.translate(0.5, -0.5, 0),
            tr.shearing(0.3 * np.cos(theta), 0, 0, 0, 0, 0),
            tr.uniformScale(0.7)
        ])
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, quadTransform2)
        pipeline.drawCall(gpuQuad)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuTriangle.clear()
    gpuQuad.clear()
    
    glfw.terminate()