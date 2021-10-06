# coding=utf-8
"""Tarea 3"""

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
from operator import add
import time

__author__ = "Ivan Sipiran"
__license__ = "MIT"

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.showAxis = True
        self.viewPos = np.array([8,8,8])
        self.at = np.array([0,0,0])
        self.camUp = np.array([0, 1, 0])
        self.distance = 8


controller = Controller()

def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T


def bezierMatrix(P0, P1, P2, P3):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
    
    return np.matmul(G, Mb)

# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve

def setPlot(texPipeline, axisPipeline, lightPipeline):
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

    glUseProgram(axisPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glUseProgram(texPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)

    glUseProgram(lightPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "lightPosition"), 5, 5, 5)
    
    glUniform1ui(glGetUniformLocation(lightPipeline.shaderProgram, "shininess"), 1000)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "constantAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "linearAttenuation"), 0.1)
    glUniform1f(glGetUniformLocation(lightPipeline.shaderProgram, "quadraticAttenuation"), 0.01)

def setView(texPipeline, axisPipeline, lightPipeline):
    view = tr.lookAt(
            controller.viewPos,
            controller.at,
            controller.camUp
        )

    glUseProgram(axisPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUseProgram(texPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(texPipeline.shaderProgram, "view"), 1, GL_TRUE, view)

    glUseProgram(lightPipeline.shaderProgram)
    glUniformMatrix4fv(glGetUniformLocation(lightPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    glUniform3f(glGetUniformLocation(lightPipeline.shaderProgram, "viewPosition"), controller.viewPos[0], controller.viewPos[1], controller.viewPos[2])
    

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
    
    elif key == glfw.KEY_1:
        controller.viewPos = np.array([controller.distance,controller.distance,controller.distance]) #Vista diagonal 1
        controller.camUp = np.array([0,1,0])
    
    elif key == glfw.KEY_2:
        controller.viewPos = np.array([0,0,controller.distance]) #Vista frontal
        controller.camUp = np.array([0,1,0])

    elif key == glfw.KEY_3:
        controller.viewPos = np.array([controller.distance,0,controller.distance]) #Vista lateral
        controller.camUp = np.array([0,1,0])

    elif key == glfw.KEY_4:
        controller.viewPos = np.array([0,controller.distance,0]) #Vista superior
        controller.camUp = np.array([1,0,0])
    
    elif key == glfw.KEY_5:
        controller.viewPos = np.array([controller.distance,controller.distance,-controller.distance]) #Vista diagonal 2
        controller.camUp = np.array([0,1,0])
    
    elif key == glfw.KEY_6:
        controller.viewPos = np.array([-controller.distance,controller.distance,-controller.distance]) #Vista diagonal 2
        controller.camUp = np.array([0,1,0])
    
    elif key == glfw.KEY_7:
        controller.viewPos = np.array([-controller.distance,controller.distance,controller.distance]) #Vista diagonal 2
        controller.camUp = np.array([0,1,0])
    
    else:
        print('Unknown key')

def createOFFShape(pipeline, filename, r,g, b):
    shape = readOFF(getAssetPath(filename), (r, g, b))
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

def createCarScene(pipeline):
    chasis = createOFFShape(pipeline, 'alfa2.off', 1.0, 0.0, 0.0)
    wheel = createOFFShape(pipeline, 'wheel.off', 0.0, 0.0, 0.0)

    scale = 2.0
    rotatingWheelNode = sg.SceneGraphNode('rotatingWheel')
    rotatingWheelNode.childs += [wheel]

    chasisNode = sg.SceneGraphNode('chasis')
    chasisNode.transform = tr.uniformScale(scale)
    chasisNode.childs += [chasis]

    wheel1Node = sg.SceneGraphNode('wheel1')
    wheel1Node.transform = tr.matmul([tr.uniformScale(scale),tr.translate(0.056390,0.037409,0.091705)])
    wheel1Node.childs += [rotatingWheelNode]

    wheel2Node = sg.SceneGraphNode('wheel2')
    wheel2Node.transform = tr.matmul([tr.uniformScale(scale),tr.translate(-0.060390,0.037409,-0.091705)])
    wheel2Node.childs += [rotatingWheelNode]

    wheel3Node = sg.SceneGraphNode('wheel3')
    wheel3Node.transform = tr.matmul([tr.uniformScale(scale),tr.translate(-0.056390,0.037409,0.091705)])
    wheel3Node.childs += [rotatingWheelNode]

    wheel4Node = sg.SceneGraphNode('wheel4')
    wheel4Node.transform = tr.matmul([tr.uniformScale(scale),tr.translate(0.066090,0.037409,-0.091705)])
    wheel4Node.childs += [rotatingWheelNode]

    car1 = sg.SceneGraphNode('car1')
    #car1.transform = tr.matmul([tr.translate(2.0, -0.037409, 5.0), tr.rotationY(np.pi)])
    car1.childs += [chasisNode]
    car1.childs += [wheel1Node]
    car1.childs += [wheel2Node]
    car1.childs += [wheel3Node]
    car1.childs += [wheel4Node]

    scene = sg.SceneGraphNode('system')
    scene.childs += [car1]

    return scene

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 800
    height = 800
    title = "Tarea 2"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Assembling the shader program (pipeline) with both shaders
    axisPipeline = es.SimpleModelViewProjectionShaderProgram()
    texPipeline = es.SimpleTextureModelViewProjectionShaderProgram()
    lightPipeline = ls.SimpleGouraudShaderProgram()
    
    # Telling OpenGL to use our shader program
    glUseProgram(axisPipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Creating shapes on GPU memory
    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    axisPipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)

    #NOTA: Aqui creas un objeto con tu escena
    car = createCarScene(lightPipeline)
    setPlot(texPipeline, axisPipeline,lightPipeline)

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

    N = 3500
    R0 = np.array([[0, 0, 0]]).T
    R1 = np.array([[-4, 0, 0]]).T
    R2 = np.array([[4, 0, 6]]).T
    R3 = np.array([[0, 0, 6]]).T
    
    M1 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve1 = evalCurve(M1, N)

    R0 = np.array([[0, 0, 6]]).T
    R1 = np.array([[-4, 0, 6]]).T
    R2 = np.array([[4, 0, 0]]).T
    R3 = np.array([[0, 0, 0]]).T
    
    M2 = bezierMatrix(R0, R1, R2, R3)
    bezierCurve2 = evalCurve(M2, N)

    C = np.concatenate((bezierCurve1,bezierCurve2), axis=0)
    print(C.shape)

    step = 0

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

        setView(texPipeline, axisPipeline, lightPipeline)

        if controller.showAxis:
            glUseProgram(axisPipeline.shaderProgram)
            glUniformMatrix4fv(glGetUniformLocation(axisPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
            axisPipeline.drawCall(gpuAxis, GL_LINES)

        if step > N*2-1:
            step = 0

        if step < N*2-1:
            angle = np.arctan2(C[step+1,0]-C[step,0], C[step+1,2]-C[step,2])
        else:
            angle = np.arctan2(C[0,0]-C[step,0],C[0,2]-C[step,2])
        
        carNode = sg.findNode(car, "system")
        carNode.transform = tr.matmul([tr.translate(C[step,0], C[step,1], C[step,2]), tr.rotationY(angle)])

        step = step + 1
       
        #NOTA: Aquí dibujas tu objeto de escena
        glUseProgram(lightPipeline.shaderProgram)
        sg.drawSceneGraphNode(car, lightPipeline, "model")

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    dibujo.clear()
    

    glfw.terminate()