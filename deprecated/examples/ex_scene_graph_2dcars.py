# coding=utf-8
"""Drawing many cars in 2D using scene_graph2"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es

__author__ = "Daniel Calderon"
__license__ = "MIT"


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return

    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')


def createCar(pipeline):

    # Creating shapes on GPU memory
    blackQuad = bs.createColorQuad(0,0,0)
    gpuBlackQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuBlackQuad)
    gpuBlackQuad.fillBuffers(blackQuad.vertices, blackQuad.indices, GL_STATIC_DRAW)

    redQuad = bs.createColorQuad(1,0,0)
    gpuRedQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuRedQuad)
    gpuRedQuad.fillBuffers(redQuad.vertices, redQuad.indices, GL_STATIC_DRAW)
    
    # Cheating a single wheel
    wheel = sg.SceneGraphNode("wheel")
    wheel.transform = tr.uniformScale(0.2)
    wheel.childs += [gpuBlackQuad]

    wheelRotation = sg.SceneGraphNode("wheelRotation")
    wheelRotation.childs += [wheel]

    # Instanciating 2 wheels, for the front and back parts
    frontWheel = sg.SceneGraphNode("frontWheel")
    frontWheel.transform = tr.translate(0.3,-0.3,0)
    frontWheel.childs += [wheelRotation]

    backWheel = sg.SceneGraphNode("backWheel")
    backWheel.transform = tr.translate(-0.3,-0.3,0)
    backWheel.childs += [wheelRotation]
    
    # Creating the chasis of the car
    chasis = sg.SceneGraphNode("chasis")
    chasis.transform = tr.scale(1,0.5,1)
    chasis.childs += [gpuRedQuad]

    car = sg.SceneGraphNode("car")
    car.childs += [chasis]
    car.childs += [frontWheel]
    car.childs += [backWheel]

    traslatedCar = sg.SceneGraphNode("traslatedCar")
    traslatedCar.transform = tr.translate(0,0.3,0)
    traslatedCar.childs += [car]

    return traslatedCar

def createCars(pipeline, N):

    # First we scale a car
    scaledCar = sg.SceneGraphNode("traslatedCar")
    scaledCar.transform = tr.uniformScale(0.15)
    scaledCar.childs += [createCar(pipeline)] # Re-using the previous function

    cars = sg.SceneGraphNode("cars")

    baseName = "scaledCar"
    for i in range(N):
        # A new node is only locating a scaledCar in the scene depending on index i
        newNode = sg.SceneGraphNode(baseName + str(i))
        newNode.transform = tr.translate(0.4 * i - 0.9, 0.9 - 0.4 * i, 0)
        newNode.childs += [scaledCar]

        # Now this car is added to the 'cars' scene graph
        cars.childs += [newNode]

    return cars


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "2D cars via scene graph", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline = es.SimpleTransformShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Creating shapes on GPU memory
    cars = createCars(pipeline, 5)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Modifying only a specific node in the scene graph
        wheelRotationNode = sg.findNode(cars, "wheelRotation")
        theta = -10 * glfw.get_time()
        wheelRotationNode.transform = tr.rotationZ(theta)

        # Modifying only car 3
        car3 = sg.findNode(cars, "scaledCar3")
        car3.transform = tr.translate(0.3, 0.5 * np.sin(0.1 * theta), 0)

        # Uncomment to see the position of scaledCar_3, it will fill your terminal
        #print("car3Position =", sg.findPosition(cars, "scaledCar3"))

        # Drawing the Car
        sg.drawSceneGraphNode(cars, pipeline, "transform")

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    cars.clear()
    
    glfw.terminate()