import numpy as np
import pyglet
from itertools import chain
import OpenGL.GL as GL
from pathlib import Path
import os


class Grid(object):
    def __init__(self, grid_resolution=100):
        self.grid_resolution = grid_resolution
        xv, yv = np.meshgrid(
            np.linspace(-1, 1, grid_resolution),
            np.linspace(-1, 1, grid_resolution),
            indexing="xy",
        )

        self.grid_vertices = np.vstack(
            (
                xv.reshape(1, -1),
                yv.reshape(1, -1),
                np.zeros(shape=(1, grid_resolution**2)),
            )
        ).T

        self.grid_indices = [
            [
                (grid_resolution * row + i, grid_resolution * row + i + 1)
                for i in range(grid_resolution - 1)
            ]
            for row in range(grid_resolution)
        ]

        self.grid_indices.extend(
            [
                [
                    (
                        grid_resolution * column + i,
                        grid_resolution * column + i + grid_resolution,
                    )
                    for i in range(grid_resolution)
                ]
                for column in range(grid_resolution - 1)
            ]
        )

        self.grid_indices = list(chain(*chain(*self.grid_indices)))
        self.setup_program()

    def setup_program(self):
        with open(
            Path(os.path.dirname(__file__))
            / ".."
            / "hello_box2d"
            / "vertex_program.glsl"
        ) as f:
            vertex_source_code = f.read()

        with open(
            Path(os.path.dirname(__file__))
            / ".."
            / "hello_box2d"
            / "fragment_program.glsl"
        ) as f:
            fragment_source_code = f.read()

        vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
        self.pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
        self.grid_gpu = self.pipeline.vertex_list_indexed(
            self.grid_resolution**2, GL.GL_LINES, self.grid_indices
        )

        self.grid_gpu.position[:] = self.grid_vertices.reshape(-1, 1, order="C")

    def draw(self, transform):
        self.pipeline.use()
        self.pipeline["transform"] = transform.reshape(16, 1, order="F")

        self.grid_gpu.draw(GL.GL_LINES)
