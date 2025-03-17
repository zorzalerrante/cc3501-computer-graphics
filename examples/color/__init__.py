import os
from pathlib import Path

import click
import numpy as np
import pyglet
from OpenGL import GL

from grafica.utils import load_pipeline


@click.command("color_wheel", short_help="Ejemplo de espacios de color")
@click.option("--width", type=int, default=800)
@click.option("--height", type=int, default=600)
def color_wheel(width, height):
    # creamos la ventana
    win = pyglet.window.Window(width, height)

    # nuestra escena contiene un cuadrilátero cuyas esquinas están en (-1,-1) y (1,1).
    # es decir, está contenido en el volumen normalizado de vista.
    # este cuadrilátero contiene cuatro vértices:
    vertices = np.array(
        [
            -1, -1, # inf izq
             1, -1, # if der
             1,  1, # sup der
            -1,  1, # sup izq
        ],
        dtype=np.float32,
    )

    # la GPU trabaja con triángulos. así que debemos especificar
    # cuáles vertices conforman los triángulos que graficaremos
    # tenemos dos triángulos: (0, 1, 2) y (2, 3, 0)
    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    # este método auxiliar en el módulo grafica nos permite cargar
    # vertex y fragment program
    # aunque en este ejemplo nos enfocamos en el fragment program
    # no puede haber FP sin VP
    pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program.glsl",
    )
    
    # debemos copiar nuestra escena a la GPU
    # primero, le indicamos que graficaremos triángulos
    gpu_data = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, indices)
    # y luego le indicamos cuáles son los vértices asociados a esos triángulos
    gpu_data.position[:] = vertices
    
    # para nuestro programa necesitaremos saber 
    # 1) la resolución de la pantalla (Vec2 en el FP)
    # 2) el tiempo total transcurrido (float en el FP)
    pipeline["resolution"] = np.array([width, height])
    total_time = 0.0
    

    @win.event
    def on_draw():
        # para acceder a la variable total_time que definimos antes
        nonlocal total_time

        # ¿qué hacer cuando se limpia el frame buffer?
        # se deja con un color. aquí, negro en RGBA
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)

        # antes de graficar, limpiamos el frame buffer
        win.clear()

        # actualizamos el parámetro time con el tiempo total de ejecución
        # ¡nota que este tiempo se actualiza en otra función!
        pipeline["time"] = total_time

        # ahora, para graficar, le indicamos a OpenGL que active el pipeline en su estado
        pipeline.use()
        # ¡noten que lo que se grafica es la escena!
        gpu_data.draw(GL.GL_TRIANGLES)

    def update(dt, window):
        # para acceder a la variable total_time que definimos antes
        nonlocal total_time
        total_time += dt

    # esta función dice que 60 veces por segundo se ejecute la función update
    pyglet.clock.schedule_interval(update, 1 / 60.0, win)

    # pyglet entrará en el _game loop_ con esto
    pyglet.app.run()
