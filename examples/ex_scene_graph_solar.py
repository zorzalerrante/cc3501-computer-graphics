# coding=utf-8
"""Drawing 3D cars via scene graph"""

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
import grafica.lighting_shaders as ls
import grafica.performance_monitor as pm
from grafica.assets_path import getAssetPath

__author__ = "Ivan Sipiran"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_LEFT_CONTROL:
        controller.showAxis = not controller.showAxis

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')

def createOFFShape(pipeline, r,g, b):
    shape = readOFF(getAssetPath('sphere.off'), (r, g, b))
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)

    return gpuShape

def readOFF(filename, color):
    vertices = []
    normals= []
    faces = []

    with open(filename, 'r') as file:
        line = file.readline().strip()
        assert line=="OFF"

        line = file.readline().strip()
        aux = line.split(' ')

        numVertices = int(aux[0])
        numFaces = int(aux[1])

        for i in range(numVertices):
            aux = file.readline().strip().split(' ')
            vertices += [float(coord) for coord in aux[0:]]
        
        vertices = np.asarray(vertices)
        vertices = np.reshape(vertices, (numVertices, 3))
        print(f'Vertices shape: {vertices.shape}')

        normals = np.zeros((numVertices,3), dtype=np.float32)
        print(f'Normals shape: {normals.shape}')

        for i in range(numFaces):
            aux = file.readline().strip().split(' ')
            aux = [int(index) for index in aux[0:]]
            faces += [aux[1:]]
            
            vecA = [vertices[aux[2]][0] - vertices[aux[1]][0], vertices[aux[2]][1] - vertices[aux[1]][1], vertices[aux[2]][2] - vertices[aux[1]][2]]
            vecB = [vertices[aux[3]][0] - vertices[aux[2]][0], vertices[aux[3]][1] - vertices[aux[2]][1], vertices[aux[3]][2] - vertices[aux[2]][2]]

            res = np.cross(vecA, vecB)
            normals[aux[1]][0] += res[0]  
            normals[aux[1]][1] += res[1]  
            normals[aux[1]][2] += res[2]  

            normals[aux[2]][0] += res[0]  
            normals[aux[2]][1] += res[1]  
            normals[aux[2]][2] += res[2]  

            normals[aux[3]][0] += res[0]  
            normals[aux[3]][1] += res[1]  
            normals[aux[3]][2] += res[2]  
        #print(faces)
        norms = np.linalg.norm(normals,axis=1)
        normals = normals/norms[:,None]

        color = np.asarray(color)
        color = np.tile(color, (numVertices, 1))

        vertexData = np.concatenate((vertices, color), axis=1)
        vertexData = np.concatenate((vertexData, normals), axis=1)

        print(vertexData.shape)

        indices = []
        vertexDataF = []
        index = 0

        for face in faces:
            vertex = vertexData[face[0],:]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[1],:]
            vertexDataF += vertex.tolist()
            vertex = vertexData[face[2],:]
            vertexDataF += vertex.tolist()
            
            indices += [index, index + 1, index + 2]
            index += 3        



        return bs.Shape(vertexDataF, indices)

def createSystem(pipeline):
    sunShape = createOFFShape(pipeline, 1.0,0.73,0.03)
    earthShape = createOFFShape(pipeline, 0.0, 0.59, 0.78)
    moonShape = createOFFShape(pipeline, 0.3, 0.3, 0.3)

    sunNode = sg.SceneGraphNode("sunNode")
    sunNode.transform = tr.uniformScale(0.3)
    sunNode.childs += [sunShape]

    earthNode = sg.SceneGraphNode("earthNode")
    earthNode.transform = tr.uniformScale(0.1)
    earthNode.childs += [earthShape]

    moonNode = sg.SceneGraphNode("moonNode")
    moonNode.transform = tr.uniformScale(0.02)
    moonNode.childs += [moonShape]

    moonRotation = sg.SceneGraphNode("moonRotation")
    moonRotation.childs += [moonNode]

    earthRotation = sg.SceneGraphNode("earthRotation")
    earthRotation.childs += [earthNode]

    moonRotation = sg.SceneGraphNode("moonRotation")
    moonRotation.childs += [moonNode]

    sunRotation = sg.SceneGraphNode("sunRotation")
    sunRotation.childs += [sunNode]
    
    moonPosition = sg.SceneGraphNode("moonSystem")
    moonPosition.transform = tr.translate(0.3,0.0,0.0)
    moonPosition.childs += [moonRotation] 

    moonSystem = sg.SceneGraphNode("moonSystem")
    moonSystem.childs += [moonPosition]
    
    earthPosition = sg.SceneGraphNode("earthSystem")
    earthPosition.transform = tr.translate(1.5, 0.0, 0.0)
    earthPosition.childs += [earthRotation]
    earthPosition.childs += [moonSystem]

    earthSystem = sg.SceneGraphNode("earthSystem")
    earthSystem.childs += [earthPosition]

    systemNode = sg.SceneGraphNode("solarSystem")
    systemNode.childs += [sunRotation]
    systemNode.childs += [earthSystem]
    
    return systemNode


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600
    title = "3D cars via scene graph"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    pipeline = ls.SimpleFlatShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(mvpPipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    mvpPipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    solarSystem = createSystem(pipeline)
    
    # Using the same view and projection matrices in the whole application
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

    glUseProgram(mvpPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glUseProgram(pipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    
    viewPos = np.array([5,5,5])
    view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,1,0])
        )

    glUseProgram(mvpPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUseProgram(pipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
    
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), 3, 3, 3)
    
    glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.001)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    while not glfw.window_should_close(window):

        # Measuring performance
        perfMonitor.update(glfw.get_time())
        glfw.set_window_title(window, title + str(perfMonitor))

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        if controller.showAxis:
            glUseProgram(mvpPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            mvpPipeline.drawCall(gpuAxis, GL_LINES)

        glUseProgram(pipeline.shaderProgram)
        
        sunRot = sg.findNode(solarSystem, "sunRotation")
        sunRot.transform = tr.rotationY(glfw.get_time())

        earthRot = sg.findNode(solarSystem, "earthRotation")
        earthRot.transform = tr.rotationY(2*glfw.get_time())
        
        moonRot = sg.findNode(solarSystem, "moonRotation")
        moonRot.transform = tr.rotationY(5*glfw.get_time())

        moonSystem = sg.findNode(solarSystem, "moonSystem")
        moonSystem.transform = tr.rotationY(3*glfw.get_time())
        
        earthSystem = sg.findNode(solarSystem, "earthSystem")
        earthSystem.transform = tr.rotationY(glfw.get_time())
        
        sg.drawSceneGraphNode(solarSystem, pipeline, "model")

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    solarSystem.clear()
    

    glfw.terminate()