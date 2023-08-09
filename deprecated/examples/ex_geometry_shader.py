# coding=utf-8
"""Geometry Shader Basic Example

Adapted from: https://learnopengl.com/code_viewer_gh.php?code=src/4.advanced_opengl/9.1.geometry_shader_houses/geometry_shader_houses.cpp
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np

__author__ = "Daniel Calderon"
__license__ = "MIT"


# We will use 32 bits data, so floats and integers have 4 bytes
# 1 byte = 8 bits
SIZE_IN_BYTES = 4


# A class to store the application control
class Controller:
    fillPolygon = True


# we will use the global controller as communication with the callback function
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


def createShaderProgram():

    # Defining shaders for our pipeline
    vertex_shader = """
    #version 330 core
    layout (location = 0) in vec2 aPos;
    layout (location = 1) in vec3 aColor;

    out VS_OUT {
        vec3 color;
    } vs_out;

    void main()
    {
        vs_out.color = aColor;
        gl_Position = vec4(aPos.x, aPos.y, 0.0, 1.0); 
    }
    """

    geometry_shader = """
    #version 330 core
    layout (points) in;
    layout (triangle_strip, max_vertices = 4) out;

    in VS_OUT {
        vec3 color;
    } gs_in[];

    out vec3 fColor;

    vec3 blueish(in vec3 color)
    {
        vec3 outColor = color;
        outColor.r -= 0.5;
        outColor.g -= 0.5;
        outColor.b += 0.5;
        outColor = clamp(outColor, 0.0, 1.0);
        return outColor;
    }

    vec3 yellowish(in vec3 color)
    {
        vec3 outColor = color;
        outColor.r += 0.5;
        outColor.g += 0.5;
        outColor.b -= 0.5;
        outColor = clamp(outColor, 0.0, 1.0);
        return outColor;
    }

    void niceQuad(in vec4 position)
    {
        vec3 color = gs_in[0].color; // gs_in[0] since there's only one input vertex

        gl_Position = position + vec4(-0.2, -0.2, 0.0, 0.0); // 1:bottom-left
        fColor = vec3(1.0, 1.0, 1.0);
        EmitVertex();

        gl_Position = position + vec4( 0.2, -0.2, 0.0, 0.0); // 2:bottom-right
        fColor = blueish(color);
        EmitVertex();

        gl_Position = position + vec4(-0.2,  0.2, 0.0, 0.0); // 3:top-left
        fColor = yellowish(color);
        EmitVertex();

        gl_Position = position + vec4( 0.2,  0.2, 0.0, 0.0); // 4:top-right
        fColor = vec3(0.0, 0.0, 0.0);
        EmitVertex();

        EndPrimitive();
    }

    void main() {    
        niceQuad(gl_in[0].gl_Position);
    }
    """

    fragment_shader = """
    #version 330 core
    out vec4 FragColor;

    in vec3 fColor;

    void main()
    {
        FragColor = vec4(fColor, 1.0);   
    }
    """

    # Binding artificial vertex array object for validation
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)


    # Assembling the shader program (pipeline) with both shaders
    shaderProgram = OpenGL.GL.shaders.compileProgram(
        OpenGL.GL.shaders.compileShader(vertex_shader, GL_VERTEX_SHADER),
        OpenGL.GL.shaders.compileShader(geometry_shader, GL_GEOMETRY_SHADER),
        OpenGL.GL.shaders.compileShader(fragment_shader, GL_FRAGMENT_SHADER))

    return shaderProgram


def createGPUPoints():

    # Defining locations and colors for each vertex
    
    vertexData = np.array([
    #   positions    colors
        -0.5,  0.5, 1.0, 0.0, 0.0, # top-left
         0.5,  0.5, 0.0, 1.0, 0.0, # top-right
         0.5, -0.5, 0.0, 0.0, 1.0, # bottom-right
        -0.5, -0.5, 1.0, 1.0, 0.0  # bottom-left
    # It is important to use 32 bits data
        ], dtype = np.float32)

    size = len(vertexData) // 5

    # VAO, VBO and EBO and  for the shape
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    # binding the generated vao
    glBindVertexArray(vao)

    # Vertex data must be attached to a Vertex Buffer Object (VBO)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, len(vertexData) * SIZE_IN_BYTES, vertexData, GL_STATIC_DRAW)
    
    # position
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 5 * SIZE_IN_BYTES, ctypes.c_void_p(0))

    # color
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 5 * SIZE_IN_BYTES, ctypes.c_void_p(2 * SIZE_IN_BYTES))

    # unbinding current vao
    glBindVertexArray(0)

    return vao, vbo, size


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "Enter Geometry Shader", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)
    
    # Creating our shader program and telling OpenGL to use it
    shaderProgram = createShaderProgram()
    glUseProgram(shaderProgram)

    # Creating shapes on GPU memory
    vao, vbo, size = createGPUPoints()

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    while not glfw.window_should_close(window):
        # Using GLFW to check for input events
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Drawing: binding the VAO and executing the draw call...
        glBindVertexArray(vao)
        glDrawArrays(GL_POINTS, 0, size)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    glDeleteBuffers(1, [vbo])
    glDeleteVertexArrays(1, [vao])

    glfw.terminate()
