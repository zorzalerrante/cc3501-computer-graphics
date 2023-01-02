# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import pyglet
from OpenGL.GL import *

from math import sin, cos

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica import basic_shapes as bs
from grafica import easy_shaders as es


class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="Pyglet window"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True


# We will use the global controller as communication with the callback function
WIDTH, HEIGHT = 1280, 800
controller = Controller(width=WIDTH, height=HEIGHT)

# Setting up the clear screen color
pyglet.gl.glClearColor(0.15, 0.15, 0.15, 1.0)

# Setting the model (data of our code)
   # Creating our shader program and telling OpenGL to use it
pipeline = es.SimpleTransformShaderProgram()
pyglet.gl.glUseProgram(pipeline.shaderProgram)

# Setting up the clear screen color
pyglet.gl.glClearColor(0.15, 0.15, 0.15, 1.0)




gpuTriangle = createGPUShape(pipeline, bs.createRainbowTriangle())

shapeQuad = bs.createRainbowQuad()
gpuQuad = es.GPUShape().initBuffers()
pipeline.setupVAO(gpuQuad)
gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, pyglet.gl.GL_STATIC_DRAW)


# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        controller.fillPolygon = not controller.fillPolygon
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()


@controller.event
def on_draw():
    controller.clear()


# # This function will be executed approximately 60 times per second
# # dt is the time between the last time it was executed and now
# def update_figures(dt: float, controller: Controller):
#     controller.total_time += dt
#     shape_quad1.rotation = 20.0 * controller.total_time
#     shape_triangle2.position = 100.0 + 100.0 * cos(controller.total_time), 100.0 + 100.0 * sin(controller.total_time)
#     shape_quad2.scale = 1.0 + 0.5 * sin(controller.total_time)

# pyglet.clock.schedule(update_figures, controller)
# Set the view
pyglet.app.run()
