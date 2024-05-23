import os
import sys
from itertools import chain
from pathlib import Path

import numpy as np
import pyglet

from pyglet.graphics.shader import Shader, ShaderProgram
from cloth_utils import Cloth
from pyglet.math import Vec2

import pymunk

if sys.path[0] != "":
    sys.path.insert(0, "")

from grafica.utils import load_pipeline
import grafica.transformations as tr

if __name__ == "__main__":
    width, height = 1920, 1080
    horizontal_resolution = 60
    vertical_resolution = 30
    spacing = 15

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

    space = pymunk.Space()

    space.gravity = (0, -9800)
    space.damping = 0.999

    bodies = {}
    cloth_group = 1

    for i, vertex in enumerate(win.cloth.vertices):
        # los convertimos de pyglet a pymunk
        if i in (0, horizontal_resolution // 2, horizontal_resolution - 1):
            b = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            b = pymunk.Body(4, 0.1)

        b.position = pymunk.Vec2d(vertex.position.x, vertex.position.y)

        s = pymunk.Circle(b, 15)
        # la ropa NO colisionará consigo misma. solo se considerarán los resortes
        s.filter = pymunk.ShapeFilter(group=cloth_group)
        space.add(b, s)
        bodies[i] = b

    win.bodies = bodies

    for joint in win.cloth.joints:
        a = bodies[joint[0]]
        b = bodies[joint[1]]
        j = pymunk.DampedSpring(
            a,
            b,
            (0, 0),
            (0, 0),
            rest_length=a.position.get_distance(b.position),
            stiffness=50000.0,
            damping=100,
        )
        space.add(j)

    def update_cloth_system(dt, win):
        # lo recomendable es que no dependa de dt. que sea fijo, por estabilidad
        r = 10
        space.step(dt / r)

    @win.event
    def on_draw():
        win.clear()

        win.node_data.position[:] = tuple(
            chain(*((p.position.x, p.position.y, 0.0) for p in win.bodies.values()))
        )

        win.joint_data.position[:] = tuple(
            chain(*((p.position.x, p.position.y, 0.0) for p in win.bodies.values()))
        )

        pipeline.use()
        win.node_data.draw(pyglet.gl.GL_POINTS)
        win.joint_data.draw(pyglet.gl.GL_LINES)

    pyglet.clock.schedule(update_cloth_system, win)
    pyglet.app.run()
