# coding=utf-8
"""
Simple example using ImGui with GLFW and OpenGL

More info at:
https://pypi.org/project/imgui/

Installation:
pip install imgui[glfw]

Another example:
https://github.com/swistakm/pyimgui/blob/master/doc/examples/integrations_glfw3.py#L2
"""

import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import random
import imgui
from imgui.integrations.glfw import GlfwRenderer
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica.gpu_shape import GPUShape
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr

__author__ = "Daniel Calderon"
__license__ = "MIT"


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


def transformGuiOverlay(locationX, locationY, angle, color):

    # start new frame context
    imgui.new_frame()

    # open new window context
    imgui.begin("2D Transformations control", False, imgui.WINDOW_ALWAYS_AUTO_RESIZE)

    # draw text label inside of current window
    imgui.text("Configuration sliders")

    edited, locationX = imgui.slider_float("location X", locationX, -1.0, 1.0)
    edited, locationY = imgui.slider_float("location Y", locationY, -1.0, 1.0)
    edited, angle = imgui.slider_float("Angle", angle, -np.pi, np.pi)
    edited, color = imgui.color_edit3("Modulation Color", color[0], color[1], color[2])
    if imgui.button("Random Modulation Color!"):
        color = (random.uniform(0.0, 1.0), random.uniform(0.0, 1.0), random.uniform(0.0, 1.0))
    imgui.same_line()
    if imgui.button("White Modulation Color"):
        color = (1.0, 1.0, 1.0)

    global controller
    edited, checked = imgui.checkbox("wireframe", not controller.fillPolygon)
    if edited:
        controller.fillPolygon = not checked

    # close current window context
    imgui.end()

    # pass all drawing comands to the rendering pipeline
    # and close frame context
    imgui.render()
    imgui.end_frame()

    return locationX, locationY, angle, color


class ModulationTransformShaderProgram:

    def __init__(self):

        vertex_shader = """
            #version 330
            
            uniform mat4 transform;

            in vec3 position;
            in vec3 color;

            out vec3 newColor;

            void main()
            {
                gl_Position = transform * vec4(position, 1.0f);
                newColor = color;
            }
            """

        fragment_shader = """
            #version 330

            in vec3 newColor;
            out vec4 outColor;

            uniform vec3 modulationColor;

            void main()
            {
                outColor = vec4(modulationColor, 1.0f) * vec4(newColor, 1.0f);
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

        # 3d vertices + rgb color specification => 3*4 + 3*4 = 24 bytes
        position = glGetAttribLocation(self.shaderProgram, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)
        
        color = glGetAttribLocation(self.shaderProgram, "color")
        glVertexAttribPointer(color, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        glEnableVertexAttribArray(color)

        # Unbinding current vao
        glBindVertexArray(0)


    def drawCall(self, shape, mode=GL_TRIANGLES):
        assert isinstance(shape, GPUShape)

        # Binding the VAO and executing the draw call
        glBindVertexArray(shape.vao)
        glDrawElements(mode, shape.size, GL_UNSIGNED_INT, None)
        
        # Unbind the current VAO
        glBindVertexArray(0)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "GLFW OpenGL ImGui", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Creating our shader program and telling OpenGL to use it
    pipeline = ModulationTransformShaderProgram()
    glUseProgram(pipeline.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.15, 0.15, 0.15, 1.0)

    # Creating shapes on GPU memory
    shapeQuad = bs.createRainbowQuad()
    gpuQuad = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuQuad)
    gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)


    # initilize imgui context (see documentation)
    imgui.create_context()
    impl = GlfwRenderer(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    # It is important to set the callback after the imgui setup
    glfw.set_key_callback(window, on_key)

    locationX = 0.0
    locationY = 0.0
    angle = 0.0
    color = (1.0, 1.0, 1.0)

    while not glfw.window_should_close(window):

        impl.process_inputs()
        # Using GLFW to check for input events

        # Poll and handle events (inputs, window resize, etc.)
        # You can read the io.WantCaptureMouse, io.WantCaptureKeyboard flags to tell if dear imgui wants to use your inputs.
        # - When io.want_capture_mouse is true, do not dispatch mouse input data to your main application.
        # - When io.want_capture_keyboard is true, do not dispatch keyboard input data to your main application.
        # Generally you may always pass all inputs to dear imgui, and hide them from your application based on those two flags.
        # io = imgui.get_io()
        #print(io.want_capture_mouse, io.want_capture_keyboard)
        glfw.poll_events()

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # imgui function
        impl.process_inputs()

        locationX, locationY, angle, color = \
            transformGuiOverlay(locationX, locationY, angle, color)

        # Setting uniforms and drawing the Quad
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE,
            np.matmul(
                tr.translate(locationX, locationY, 0.0),
                tr.rotationZ(angle)
            )
        )
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "modulationColor"),
            color[0], color[1], color[2])
        pipeline.drawCall(gpuQuad)

        # Drawing the imgui texture over our drawing
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        impl.render(imgui.get_draw_data())

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuQuad.clear()

    impl.shutdown()
    glfw.terminate()
