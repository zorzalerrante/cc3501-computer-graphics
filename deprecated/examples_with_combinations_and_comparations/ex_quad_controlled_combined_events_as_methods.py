import pyglet
from pyglet.window import key

from OpenGL.GL import *

import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr


class Controller(pyglet.window.Window):

    def __init__(self):
        super().__init__()
        # model related
        self.fillPolygon = True
        self.x = 0.0
        self.y = 0.0
        self.theta = 0.0
        self.rotate = True

        # Setup
        self.pipeline = es.SimpleTransformShaderProgram()
        glUseProgram(self.pipeline.shaderProgram)

        shapeQuad = bs.createRainbowQuad()
        self.gpuQuad = es.GPUShape().initBuffers()
        self.pipeline.setupVAO(self.gpuQuad)
        self.gpuQuad.fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)


    # Controller related
    def on_key_press(self, symbol, modifiers):
        if symbol == key.SPACE:
            self.rotate = not self.rotate
        elif symbol == key.LEFT:
            self.x -= 0.1
        elif symbol == key.RIGHT:
            self.x += 0.1
        elif symbol == key.UP:
            self.y += 0.1
        elif symbol == key.DOWN:
            self.y -= 0.1
        elif key == key.ESCAPE:
           self.close()
            
    def on_draw(self):
        self.clear()
        glUniformMatrix4fv(glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 1, GL_TRUE, np.matmul(
                tr.translate(controller.x, controller.y, 0.0),
                tr.rotationZ(controller.theta)
            ))
        self.pipeline.drawCall(self.gpuQuad)

    def update_quad(self, dt):
        if self.rotate:
            self.theta += dt


if __name__ == "__main__":
    controller = Controller()
    pyglet.clock.schedule_interval(controller.update_quad, 1/30)
    pyglet.app.run()
