import os
import sys
from itertools import chain
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL

import click

import grafica.transformations as tr
from grafica.utils import load_pipeline
# esta vez pusimos todos nuestros elementos en un archivo extra
from .elementos import rectangulo, stanford_bunny, regular_grid

@click.command("projection_example", short_help='Ejemplo de proyección')
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=960)
def projection_example(width, height):
    window = pyglet.window.Window(width, height)

    # primer elemento: el rectángulo de fondo
    bg_rectangle = rectangulo()

    # reusamos nuestros shaders
    bg_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / ".." / "hello_world" / "vertex_program.glsl", 
        Path(os.path.dirname(__file__)) / ".." / "hello_world" / "fragment_program.glsl") 

    bg_gpu_data = bg_pipeline.vertex_list_indexed(bg_rectangle['n_vertices'], bg_rectangle['gl_type'], bg_rectangle['indices'])

    bg_gpu_data.position[:] = bg_rectangle['position']
    bg_gpu_data.color[:] = bg_rectangle['color']

    # segundo, el conejo
    bunny = stanford_bunny()

    # cargamos el shader que usaremos para graficar al conejo
    bunny_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "mesh_vertex_program.glsl", 
        Path(os.path.dirname(__file__)) / ".." / "hello_world" / "fragment_program.glsl")

    bunny_gpu = bunny_pipeline.vertex_list_indexed(
        bunny['n_vertices'], bunny['gl_type'], bunny['indices']
    )
    bunny_gpu.position[:] = bunny['position']

    # en este caso sabemos que trimesh nos entregó una "sopa de triángulos"
    # donde algunos vértices se repiten. entonces, no podemos entregarle directamente
    # la curvatura que hemos calculado.
    # así que construimos la curvatura correspondiente a cada vértice de cada triángulo
    # nos ayudamos de los índices de las caras (bunny.faces) y el método numpy.take
    bunny_gpu.curvature[:] = bunny['curvature']

    # el tercer elemento es una grilla que graficaremos con GL_LINES (líneas)
    # nuevamente reusamos el fragment program. solo debemos cargar el vertex program
    grid = regular_grid(resolution=20)
    
    grid_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "grid_vertex_program.glsl", 
        Path(os.path.dirname(__file__)) / ".." / "hello_world" / "fragment_program.glsl")

    
    grid_gpu = grid_pipeline.vertex_list_indexed(
        grid['n_vertices'], grid['gl_type'], grid['indices']
    )
    
    grid_gpu.position[:] = grid['position']

    # agregamos la vista y la proyección a nuestro estado de programa
    total_time = 0.0
    transformations = {
        # al conejo le aplicamos la identidad por ahora.
        "bunny": tr.identity(),
        # nuestra grilla se define entre 0 y 1, movámosla para centrarla en el origen
        "grid": tr.translate(-0.5, -0.5, 0),
        # transformación de la vista
        "view": tr.lookAt(
            np.array([-1.0, 0, 0.25]),  # posición de la cámara
            np.array([0, 0, 0.25]),  # hacia dónde apunta
            np.array([0.0, 0.0, 1.0]),  # vector para orientarla (arriba)
        ),
        # transformación de proyección, en este caso, en perspectiva
        "projection": tr.perspective(60, width / height, 0.001, 5.0),
        # Variable para controlar el tipo de proyección
        "projection_type": "perspective",
    }

    # Creamos las dos matrices de proyección que vamos a utilizar
    perspective_projection = tr.perspective(60, width / height, 0.001, 5.0)
    # Para la proyección isométrica usamos una matriz ortográfica
    # Los parámetros son: izquierda, derecha, abajo, arriba, cerca, lejos
    orthographic_projection = tr.ortho(-0.5, 0.5, -0.5, 0.5, 0.001, 5.0)
    
    # Modificamos la vista para la proyección isométrica cuando se active
    # Una vista isométrica típica tiene ángulos iguales (120 grados) entre los ejes
    isometric_view = tr.lookAt(
        np.array([-0.7, -0.7, 0.7]),  # posición isométrica de la cámara
        np.array([0, 0, 0.25]),        # hacia dónde apunta (mismo punto)
        np.array([0.0, 0.0, 1.0])      # vector para orientarla (arriba)
    )
    
    # Vista en perspectiva original
    perspective_view = tr.lookAt(
        np.array([-1.0, 0, 0.25]),     # posición de la cámara
        np.array([0, 0, 0.25]),        # hacia dónde apunta
        np.array([0.0, 0.0, 1.0])      # vector para orientarla (arriba)
    )

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.P:
            # Cambiamos entre proyección en perspectiva e isométrica
            if transformations["projection_type"] == "perspective":
                transformations["projection"] = orthographic_projection
                transformations["view"] = isometric_view
                transformations["projection_type"] = "isometric"
            else:
                transformations["projection"] = perspective_projection
                transformations["view"] = perspective_view
                transformations["projection_type"] = "perspective"

    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glLineWidth(1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        window.clear()

        # desactivamos el test de profundidad porque el fondo es eso, un fondo
        GL.glDisable(GL.GL_DEPTH_TEST)
        bg_pipeline.use()
        bg_gpu_data.draw(bg_rectangle['gl_type'])

        # lo activamos a la hora de graficar nuestra escena
        GL.glEnable(GL.GL_DEPTH_TEST)

        # hora de dibujar al conejo! activamos su shader
        bunny_pipeline.use()

        bunny_pipeline["transform"] = transformations["bunny"].reshape(
            16, 1, order="F"
        )
        # le entregamos los nuevos parámetros al pipeline
        bunny_pipeline["view"] = transformations["view"].reshape(16, 1, order="F")
        bunny_pipeline["projection"] = transformations["projection"].reshape(
            16, 1, order="F"
        )
        bunny_gpu.draw(bunny['gl_type'])

        # ahora la grilla. activamos su shader y le pasamos los parámetros correspondientes
        grid_pipeline.use()
        grid_pipeline["transform"] = transformations["grid"].reshape(
            16, 1, order="F"
        )
        grid_pipeline["view"] = transformations["view"].reshape(16, 1, order="F")
        grid_pipeline["projection"] = transformations["projection"].reshape(
            16, 1, order="F"
        )
        # como dibujaremos líneas y no polígonos, debemos especificarlo en la llamada a draw
        grid_gpu.draw(grid['gl_type'])

    def update_world(dt, window):
        nonlocal total_time
        total_time += dt

        # actualizamos la transformación del conejo.
        # esta vez respecto al eje Z, es decir, en el "mundo del conejo"
        # y no en las coordenadas de OpenGL :)
        transformations["bunny"] = tr.rotationZ(total_time * 2.0)

    pyglet.clock.schedule_interval(update_world, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)