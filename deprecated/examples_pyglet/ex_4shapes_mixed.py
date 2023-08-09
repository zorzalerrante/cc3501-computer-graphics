# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import pyglet
from OpenGL.GL import *

from math import cos, sin

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from grafica import basic_shapes as bs
from grafica import easy_shaders as es
from grafica import transformations as tr
from shapes_utils import HighLevelGPUShape, createGPUShape

class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="Pyglet window"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True
        self.pipeline = None
        self.repeats = 0

# We will use the global controller as communication with the callback function
WIDTH, HEIGHT = 1280, 800
controller = Controller(width=WIDTH, height=HEIGHT)
# Setting up the clear screen color
glClearColor(0.15, 0.15, 0.15, 1.0)

# Setting the model (data of our code)
# Creating our shader program and telling OpenGL to use it
pipeline = es.SimpleTransformShaderProgram()
controller.pipeline = pipeline
glUseProgram(pipeline.shaderProgram)

gpuTriangle = HighLevelGPUShape(pipeline, bs.createRainbowTriangle())
gpuQuad = HighLevelGPUShape(pipeline, bs.createRainbowQuad())


# This function will be executed approximately 60 times per second
# dt is the time between the last time it was executed and now
def draw_translated_quad(controller: Controller):
    gpuQuad.scale = tr.uniformScale(0.8)
    gpuQuad.translation = tr.translate(
        0.5 + 0.1 * cos(controller.total_time * 6.0),
        0.5 + 0.1 * sin(controller.total_time * 6.0),
        0.0
    )
    gpuQuad.draw(controller.pipeline)

def draw_scalating_quad(controller: Controller):
    gpuQuad.scale = tr.uniformScale(0.5 * sin(controller.total_time))
    gpuQuad.translation = tr.translate(-0.5, -0.5, 0.0)
    gpuQuad.draw(controller.pipeline)

# This function will be executed approximately 60 times per second
# dt is the time between the last time it was executed and now
def draw_shearing_triangle(controller: Controller):
    gpuTriangle._transform = tr.matmul([
        tr.translate(0.5, -0.5, 0),
        tr.shearing(0.3 * sin(controller.total_time), 0, 0, 0, 0, 0),
        tr.uniformScale(0.7)
    ])
    gpuTriangle.draw(controller.pipeline)

def draw_rotating_triangle(controller: Controller):
    gpuTriangle._transform = tr.identity()  # Make the transform neutral again
    gpuTriangle.rotation = tr.rotationZ(controller.total_time)
    gpuTriangle.translation = tr.translate(-0.5, 0.5, 0.0)
    gpuTriangle.scale = tr.uniformScale(0.3)
    gpuTriangle.draw(controller.pipeline)

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
    draw_translated_quad(controller)
    draw_scalating_quad(controller)
    draw_shearing_triangle(controller)
    draw_rotating_triangle(controller)

# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
# We could also create 2 different gpuQuads and different transform for each
# one, but this would use more memory
def update(dt, controller):
    controller.total_time += dt

# Try to call this function 60 times per second
pyglet.clock.schedule(update, controller)
# Set the view
pyglet.app.run()
