# coding=utf-8
"""Render to Texture Example"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es

__author__ = "Daniel Calderon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    fillPolygon = True
    fillTexture = True


# we will use the global controller as communication with the callback function
controller = Controller()


def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    if key == glfw.KEY_LEFT_CONTROL:
        controller.fillTexture = not controller.fillTexture

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)

    else:
        print('Unknown key')


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Render To Texture", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    #glEnable(GL_DEPTH_TEST)

    
    # Framebuffer configuration
    #######################
    
    # Generating a new freamebuffer and binding it
    framebuffer = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)

    # Create a color attachment texture
    textureColorbuffer = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textureColorbuffer)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, None)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, textureColorbuffer, 0)

    # Create a renderbuffer object for depth and stencil attachment (we won't be sampling these)
    rbo = glGenRenderbuffers(1)
    glBindRenderbuffer(GL_RENDERBUFFER, rbo)

    # use a single renderbuffer object for both a depth AND stencil buffer.
    glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH24_STENCIL8, width, height)

    # now actually attach it
    glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rbo)

    # now that we actually created the framebuffer and added all attachments we want to check if it is actually complete now
    if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
        print("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")

    # Binding again the default shape buffer
    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    

    # Creating shader programs for textures and for colors
    #######################
    textureShaderProgram = es.SimpleTextureTransformShaderProgram()
    colorShaderProgram = es.SimpleModelViewProjectionShaderProgram()

    # Creating shapes on GPU memory
    #######################
    rainbowCube = bs.createRainbowCube()
    gpuRainbowCube = es.GPUShape().initBuffers()
    colorShaderProgram.setupVAO(gpuRainbowCube)
    gpuRainbowCube.fillBuffers(rainbowCube.vertices, rainbowCube.indices, GL_STATIC_DRAW)
    
    shapeQuad = bs.createTextureQuad(1,1)
    gpuQuad = es.GPUShape().initBuffers()
    textureShaderProgram.setupVAO(gpuQuad)
    gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)
    gpuQuad.texture = textureColorbuffer # <--- Here is where the magic happens!

    # Setting up the scene
    view = tr.lookAt(
            np.array([1.0, 1.0, 1.0]),
            np.array([0.0, 0.0, 0.0]),
            np.array([0.0, 0.0, 1.0])
        )
    projection = tr.ortho(-1, 1, -1, 1, 0.1, 100)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Using the time as the theta parameter
        theta = glfw.get_time()

        # Rendering to a texture
        #######################
        glBindFramebuffer(GL_FRAMEBUFFER, framebuffer)
        #glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.15, 0.15, 0.15, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Drawing
        glUseProgram(colorShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "model"), 1, GL_TRUE, tr.rotationZ(theta))
        glUniformMatrix4fv(glGetUniformLocation(colorShaderProgram.shaderProgram, "view"), 1, GL_TRUE, view)
        colorShaderProgram.drawCall(gpuRainbowCube)
        
        
        # Rendering the rendered texture to the viewport as a simple quad
        #######################
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glDisable(GL_DEPTH_TEST)
        glClearColor(0.85, 0.85, 0.85, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if (controller.fillTexture):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        glUseProgram(textureShaderProgram.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(textureShaderProgram.shaderProgram, "transform"), 1, GL_TRUE,
            tr.matmul([
                tr.translate(0.3 * np.cos(theta), 0, 0),
                tr.shearing(0.3 * np.cos(theta), 0, 0, 0, 0, 0)])
        )
        textureShaderProgram.drawCall(gpuQuad)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuRainbowCube.clear()
    gpuQuad.clear()

    glfw.terminate()