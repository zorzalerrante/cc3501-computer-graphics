from OpenGL.GL import *

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
from grafica.easy_shaders import GPUShape 
from grafica.basic_shapes import Shape

# Creating shapes on GPU memory
def createGPUShape(pipeline, shape):
    gpuShape = GPUShape().initBuffers()
    pipeline.setupVAO(gpuShape)
    gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
    return gpuShape


class HighLevelGPUShape:

    def __init__(self, pipeline, shape: Shape):
        self._rotation = tr.identity()
        self._translation = tr.identity()
        self._scale = tr.identity()
        self._transform = tr.identity()
        self._GPUShape = createGPUShape(pipeline, shape)

    def _update_transform(self):
        self._transform = self._translation @ self._rotation @ self._scale
    
    @property
    def translation(self):
        return self._translation

    @translation.setter
    def translation(self, value):
        self._translation = value
        self._update_transform()

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self._update_transform()

    @property
    def rotation(self):
        return self._rotation

    @rotation.setter
    def rotation(self, value):
        self._rotation = value
        self._update_transform()

    def draw(self, pipeline):
        # TODO: assert that pipeline has transform uniform
        glUniformMatrix4fv(
            glGetUniformLocation(pipeline.shaderProgram, "transform"),
            1,
            GL_TRUE,
            self._transform,
        )
        pipeline.drawCall(self._GPUShape)

