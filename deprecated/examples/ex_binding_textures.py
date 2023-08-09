# coding=utf-8
"""Using 2 different textures in the same Fragment Shader"""

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
from grafica.assets_path import getAssetPath

from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES

__author__ = "Sebastián Olmos"
__license__ = "MIT"

# We extend the functionality of a GPUShape with an additional texture.
class TexGPUShape(GPUShape):
    def __init__(self):
        """VAO, VBO, EBO and texture handlers to GPU memory"""
        super().__init__()
        self.texture2 = None

    def __str__(self):
        return super().__str__() + "  tex=" + str(self.texture2)

    def clear(self):
        """Freeing GPU memory"""

        super().clear()
        if self.texture2 != None:
            glDeleteTextures(1, [self.texture2])

# Shader that handles two textures
class DoubleTextureTransformShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 330

            uniform mat4 transform;

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 330
            
            // gl_FragCoord contains the (x,y) fragment coordinates of the window.
            // We also set the origin to the upper left corner
            layout(origin_upper_left) in vec4 gl_FragCoord;
            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D upTexture;
            uniform sampler2D downTexture;
            uniform float mousePosY;

            void main()
            {
                vec4 finalColor;
                if ( gl_FragCoord.y > mousePosY){
                    finalColor = texture(downTexture, outTexCoords);
                }
                else {
                    finalColor = texture(upTexture, outTexCoords);
                }
                outColor = finalColor;
            }
            """

        # Binding artificial vertex array object for validation
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)

        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))


    def setupVAO(self, gpuShape):

        glBindVertexArray(gpuShape.vao)

        glBindBuffer(GL_ARRAY_BUFFER, gpuShape.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, gpuShape.ebo)

        # 3d vertices + 2d texture coordinates => 3*4 + 2*4 = 20 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        texCoords = glGetAttribLocation(self.shaderProgram, "texCoords")
        glVertexAttribPointer(texCoords, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(3 * SIZE_IN_BYTES))
        glEnableVertexAttribArray(texCoords)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, gpuShape, mode=GL_TRIANGLES):
        assert isinstance(gpuShape, TexGPUShape)

        glBindVertexArray(gpuShape.vao)
        # Binding the first texture
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        # Binding the second texture
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture2)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)
        

# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True
        self.mousePos = (0.0, 0.0)

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

def cursor_pos_callback(window, x, y):
    global controller
    controller.mousePos = (x,y)

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit(1)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Double binding", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    glfw.set_cursor_pos_callback(window, cursor_pos_callback)

    # A simple shader program with position and texture coordinates as inputs.
    pipeline = DoubleTextureTransformShaderProgram()
    
    # Telling OpenGL to use our shader program

    # Setting up the clear screen color
    glClearColor(0.25, 0.25, 0.25, 1.0)

    # Creating shapes on GPU memory
    shape = bs.createTextureQuad(1, 1)
    gpuShape = TexGPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    gpuShape.texture = es.textureSimpleSetup(
        getAssetPath("torres-del-paine-sq.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    gpuShape.texture2 = es.textureSimpleSetup(
        getAssetPath("red_woodpecker.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)

    currentMousePos = [width/2, height/2]

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        theta = 0.3 * np.sin(glfw.get_time())

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(pipeline.shaderProgram)
        # Drawing the shapes        
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE,
            np.matmul(
                tr.shearing(0,theta,0,0,0,0),
                tr.uniformScale(1.5)
            )
        )
        
        # Binding samplers to both texture units
        glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "upTexture"), 0)
        glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "downTexture"), 1)

        # Sending the mouse vertical location to our shader
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "mousePosY"), controller.mousePos[1])
        pipeline.drawCall(gpuShape)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)
    
    # freeing GPU memory
    gpuShape.clear()

    glfw.terminate()
