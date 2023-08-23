# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import pyglet
from OpenGL.GL import *

from math import cos, sin

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from grafica import basic_shapes as bs
from grafica import easy_shaders as es
from grafica import transformations as tr


def createGPUShape(pipeline, shape):
    gpuShape = es.GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape

def apply_transform(pipeline, transform_matrix, shader_param_name="transform"):
    glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, shader_param_name), 1, GL_TRUE, transform_matrix)



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

gpuTriangle = createGPUShape(pipeline, bs.createRainbowTriangle())
gpuQuad = createGPUShape(pipeline, bs.createRainbowQuad())

# This function will be executed approximately 60 times per second
# dt is the time between the last time it was executed and now
def draw_translated_gpu_shape(pipeline, GPUShape: es.GPUShape, total_time):
    GPUShape_translation = tr.translate(
        0.5 + 0.1 * cos(total_time * 6.0),
        0.5 + 0.1 * sin(total_time * 6.0),
        0.0
    )
    GPUShape_scale = tr.uniformScale(0.8)
    final_transform = tr.matmul([
            GPUShape_translation,
            GPUShape_scale,
        ]
    )
    apply_transform(pipeline, final_transform)
    pipeline.drawCall(GPUShape)


def draw_scalating_gpu_shape(pipeline, GPUShape: es.GPUShape, total_time):
    GPUShape_translation = tr.translate(-0.5, -0.5, 0.0)
    GPUShape_scale = tr.uniformScale(0.5 * sin(total_time))
    final_transform = tr.matmul([
            GPUShape_translation,
            GPUShape_scale,
        ])
    apply_transform(pipeline, final_transform)
    pipeline.drawCall(GPUShape)


# This function will be executed approximately 60 times per second
# dt is the time between the last time it was executed and now
def draw_shearing_triangle(pipeline, GPUShape: es.GPUShape, total_time):
    GPUShape_translation = tr.translate(0.5, -0.5, 0)
    GPUShape_scale = tr.uniformScale(0.7)
    GPUShape_shearing = tr.shearing(0.3 * sin(total_time), 0, 0, 0, 0, 0)
    final_transform = tr.matmul([
            GPUShape_translation,
            GPUShape_scale,
            GPUShape_shearing,
        ])
    apply_transform(pipeline, final_transform)
    pipeline.drawCall(GPUShape)


def draw_rotating_triangle(pipeline, GPUShape: es.GPUShape, total_time):
    GPUShape_rotation = tr.rotationZ(total_time)
    GPUShape_translation = tr.translate(-0.5, 0.5, 0.0)
    GPUShape_scale = tr.uniformScale(0.3)
    final_transform = tr.matmul([
            GPUShape_translation,
            GPUShape_scale,
            GPUShape_rotation,
        ])
    apply_transform(pipeline, final_transform)
    pipeline.drawCall(GPUShape)


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
    draw_translated_gpu_shape(controller.pipeline, gpuQuad, controller.total_time)
    draw_scalating_gpu_shape(controller.pipeline, gpuQuad, controller.total_time)
    draw_shearing_triangle(controller.pipeline, gpuTriangle, controller.total_time)
    draw_rotating_triangle(controller.pipeline, gpuTriangle, controller.total_time)

# Each time update is called, on_draw is called again
# That is why it is better to draw and update each one in a separated function
def update(dt, controller):
    controller.total_time += dt

# Try to call this function 60 times per second
pyglet.clock.schedule(update, controller)
pyglet.app.run()
