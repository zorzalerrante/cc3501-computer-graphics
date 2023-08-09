# coding=utf-8
"""
Interactions with keyboard and mouse via GLFW/python

More information at:
https://www.glfw.org/docs/latest/input_guide.html

How to convert GLFW/C calls to GLFW/python
https://pypi.org/project/glfw/
"""

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


# A class to control the application
class Controller:
    def __init__(self):
        self.leftClickOn = False
        self.theta = 0.0
        self.mousePos = (0.0, 0.0)


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action == glfw.PRESS:
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)


def mouse_button_callback(window, button, action, mods):

    global controller

    """
    glfw.MOUSE_BUTTON_1: left click
    glfw.MOUSE_BUTTON_2: right click
    glfw.MOUSE_BUTTON_3: scroll click
    """

    if (action == glfw.PRESS or action == glfw.REPEAT):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = True
            print("Mouse click - button 1")

        if (button == glfw.MOUSE_BUTTON_2):
            print("Mouse click - button 2:", glfw.get_cursor_pos(window))

        if (button == glfw.MOUSE_BUTTON_3):
            print("Mouse click - button 3")

    elif (action ==glfw.RELEASE):
        if (button == glfw.MOUSE_BUTTON_1):
            controller.leftClickOn = False


def scroll_callback(window, x, y):

    print("Mouse scroll:", x, y)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Handling mouse events", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)


    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Connecting callback functions to handle mouse events:
    # - Cursor moving over the window
    # - Mouse buttons input
    # - Mouse scroll
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_scroll_callback(window, scroll_callback)

    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Convenience function to ease initialization
    def createGPUColorQuad(r,g,b):
        shapeQuad = bs.createColorQuad(r,g,b)
        gpuQuad = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuQuad)
        gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)
        return gpuQuad

    # Creating shapes on GPU memory
    blueQuad = createGPUColorQuad(0,0,1)
    redQuad = createGPUColorQuad(1,0,0)
    yellowQuad = createGPUColorQuad(1,1,0)
    greenQuad = createGPUColorQuad(0,1,0)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    t0 = glfw.get_time()

    while not glfw.window_should_close(window):
        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # While left click is pressed, we have continous rotation movement
        if controller.leftClickOn:
            controller.theta += 4 * dt
            if controller.theta >= 2 * np.pi:
                controller.theta -= 2 * np.pi
        
        # Setting transform and drawing the rotating red quad
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.matmul([
            tr.rotationZ(controller.theta),
            tr.translate(0.5, 0.0, 0.0),
            tr.uniformScale(0.5)
        ]))
        pipeline.drawCall(redQuad)

        # Getting the mouse location in opengl coordinates
        mousePosX = 2 * (controller.mousePos[0] - width/2) / width
        mousePosY = 2 * (height/2 - controller.mousePos[1]) / height
 
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
            tr.translate(mousePosX, mousePosY, 0),
            tr.uniformScale(0.3)
        ))
        pipeline.drawCall(greenQuad)

        # This is another way to work with keyboard inputs
        # Here we request the state of a given key
        if (glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.PRESS):
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
                tr.translate(-0.6, 0.4, 0.0),
                tr.uniformScale(0.2)
            ))
            pipeline.drawCall(blueQuad)

        # All "non-pressed" keys are in release state
        if (glfw.get_key(window, glfw.KEY_LEFT_CONTROL) == glfw.RELEASE):
            glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
                tr.translate(-0.6, 0.6, 0.0),
                tr.uniformScale(0.2)
            ))
            pipeline.drawCall(yellowQuad)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    blueQuad.clear()
    redQuad.clear()
    yellowQuad.clear()
    greenQuad.clear()

    glfw.terminate()