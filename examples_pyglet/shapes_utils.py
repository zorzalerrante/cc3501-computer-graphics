from OpenGL.GL import *

import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
from grafica.gpu_shape import createGPUShape


class HighLevelGPUShape:
    """
    This GPUShape allows to apply transformation very easily, by just changing
    properties such as rotation, translation or scale.
    Example:

    pipeline = es.SimpleTransformShaderProgram()
    gpuTriangle = HighLevelGPUShape(pipeline, bs.createRainbowTriangle())
    gpuQuad.scale = tr.uniformScale(0.8)
    gpuQuad.translation = tr.translate(0.5, 0.5, 0.0)
    gpuQuad.draw(pipeline)
    
    The given pipeline must have an uniform mat4 value called transform.
    """
    def __init__(self, pipeline, shape: bs.Shape):
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

    def draw(self, pipeline, transform_shader_param="transform"):
        # TODO: assert that pipeline has transform uniform
        glUniformMatrix4fv(
            glGetUniformLocation(pipeline.shaderProgram, transform_shader_param),
            1,
            GL_TRUE,
            self._transform,
        )
        pipeline.drawCall(self._GPUShape)

