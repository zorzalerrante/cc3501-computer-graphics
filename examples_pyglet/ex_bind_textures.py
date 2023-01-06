# coding=utf-8
"""Dibujando 2 texturas en un mismo Fragment Shader"""

from OpenGL.GL import *
import sys
import os.path
import pyglet
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
from grafica.assets_path import getAssetPath
import grafica.easy_shaders as es
from grafica.gpu_shape import GPUShape, SIZE_IN_BYTES, createGPUShape


# Nuevas clase para almacenar otra textura
class TwoTexturesGPUShape(GPUShape):
    def __init__(self, pipeline, vertices, indices, usage):
        """VAO, VBO, EBO and texture handlers to GPU memory.
        This GPUShape implements a second texture"""
        super().__init__()
        self.texture_2 = None
        super().initBuffers()
        super().fillBuffers(vertices, indices, usage)

    def __str__(self):
        return super().__str__() + "  tex=" + str(self.texture_2)

    def clear(self):
        """Freeing GPU memory"""
        if self.texture_2 != None:
            glDeleteTextures(1, [self.texture_2])
        super().clear()


# Shader para entregar dos texturas
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

            // Vector que contiene en las dos primeras componentes la posicion (x, y) del fragmento en la ventana
            // Con el origen en la esquina superior izquierda
            layout(origin_upper_left) in vec4 gl_FragCoord;
            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D upTexture;
            uniform sampler2D downTexture;
            uniform float mousePosY; // Recibe la posicion en Y del mouse

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

        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, OpenGL.GL.GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, OpenGL.GL.GL_FRAGMENT_SHADER))


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
        assert isinstance(gpuShape, TwoTexturesGPUShape)

        glBindVertexArray(gpuShape.vao)
        # Binding de la primera textura
        glActiveTexture(GL_TEXTURE0 + 0)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture)
        # Binding de la seguna textura
        glActiveTexture(GL_TEXTURE0 + 1)
        glBindTexture(GL_TEXTURE_2D, gpuShape.texture_2)

        glDrawElements(mode, gpuShape.size, GL_UNSIGNED_INT, None)

        # Unbind the current VAO
        glBindVertexArray(0)
        

# A class to store the application control
class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="Pyglet window"):
        super().__init__(width, height, title)
        self.width = width
        self.height = height
        self.fillPolygon = True
        self.mousePos = (0.0, 0.0)

# global controller as communication with the callback function
controller = Controller(width=800, height=800)



# A simple shader program with position and texture coordinates as inputs.
pipeline = DoubleTextureTransformShaderProgram()
shape = bs.createTextureQuad(1.0, 1.0)
gpuShape = TwoTexturesGPUShape(pipeline, shape.vertices, shape.indices, GL_STATIC_DRAW)
pipeline.setupVAO(gpuShape)  # This has to be done since this is another kind of GPUShape

# The two textures can have different properties
gpuShape.texture = es.textureSimpleSetup(
    getAssetPath("bricks.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
gpuShape.texture_2 = es.textureSimpleSetup(
    getAssetPath("boo.png"), GL_REPEAT, GL_REPEAT, GL_NEAREST, GL_NEAREST)

@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        controller.fillPolygon = not controller.fillPolygon
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()

@controller.event
def on_mouse_motion(x, y, dx, dy):
    controller.mousePos = (x, controller.height - y)
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.uniformScale(1.5))
    # Bindear los samplers a las unidades de texturas
    glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "upTexture"), 0)
    glUniform1i(glGetUniformLocation(pipeline.shaderProgram, "downTexture"), 1)
    # Posicion vertical del mouse
    glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "mousePosY"), controller.mousePos[1])

@controller.event
def on_draw():
    controller.clear()
    if (controller.fillPolygon):
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    else:
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    pipeline.drawCall(gpuShape)


glUseProgram(pipeline.shaderProgram)
# Set the view
pyglet.app.run()
