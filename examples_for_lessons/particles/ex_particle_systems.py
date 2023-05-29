import os
import sys
from collections import deque
from itertools import chain
from pathlib import Path

import numpy as np
import OpenGL.GL.shaders as shaders
import pyglet
from OpenGL.GL import (
    GL_BLEND,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_PROGRAM_POINT_SIZE,
    GL_SRC_ALPHA,
    glBlendFunc,
    glDisable,
    glEnable,
)
from pyglet.graphics.shader import Shader, ShaderProgram

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
)


import grafica.transformations as tr


class Particle(object):
    def __init__(self, position, ttl):
        self.position = np.array(position, dtype=np.float32)
        self.ttl = ttl
        self.velocity = np.array([0, -50, 0], dtype=np.float32)

    def step(self, dt):
        self.ttl = self.ttl - dt
        # método de Euler
        self.position = self.position + dt * self.velocity

    def alive(self):
        return bool(self.ttl > 0)


if __name__ == "__main__":
    width = 600
    height = 600

    with open(Path(os.path.dirname(__file__)) / "point_vertex_program.glsl") as f:
        vertex_program = f.read()

    with open(Path(os.path.dirname(__file__)) / "point_fragment_program.glsl") as f:
        fragment_program = f.read()

    win = pyglet.window.Window(width, height)

    vert_shader = Shader(vertex_program, "vertex")
    frag_shader = Shader(fragment_program, "fragment")
    pipeline = ShaderProgram(vert_shader, frag_shader)

    projection = tr.ortho(-300.0, 300.0, -300.0, 300.0, 0.001, 10.0)

    view = tr.lookAt(
        np.array([300.0, 300.0, 1.0]), # posición de la cámara
        np.array([300.0, 300.0, 0.0]), # hacia dónde apunta
        np.array([0.0, 1.0, 0.0]),     # vector para orientarla (arriba)
    )

    pipeline.use()
    # ojo! OpenGL usa column major, pero numpy usa row major.
    # por eso antes le pasábamos un parámetro GL_TRUE a la opción traspose
    # aquí el parámetro order='F' indica que es row major
    # (así lo espera pyglet para entregarlo a OpenGL)
    pipeline["projection"] = projection.reshape(16, 1, order="F")
    pipeline["view"] = view.reshape(16, 1, order="F")
    pipeline["max_ttl"] = 3

    # nuestra colección de partículas.
    # ¿por qué es una deque (cola)?
    win.particles = deque()
    # los datos que tendremos en la GPU. los gestionaremos con pyglet
    win.particle_data = None
    
    def add_particle(x, y):
        win.particles.append(Particle((x, y, 0.0), 3))

    @win.event
    def on_draw():
        win.clear()
        glEnable(GL_PROGRAM_POINT_SIZE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        pipeline.use()
        if win.particle_data is not None:
            win.particle_data.draw(pyglet.gl.GL_POINTS)

    @win.event
    def on_mouse_motion(x, y, dx, dy):
        add_particle(x, y)

    def update_particle_system(dt, win):
        to_remove = 0
        for i, p in enumerate(win.particles):
            p.step(dt)

            if not p.alive():
                to_remove += 1

        for i in range(to_remove):
            win.particles.popleft()

        if win.particle_data is not None:
            win.particle_data.delete()
            win.particle_data = None

        if len(win.particles) > 0:
            win.particle_data = pipeline.vertex_list(
                len(win.particles), pyglet.gl.GL_POINTS, position="f", ttl="f"
            )
            win.particle_data.position[:] = tuple(
                chain(*(p.position for p in win.particles))
            )
            win.particle_data.ttl[:] = tuple(p.ttl for p in win.particles)

    pyglet.clock.schedule(update_particle_system, win)
    pyglet.app.run()
