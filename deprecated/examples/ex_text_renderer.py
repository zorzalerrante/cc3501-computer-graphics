# coding=utf-8
"""Example drawing text with OpenGL textures"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import datetime
import random
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.performance_monitor as pm
import grafica.text_renderer as tx
from grafica.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"


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


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 700
    height = 700
    title = "Rendering text with OpenGL textures"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Creating shader programs
    texturePipeline = es.SimpleTextureShaderProgram()
    textPipeline = tx.TextureTextRendererShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # Creating texture with all characters
    textBitsTexture = tx.generateTextBitsTexture()
    # Moving texture to GPU memory
    gpuText3DTexture = tx.toOpenGLTexture(textBitsTexture)

    # Testing text 3D texture. Check the terminal!
    for char in "hi!":
        print(textBitsTexture[:, :, ord(char)].transpose() * 255)
        print()

    # Creating shapes on GPU memory
    backgroundShape = bs.createTextureQuad(1,1)
    bs.scaleVertices(backgroundShape, 5, [2,2,1])
    gpuBackground = es.GPUShape().initBuffers()
    texturePipeline.setupVAO(gpuBackground)
    gpuBackground.fillBuffers(backgroundShape.vertices, backgroundShape.indices, GL_STATIC_DRAW)
    gpuBackground.texture = es.textureSimpleSetup(
        getAssetPath("torres-del-paine-sq.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)

    headerText = "Torres del Paine"
    headerCharSize = 0.1
    headerCenterX = headerCharSize * len(headerText) / 2
    headerShape = tx.textToShape(headerText, headerCharSize, headerCharSize)
    gpuHeader = es.GPUShape().initBuffers()
    textPipeline.setupVAO(gpuHeader)
    gpuHeader.fillBuffers(headerShape.vertices, headerShape.indices, GL_STATIC_DRAW)
    gpuHeader.texture = gpuText3DTexture
    headerTransform = tr.matmul([
        tr.translate(0.9, -headerCenterX, 0),
        tr.rotationZ(np.pi/2),
    ])

    dateCharSize = 0.15
    timeCharSize = 0.1

    now = datetime.datetime.now()
    dateStr = now.strftime("%d/%m/%Y")
    timeStr = now.strftime("%H:%M:%S.%f")[:-3]
    dateShape = tx.textToShape(dateStr, dateCharSize, dateCharSize)
    timeShape = tx.textToShape(timeStr, timeCharSize, timeCharSize)
    gpuDate = es.GPUShape().initBuffers()
    gpuTime = es.GPUShape().initBuffers()
    textPipeline.setupVAO(gpuDate)
    textPipeline.setupVAO(gpuTime)
    gpuDate.fillBuffers(dateShape.vertices, dateShape.indices, GL_STATIC_DRAW)
    gpuTime.fillBuffers(timeShape.vertices, timeShape.indices, GL_STATIC_DRAW)
    gpuDate.texture = gpuText3DTexture
    gpuTime.texture = gpuText3DTexture

    second = now.second
    color = [1.0,1.0,1.0]

    perfMonitor = pm.PerformanceMonitor(glfw.get_time(), 0.5)

    # glfw will swap buffers as soon as possible
    glfw.swap_interval(0)

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

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(texturePipeline.shaderProgram)
        texturePipeline.drawCall(gpuBackground)

        glUseProgram(textPipeline.shaderProgram)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1,1,1,0)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0,0,0,1)
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE, headerTransform)
        textPipeline.drawCall(gpuHeader)

        now = datetime.datetime.now()
        dateStr = now.strftime("%d/%m/%Y")
        timeStr = now.strftime("%H:%M:%S.%f")[:-3]
        dateShape = tx.textToShape(dateStr, dateCharSize, dateCharSize)
        timeShape = tx.textToShape(timeStr, timeCharSize, timeCharSize)

        # Updating GPU memory...
        gpuDate.fillBuffers(dateShape.vertices, dateShape.indices, GL_STREAM_DRAW)
        gpuTime.fillBuffers(timeShape.vertices, timeShape.indices, GL_STREAM_DRAW)

        if now.second != second:
            second = now.second
            color = [random.random(), random.random(), random.random()]
        
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), color[0], color[1], color[2], 1)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 1-color[0], 1-color[1], 1-color[2],0.5)
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE,
            tr.translate(-0.9, -0.7, 0))
        textPipeline.drawCall(gpuDate)

        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "fontColor"), 1,1,1,1)
        glUniform4f(glGetUniformLocation(textPipeline.shaderProgram, "backColor"), 0,0,0,0)
        glUniformMatrix4fv(glGetUniformLocation(textPipeline.shaderProgram, "transform"), 1, GL_TRUE,
            tr.translate(-0.9, -0.9, 0))
        textPipeline.drawCall(gpuTime)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuBackground.clear()
    gpuHeader.clear()
    gpuDate.clear()
    gpuTime.clear()

    glfw.terminate()
