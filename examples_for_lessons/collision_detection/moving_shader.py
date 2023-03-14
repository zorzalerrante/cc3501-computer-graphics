from OpenGL.GL import *
import OpenGL.GL.shaders

import grafica.easy_shaders as es


class MovingShader2D(es.SimpleTextureTransformShaderProgram):
    """ Moves everything considering the position of the player by applying a translation """

    def __init__(self):

        vertex_shader = """
            #version 330

            uniform mat4 transform;
            uniform mat4 playerPosition; // playerPosition is a translation

            in vec3 position;
            in vec2 texCoords;

            out vec2 outTexCoords;

            void main()
            {
                gl_Position = transform * playerPosition * vec4(position, 1.0f);
                outTexCoords = texCoords;
            }
            """

        fragment_shader = """
            #version 330

            in vec2 outTexCoords;

            out vec4 outColor;

            uniform sampler2D samplerTex;

            void main()
            {
                outColor = texture(samplerTex, outTexCoords);
            }
            """

        # Binding artificial vertex array object for validation
        VAO = glGenVertexArrays(1)
        glBindVertexArray(VAO)


        # Compiling our shader program
        self.shaderProgram = OpenGL.GL.shaders.compileProgram(
            OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
            OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))
