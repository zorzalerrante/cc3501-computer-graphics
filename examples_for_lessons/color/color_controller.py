import pyglet
from pyglet.window import key

from OpenGL.GL import *

import numpy as np
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.transformations as tr


class Controller(pyglet.window.Window):

    def __init__(
            self,
            rows = 8,
            columns = 8,
            background_color=(0.0, 0.0, 0.0)
    ):
        super().__init__()
        # model related
        self.fillPolygon = True
        self.rows = rows
        self.cols = columns
        self.background_color = background_color

        # Setup
        self.pipeline = es.SimpleTransformShaderProgram()
        glUseProgram(self.pipeline.shaderProgram)
        
        self.quads = np.zeros(shape=(rows, columns, 3), dtype=float)
        self.gpuQuads = np.zeros(shape=(rows, columns), dtype=es.GPUShape)
        self.set_random_colors()
        self.update_colors()
   

    def set_random_colors(self):
        for i in range(len(self.gpuQuads)):
            for j in range(len(self.gpuQuads[0])):
                self.quads[i, j, :] = np.random.rand(3)

    def update_colors(self):
        for i in range(len(self.gpuQuads)):
            for j in range(len(self.gpuQuads[0])):
                shapeQuad = bs.createColorQuad(*self.quads[i, j, :])
                self.gpuQuads[i, j] = es.GPUShape().initBuffers()
                self.pipeline.setupVAO(self.gpuQuads[i, j])
                self.gpuQuads[i, j].fillBuffers(shapeQuad.vertices, shapeQuad.indices, GL_STATIC_DRAW)        

    def draw_quads(self):
        SCALE_FACTOR_X = 2.0 / self.rows
        SCALE_FACTOR_Y = 2.0 / self.cols
        delta = 0.01 # So lines can be appreciated
        for i in range(len(self.gpuQuads)):
            for j in range(len(self.gpuQuads[0])):
                translation = tr.translate(1.0 / self.rows + (SCALE_FACTOR_X + delta) * (i - self.rows/2),
                                           1.0 / self.cols + (SCALE_FACTOR_Y + delta) * (self.cols / 2 - j - 1),
                                           0.0
                                           )
                glUniformMatrix4fv(
                    glGetUniformLocation(self.pipeline.shaderProgram, "transform"), 
                    1,
                    GL_TRUE,
                    tr.matmul([
                        translation,
                        tr.scale(SCALE_FACTOR_X, SCALE_FACTOR_Y, 1.0),
                    ])
                )
                self.pipeline.drawCall(self.gpuQuads[i, j])

    def set_color_for_quad(self, i, j, r, g, b):
        self.quads[i, j, :] = r, g, b

    def __getitem__(self, index):
        """ Index should be of the type (0, 1) or [0, 1]
        So this object is accessed with controller[0, 0]
        """
        try:
            assert(type(index[0]) == int and index[1] == int)
            return self.quads[index[0]], [index[1]]

        except AssertionError:
            raise("Indexes must be two integers")

    def __setitem__(self, index, value):
        """ Index should be of the type (0, 1) or [0, 1]
        So this object is accessed with controller[0, 0]
        """
        r, g, b = value
        self.quads[index[0], index[1], :] = r, g, b

    ## EVENTS ##

    # Triggered when pressing a key
    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.fillPolygon = not self.fillPolygon
        elif symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_draw(self):
        self.clear()
        glClearColor(*self.background_color, 1.0)
        if self.fillPolygon:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        self.draw_quads()
