import os
import sys
from collections import deque
from itertools import chain
from pathlib import Path

import numpy as np
import OpenGL.GL as GL
import pyglet
from pyglet.graphics.shader import Shader, ShaderProgram

# para calcular inversa
from scipy import linalg

if sys.path[0] != "":
    sys.path.insert(0, "")

from grafica.utils import load_pipeline
import grafica.transformations as tr


# definimos un objeto partícula
class Particle(object):
    def __init__(self, position, ttl):
        self.position = np.array(position, dtype=np.float32)
        # por simpleza asumiremos que tiene velocidad constante en el eje y, sin aceleraci[on]
        self.velocity = np.array([0, -50, 0], dtype=np.float32)
        # ttl es la abreviación de "time to live", es el tiempo de vida restante
        self.ttl = ttl

    def step(self, dt):
        # en cada paso de la simulación pasan dos cosas.
        # por un lado, se reduce el tiempo de vida de la partícula
        self.ttl = self.ttl - dt
        # por otro, debemos actualizar su posición
        # en este caso sabemos que la velocidad siempre apunta en la misma dirección
        # pero en una aplicación más avanzada hay que calcular la velocidad
        # usamos el método de Euler
        self.position = self.position + dt * self.velocity

    def alive(self):
        # esta función utilitaria nos dice si la partícula está viva
        return bool(self.ttl > 0)


if __name__ == "__main__":
    width = 900
    height = 600

    win = pyglet.window.Window(width, height)

    pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "point_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "point_fragment_program.glsl",
    )

    # trabajaremos con una escena de 600x600
    # y esta escena se verá en toda la pantalla
    projection = tr.ortho(0, 600.0, 0, 600.0, 0.001, 10.0)

    # especificamos la cámara en coordenadas de la escena
    view = tr.lookAt(
        # posición de la cámara
        np.array([300.0, 300.0, 1.0]),
        # hacia dónde apunta
        np.array([300.0, 300.0, 0.0]),
        # vector para orientarla (arriba)
        np.array([0.0, 1.0, 0.0]),
    )

    # tendremos que convertir las coordenadas de la pantalla a coordenadas de la escena
    # para ello calculamos esta inversa
    inv_view_proj = linalg.inv(projection @ view)

    pipeline.use()
    pipeline["projection"] = projection.reshape(16, 1, order="F")
    pipeline["view"] = view.reshape(16, 1, order="F")
    pipeline["max_ttl"] = 3

    # nuestra colección de partículas.
    # ¿por qué es una deque (cola)?
    win.particles = deque()
    # Guardaremos una referencia a los datos que tendremos en la GPU.
    # La necesitaremos más tarde, porque los datos de las partículas
    # cambian todo el tiempo.
    win.particle_data = None

    @win.event
    def on_draw():
        win.clear()
        # usaremos esto en el shader, porque dibujaremos GL_POINTS
        GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        pipeline.use()

        # si no tenemos partículas, no dibujamos
        if win.particle_data is not None:
            win.particle_data.draw(pyglet.gl.GL_POINTS)

    @win.event
    def on_mouse_motion(x, y, dx, dy):
        # convertimos las coordenadas de la pantalla
        # (que fueron calculadas en la etapa de SCREEN MAPPING)
        # a coordenadas del volumen normalizado: entre -1 y 1
        norm_screen_x = (x / width) * 2 - 1
        norm_screen_y = (y / height) * 2 - 1

        # "desproyectamos"
        result = inv_view_proj @ np.array([norm_screen_x, norm_screen_y, 0.0, 1.0])

        # y el resultado se lo asignamos a una partícula
        win.particles.append(Particle((result[0], result[1], 0.0), 3))

    def update_particle_system(dt, win):
        # primero debemos revisar cuales partículas ya no están vivas
        to_remove = 0
        for i, p in enumerate(win.particles):
            p.step(dt)

            if not p.alive():
                to_remove += 1

        # descartamos a las que dejaron de vivir
        for i in range(to_remove):
            win.particles.popleft()

        if win.particle_data is not None:
            win.particle_data.delete()
            win.particle_data = None

        # si hay partículas vivas, hay que copiarlas a la GPU
        if len(win.particles) > 0:
            win.particle_data = pipeline.vertex_list(
                len(win.particles), pyglet.gl.GL_POINTS, position="f", ttl="f"
            )
            win.particle_data.position[:] = np.array(
                list(chain(*(p.position for p in win.particles)))
            )
            win.particle_data.ttl[:] = np.array(list(p.ttl for p in win.particles))

    pyglet.clock.schedule(update_particle_system, win)
    pyglet.app.run()
