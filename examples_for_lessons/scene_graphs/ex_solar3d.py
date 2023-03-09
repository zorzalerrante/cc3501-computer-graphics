import pyglet
from OpenGL.GL import *

import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))

import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.scene_graph as sg
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
from utils import createOFFShape


# Based on Ivan Sipirán's implementaton


class Controller(pyglet.window.Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        self.fillPolygon = True
        self.showAxis = True
        self.total_time = 0.0


def createSystem(pipeline) -> sg.SceneGraphNode:
    sunShape = createOFFShape(pipeline, 1.0, 0.73, 0.03)
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


def set_shader_light_parameters(pipeline):    
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


def setup_projection_view_eye_shader_params(pipeline, projection, viewPos, view):
    glUseProgram(pipeline.shaderProgram)
    set_shader_light_parameters(pipeline)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])


def update_solar_system(dt: float, controller: Controller, solarSystem: sg.SceneGraphNode):
    controller.total_time += dt
    sunRot = sg.findNode(solarSystem, "sunRotation")
    sunRot.transform = tr.rotationY(controller.total_time)

    earthRot = sg.findNode(solarSystem, "earthRotation")
    earthRot.transform = tr.rotationY(2*controller.total_time)
    
    moonRot = sg.findNode(solarSystem, "moonRotation")
    moonRot.transform = tr.rotationY(5*controller.total_time)

    moonSystem = sg.findNode(solarSystem, "moonSystem")
    moonSystem.transform = tr.rotationY(3*controller.total_time)
    
    earthSystem = sg.findNode(solarSystem, "earthSystem")
    earthSystem.transform = tr.rotationY(controller.total_time)
    


# we will use the global controller as communication with the callback function
width = 600
height = 600
controller = Controller(width, height)


@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        controller.fillPolygon = not controller.fillPolygon
    elif symbol == pyglet.window.key.LCTRL:
        controller.showAxis = not controller.showAxis
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()


@controller.event
def on_draw():
    controller.clear()
    if controller.showAxis:
        glUseProgram(mvpPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        mvpPipeline.drawCall(gpuAxis, GL_LINES)

    glUseProgram(lightPipeline.shaderProgram)
    sg.drawSceneGraphNode(solarSystem, lightPipeline, "model")


if __name__ == "__main__":
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    lightPipeline = ls.SimpleFlatShaderProgram()    
    projection = tr.perspective(45, float(width)/float(height), 0.1, 100)
    viewPos = np.array([5,5,5])
    view = tr.lookAt(
        viewPos,
        np.array([0,0,0]),
        np.array([0,1,0])
    )
    
    setup_projection_view_eye_shader_params(mvpPipeline, projection, viewPos, view)
    setup_projection_view_eye_shader_params(lightPipeline, projection, viewPos, view)
    glEnable(GL_DEPTH_TEST)  # to make 3D models look good
    glClearColor(0.3, 0.3, 0.3, 0.3)

    # Creating shapes on GPU memory
    cpuAxis = bs.createAxis(7)
    gpuAxis = es.GPUShape().initBuffers()
    mvpPipeline.setupVAO(gpuAxis)
    gpuAxis.fillBuffers(cpuAxis.vertices, cpuAxis.indices, GL_STATIC_DRAW)
    solarSystem = createSystem(lightPipeline)

    pyglet.clock.schedule(update_solar_system, controller, solarSystem)
    pyglet.app.run()
