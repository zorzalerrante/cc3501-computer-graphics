import os
import sys
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL
import trimesh as tm

import click

# importamos esta función de trimesh porque nos permitirá asignarle una propiedad a cada vértice
# y pintaremos el conejo en función de esa propiedad
# en este caso, es la curvatura de la superficie
from trimesh.curvature import discrete_gaussian_curvature_measure
import grafica.transformations as tr
from grafica.utils import load_pipeline


@click.command("compositions", short_help="Ejemplo de composición de transformaciones")
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=960)
def compositions(width, height):
    try:
        config = pyglet.gl.Config(sample_buffers=1, samples=4)
        window = pyglet.window.Window(width, height, config=config)
    except pyglet.window.NoSuchConfigException:
        window = pyglet.window.Window(width, height)

    # elementos en nuestra escena
    # primero, el rectángulo que usaremos de fondo
    vertices = np.array(
        [
            -1,
            -1,
            0.0,  # inf izq
            1,
            -1,
            0.0,  # if der
            1,
            1,
            0.0,  # sup der
            -1,
            1,
            0.0,  # sup izq
        ],
        dtype=np.float32,
    )

    vertex_colors = np.array(
        [
            1.0,
            204 / 255.0,
            1.0,  # inf izq
            1.0,
            204 / 255.0,
            1.0,  # if der
            204 / 255.0,
            1.0,
            1.0,  # sup der
            204 / 255.0,
            1.0,
            1.0,  # sup izq
        ],
        dtype=np.float32,
    )

    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    # reusamos nuestros shaders
    bg_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / ".." / "hello_world" / "vertex_program.glsl",
        Path(os.path.dirname(__file__))
        / ".."
        / "hello_world"
        / "fragment_program.glsl",
    )

    bg_gpu_data = bg_pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, indices)
    bg_gpu_data.position[:] = vertices
    bg_gpu_data.color[:] = vertex_colors

    # segundo, el conejo
    bunny = tm.load("assets/Stanford_Bunny.stl")

    # noten que esta vez no lo agrandamos!
    bunny_scale = tr.uniformScale(1.0 / bunny.scale)
    bunny_translate = tr.translate(*-bunny.centroid)
    bunny_rotate = tr.rotationX(-np.pi / 2)
    bunny.apply_transform(bunny_rotate @ bunny_scale @ bunny_translate)

    # aquí calculamos la curvatura. pueden ver la documentación de trimesh para saber qué es.
    bunny_curvature = discrete_gaussian_curvature_measure(bunny, bunny.vertices, 0.01)
    # la curvatura está definida entre -1 y 1, así que la convertimos al rango 0 a 1.
    # usaremos este valor para pintar cada vértice en el vertex shader
    bunny_curvature = (bunny_curvature + 1) / 2

    bunny_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "mesh_vertex_program.glsl",
        Path(os.path.dirname(__file__))
        / ".."
        / "hello_world"
        / "fragment_program.glsl",
    )

    # dibujaremos cuatro conejos, pero basta que lo copiemos una única vez a la GPU
    bunny_vertex_list = tm.rendering.mesh_to_vertexlist(bunny)
    bunny_gpu = bunny_pipeline.vertex_list_indexed(
        len(bunny_vertex_list[4][1]) // 3, GL.GL_TRIANGLES, bunny_vertex_list[3]
    )
    bunny_gpu.position[:] = bunny_vertex_list[4][1]
    bunny_gpu.curvature[:] = np.take(bunny_curvature, bunny.faces).reshape(
        -1, 1, order="C"
    )

    # tendremos cuatro transformaciones distintas, una por conejo
    transforms = {
        "TL": tr.identity(),
        "TR": tr.identity(),
        "BL": tr.identity(),
        "BR": tr.identity(),
    }

    total_time = 0.0

    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glLineWidth(1.0)
        window.clear()

        # dibujamos nuestro primer objeto. este lo pintamos (GL_FILL)
        # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        bg_pipeline.use()
        bg_gpu_data.draw(GL.GL_TRIANGLES)

        # dibujamos nuestro segundo objeto. usamos el wireframe (GL_LINE)
        # GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        bunny_pipeline.use()

        # dibujamos tantos conejos como tengamos en nuestro programa
        for transform in transforms.values():
            bunny_pipeline["transform"] = transform.reshape(16, 1, order="F")
            bunny_gpu.draw(pyglet.gl.GL_TRIANGLES)

        # noten que no interfieren los sistemas de coordenadas ni transformaciones
        # entre ellos.

    def update_world(dt, window):
        nonlocal total_time, transforms
        total_time += dt

        # Conejo TL: Rotación en Z (original)
        transforms["TL"] = tr.translate(-0.5, 0.5, 0) @ tr.rotationZ(total_time * 6.0)

        # Conejo TR: Efecto de pulsación (breathing)
        # Usa una función seno para crear un efecto de respiración con el escalado
        breathing_scale = 0.3 + 0.1 * np.sin(total_time * 3.0)
        transforms["TR"] = tr.translate(0.5, 0.5, 0) @ tr.uniformScale(breathing_scale)

        # Conejo BL: Efecto de rebote (bouncing)
        # Usa una función abs(sin) para simular un rebote vertical
        bounce_height = 0.15 * abs(np.sin(total_time * 4.0))
        bounce_squash = 1.0 - 0.2 * abs(
            np.cos(total_time * 4.0)
        )  # Aplana cuando toca el "suelo"
        transforms["BL"] = tr.translate(-0.5, -0.5 + bounce_height, 0) @ tr.scale(
            1.1 * bounce_squash, 0.9 + 0.2 * (1 - bounce_squash), 1.0
        )

        # Conejo BR: Rotación en Y (original)
        transforms["BR"] = tr.translate(0.5, -0.5, 0) @ tr.rotationY(total_time * 6.0)

    pyglet.clock.schedule_interval(update_world, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
