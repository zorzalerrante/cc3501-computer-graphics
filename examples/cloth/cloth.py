import os
import sys
from itertools import chain
from pathlib import Path

import numpy as np
import pyglet

from pyglet.graphics.shader import Shader, ShaderProgram
from cloth_utils import Cloth
from pyglet.math import Vec2

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
)


import grafica.transformations as tr

if __name__ == "__main__":
    width, height = 1920, 1080
    horizontal_resolution = 80
    vertical_resolution = 50
    spacing = 15

    half_width = width // 2
    half_height = height // 2

    with open(Path(os.path.dirname(__file__)) / "point_vertex_program.glsl") as f:
        vertex_program = f.read()

    with open(Path(os.path.dirname(__file__)) / "point_fragment_program.glsl") as f:
        fragment_program = f.read()

    win = pyglet.window.Window(width, height)

    vert_shader = Shader(vertex_program, "vertex")
    frag_shader = Shader(fragment_program, "fragment")
    pipeline = ShaderProgram(vert_shader, frag_shader)

    projection = tr.ortho(
        -half_width, half_width, -half_height, half_height, 0.001, 10.0
    )

    view = tr.lookAt(
        np.array([half_width, half_height, 1.0]),  # posición de la cámara
        np.array([half_width, half_height, 0.0]),  # hacia dónde apunta
        np.array([0.0, 1.0, 0.0]),  # vector para orientarla (arriba)
    )

    pipeline.use()
    pipeline["projection"] = projection.reshape(16, 1, order="F")
    pipeline["view"] = view.reshape(16, 1, order="F")

    win.cloth = Cloth(
        width, height, Vec2(half_width - horizontal_resolution * spacing // 2, height * 0.95), horizontal_resolution, vertical_resolution, spacing
    )

    win.node_data = pipeline.vertex_list(
        len(win.cloth.vertices), pyglet.gl.GL_POINTS, position="f"
    )

    win.joint_data = pipeline.vertex_list_indexed(
        len(win.cloth.vertices),
        pyglet.gl.GL_LINES,
        tuple(chain(*(j for j in win.cloth.joints))),
        position="f",
    )

    def update_cloth_system(dt, win):
        win.cloth.update(dt)

    @win.event
    def on_draw():
        win.clear()
        
        win.node_data.position[:] = tuple(
            chain(*((p.position[0], p.position[1], 0.0) for p in win.cloth.vertices))
        )

        win.joint_data.position[:] = tuple(
            chain(*((p.position[0], p.position[1], 0.0) for p in win.cloth.vertices))
        )

        pipeline.use()
        win.node_data.draw(pyglet.gl.GL_POINTS)
        win.joint_data.draw(pyglet.gl.GL_LINES)


    pyglet.clock.schedule(update_cloth_system, win)
    pyglet.app.run()
