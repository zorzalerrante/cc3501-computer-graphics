# coding=utf-8
"""Drawing a deformable shape using GL_STREAM_DRAW"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import math
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
import grafica.basic_shapes as bs
import grafica.easy_shaders as es

__author__ = "Daniel Calderon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.mousePos = (0.0, 0.0)


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


def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)


def createVertices(N, maxPerturbationSize, time, normalizedMousePos):

    numberOfPerturbations = 20 * normalizedMousePos[0]
    perturbationSize = maxPerturbationSize * normalizedMousePos[1]

    # First vertex at the center
    vertices = [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]

    dtheta = 2 * math.pi / N

    for i in range(N):
        theta = i * dtheta

        radialDirection = np.array([math.cos(theta), math.sin(theta)])
        smallPerturbation = perturbationSize * math.sin(4 * time) * math.cos(numberOfPerturbations * theta)
        radious = 0.7 + smallPerturbation

        xCoord = radious * radialDirection[0]
        yCoord = radious * radialDirection[1]

        vertices += [
            # vertex coordinates
            xCoord, yCoord, 0,

            # color generates varying between 0 and 1
            math.sin(theta + 3 * time),       math.cos(theta + 3 * time), 0]

    return vertices


def createIndices(N):

    indices = []
    for i in range(N):
        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return indices


def createShape(N, maxPerturbationSize, time, normalizedMousePos):
    vertices = createVertices(N, maxPerturbationSize, time, normalizedMousePos)
    indices = createIndices(N)
    
    return bs.Shape(vertices, indices)
    

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Drawing a deformable shape", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback functions
    glfw.set_key_callback(window, on_key)
    glfw.set_cursor_pos_callback(window, cursor_pos_callback)
    
    # Creating our shader program and telling OpenGL to use it
    pipeline = es.SimpleShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Creating shapes on GPU memory
    shape = createShape(200, 15, 0.0, (0,0))
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    # We use stream as we will be changing the vertex data on each frame
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STREAM_DRAW)
    
    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen
        glClear(GL_COLOR_BUFFER_BIT)

        time = glfw.get_time()

        normalizedMousePos = (
            controller.mousePos[0] / width,
            controller.mousePos[1] / height
        )

        # A better approach is to generate the vertices directly into the numpy array.
        # python lists are always expensive...
        vertices = createVertices(200, 0.2, time, normalizedMousePos)
        vertexData = np.array(vertices, dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STREAM_DRAW)

        # Drawing the Quad as specified in the VAO with the active shader program
        pipeline.drawCall(gpuShape)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuShape.clear()

    glfw.terminate()