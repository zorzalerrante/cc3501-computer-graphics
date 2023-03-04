import pyglet
from OpenGL.GL import *

import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))

import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr


""" 
When pressing the arrows, the quad performs a translation.
When pressing space, the quad stops rotating.

The base for interactive programs and movements in applications is to bind key events
to a transformation.
"""

class Controller(pyglet.window.Window):

    def __init__(self):
        super().__init__()
        # model related
        self.fillPolygon = True
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.rotate = True

    def update_quad(self, dt):
        if self.rotate:
            self.theta += dt


window = Controller()
pipeline = es.SimpleTransformShaderProgram()
glUseProgram(pipeline.shaderProgram)
glClearColor(0.5, 0.5, 0.5, 1.0)

shapeQuad = bs.createRainbowQuad()
gpuQuad = es.GPUShape().initBuffers()
pipeline.setupVAO(gpuQuad)
gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)
glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

# Happens when pressing a key
@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        window.rotate = not window.rotate
    elif symbol == pyglet.window.key.LEFT:
        window.x -= 0.1
    elif symbol == pyglet.window.key.RIGHT:
        window.x += 0.1
    elif symbol == pyglet.window.key.UP:
        window.y += 0.1
    elif symbol == pyglet.window.key.DOWN:
        window.y -= 0.1
    elif symbol == pyglet.window.key.ESCAPE:
        window.close()

def update_background(dt):
    glClearColor(*np.random.random(4))

# When rendering to window
@window.event
def on_draw():
    window.clear()
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glUniformMatrix4fv(
        glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
            tr.translate(window.x, window.y, 0.0),
            tr.rotationZ(window.theta)
        ))
    pipeline.drawCall(gpuQuad)


pyglet.clock.schedule(window.update_quad)  # Execute update_quad constantly (ideally 60 times per second)
pyglet.app.run()
