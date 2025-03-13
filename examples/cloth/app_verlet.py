import os
import sys
from itertools import chain
from pathlib import Path

import numpy as np
import pyglet
import click

from pyglet.graphics.shader import Shader, ShaderProgram
from .cloth_utils import Cloth
from pyglet.math import Vec2


from grafica.utils import load_pipeline
import grafica.transformations as tr


@click.command("cloth_verlet", short_help='Simulación de tela usando una implementación ingenua de integración de Verlet')
@click.option("--width", type=int, default=1920)
@click.option("--height", type=int, default=1080)
@click.option("--vertical_resolution", type=int, default=30)
@click.option("--horizontal_resolution", type=int, default=60)
@click.option("--spacing", type=int, default=15)
def cloth_verlet(width, height, vertical_resolution, horizontal_resolution, spacing):
    half_width = width // 2
    half_height = height // 2

    win = pyglet.window.Window(width, height)

    pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "point_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "point_fragment_program.glsl",
    )

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
        width,
        height,
        Vec2(half_width - horizontal_resolution * spacing // 2, height * 0.95),
        horizontal_resolution,
        vertical_resolution,
        spacing,
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
