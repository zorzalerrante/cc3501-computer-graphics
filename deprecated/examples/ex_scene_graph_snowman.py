# coding=utf-8
"""
Drawing a Snowman using scene_graph
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
import grafica.scene_graph as sg
import grafica.easy_shaders as es


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


def createColorTriangle(r,g,b):

    # Defining the location and colors of each vertex  of the shape
    vertices = [
    #   positions        colors
        -0.5, -0.5, 0.0,  r, g, b,
         0.5, -0.5, 0.0,  r, g, b,
         0.0,  0.5, 0.0,  r, g, b]

    # Defining connections among vertices
    # We have a triangle every 3 indices specified
    indices = [0, 1, 2]

    return bs.Shape(vertices, indices)


def createColorCircle(N, R, r, g, b):

    # First vertex at the center
    vertices = [0, 0, 0, r, g, b]
    indices = []

    dtheta = 2 * np.pi / N

    for i in range(N):
        theta = i * dtheta

        vertices += [
            # vertex coordinates
            R * np.cos(theta), R * np.sin(theta), 0, r, g, b]

        # A triangle is created using the center, this and the next vertex
        indices += [0, i, i+1]

    # The final triangle connects back to the second vertex
    indices += [0, N, 1]

    return bs.Shape(vertices, indices)


def createSnowman(pipeline):

    # Convenience function to ease initialization
    def createGPUShape(shape):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
        return gpuShape

    # basic GPUShapes
    gpuWhiteCircle = createGPUShape(createColorCircle(30, 1, 1, 1, 1))
    gpuBlackCircle = createGPUShape(createColorCircle(10, 1, 0, 0, 0))
    gpuBrownQuad = createGPUShape(bs.createColorQuad(0.6, 0.3, 0))
    gpuOrangeTriangle = createGPUShape(createColorTriangle(1, 0.6, 0))
    
    # Leaf nodes
    whiteCircleNode = sg.SceneGraphNode("whiteCircleNode")
    whiteCircleNode.childs = [gpuWhiteCircle]

    blackCircleNode = sg.SceneGraphNode("blackCircleNode")
    blackCircleNode.childs = [gpuBlackCircle]

    brownQuadNode = sg.SceneGraphNode("brownQuadNode")
    brownQuadNode.childs = [gpuBrownQuad]
    
    orangeTriangleNode = sg.SceneGraphNode("orangeTriangleNode")
    orangeTriangleNode.childs = [gpuOrangeTriangle]
    
    # Body
    snowballBody = sg.SceneGraphNode("snowballBody")
    snowballBody.transform = tr.scale(10, 10, 0)
    snowballBody.childs = [whiteCircleNode]

    arm = sg.SceneGraphNode("arm")
    arm.transform = tr.matmul([
        tr.translate(0, 5, 0),
        #tr.rotationZ(0),
        tr.scale(2, 10, 1)
    ])
    arm.childs = [brownQuadNode]

    leftArm = sg.SceneGraphNode("leftArm")
    leftArm.transform = tr.matmul([
        tr.translate(-7, 7, 0),
        tr.rotationZ(60 * np.pi / 180),
        #tr.scale(1, 1, 1)
    ])
    leftArm.childs = [arm]

    rightArm = sg.SceneGraphNode("rightArm")
    rightArm.transform = tr.matmul([
        tr.translate(7, 7, 0),
        tr.rotationZ(-60 * np.pi / 180),
        #tr.scale(1, 1, 1)
    ])
    rightArm.childs = [arm]
    
    body = sg.SceneGraphNode("body")
    body.transform = tr.translate(0,10,0)
    body.childs = [snowballBody, leftArm, rightArm]
    
    # Head
    snowballHead = sg.SceneGraphNode("snowballHead")
    snowballHead.transform = tr.scale(8, 8, 0)
    snowballHead.childs = [whiteCircleNode]
    
    leftEye = sg.SceneGraphNode("leftEye")
    leftEye.transform = tr.matmul([
        tr.translate(0, 5, 0),
        #tr.rotationZ(0),
        tr.scale(2, 2, 1)
    ])
    leftEye.childs = [blackCircleNode]
    
    rightEye = sg.SceneGraphNode("rightEye")
    rightEye.transform = tr.matmul([
        tr.translate(5, 5, 0),
        #tr.rotationZ(0),
        tr.scale(2, 2, 1)
    ])
    rightEye.childs = [blackCircleNode]
    
    baseTriangle = sg.SceneGraphNode("baseTriangle")
    baseTriangle.transform = tr.matmul([
        tr.translate(0, 3.5, 0),
        #tr.rotationZ(0),
        tr.scale(2, 7, 1)
    ])
    baseTriangle.childs = [orangeTriangleNode]
    
    nose = sg.SceneGraphNode("nose")
    nose.transform = tr.matmul([
        tr.translate(2, 0, 0),
        tr.rotationZ(-70 * np.pi / 180),
        #tr.scale(1, 1, 1)
    ])
    nose.childs = [baseTriangle]
    
    head = sg.SceneGraphNode("head")
    head.transform = tr.translate(0, 27, 0)
    head.childs = [snowballHead, leftEye, rightEye, nose]
   
    # Snowman, the one and only
    snowman = sg.SceneGraphNode("snowman")
    snowman.childs = [head, body]

    return snowman


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Snowman via scene graph", None, None)

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
    glClearColor(0.55, 0.55, 0.85, 1.0)

    # Creating shapes on GPU memory
    snowman = createSnowman(pipeline)

    # Our shapes here are always fully painted
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()
        
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        theta = np.sin(3.0 * glfw.get_time())

        leftArm = sg.findNode(snowman, "leftArm")
        leftArm.transform = tr.matmul([
            tr.translate(-7, 7, 0),
            tr.rotationZ(theta),
            #tr.scale(1, 1, 1)
        ])

        rightArm = sg.findNode(snowman, "rightArm")
        rightArm.transform = tr.matmul([
            tr.translate(7, 7, 0),
            tr.rotationZ(theta),
            #tr.scale(1, 1, 1)
        ])

        # Drawing the Car
        sg.drawSceneGraphNode(snowman, pipeline, "transform", 
                np.matmul(tr.translate(0, -0.5, 0), tr.scale(0.03, 0.03, 1)))

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    snowman.clear()

    glfw.terminate()
