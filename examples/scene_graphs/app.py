import os.path
import sys
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL

import click

import grafica.transformations as tr
from grafica.utils import load_pipeline
from grafica.scenegraph import Scenegraph
from grafica.scenegraph_premade import unit_axes_node

@click.command("solar_system", short_help="Sistema solar con grafos de escena")
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=960)
def solar_system(width, height):
    window = pyglet.window.Window(width, height)

    # cargamos una esfera y la convertimos en una bola de diámetro 1
    #mesh = node_from_file("assets/sphere.off")

    solar_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "mesh_vertex_program.glsl",
        Path(os.path.dirname(__file__))
        / ".."
        / "hello_world"
        / "fragment_program.glsl",
    )


    axis_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "line_vertex_program.glsl",
        Path(os.path.dirname(__file__))
        / ".."
        / "hello_world"
        / "fragment_program.glsl",
    )

    #add_node_pipeline(axis, axis_pipeline)

    # creamos el grafo de escena con la función definida más arriba
    graph = Scenegraph("sun")
    graph.load_and_register_mesh('sphere', "assets/sphere.off")
    graph.register_mesh('axis', unit_axes_node())
    graph.register_pipeline('solar_pipeline', solar_pipeline)
    graph.register_pipeline('axis_pipeline', axis_pipeline)

    graph.add_transform("sun_geometry", tr.uniformScale(0.8))
    graph.add_mesh_instance("sun_mesh", 'sphere', 'solar_pipeline', color=np.array((1.0, 0.73, 0.03)))
    graph.add_mesh_instance("sun_axis", 'axis', 'axis_pipeline', transform=tr.uniformScale(1))

    graph.add_edge("sun", "sun_geometry")
    graph.add_edge("sun_geometry", "sun_mesh")
    graph.add_edge("sun", "sun_axis")

    graph.add_transform("earth", tr.translate(2.5, 0.0, 0.0))
    graph.add_transform("earth_geometry", tr.uniformScale(0.3))
    graph.add_mesh_instance("earth_mesh", 'sphere', 'solar_pipeline', color=np.array((0.0, 0.59, 0.78)))
    graph.add_mesh_instance(
        "earth_axis", 'axis', 'axis_pipeline', transform=tr.uniformScale(0.5)
    )

    graph.add_edge("sun", "earth")
    graph.add_edge("earth", "earth_geometry")
    graph.add_edge("earth_geometry", "earth_mesh")
    graph.add_edge("earth", "earth_axis")

    graph.add_transform("moon", tr.translate(0.5, 0.0, 0.0))
    graph.add_transform("moon_geometry", tr.uniformScale(0.1))
    graph.add_mesh_instance("moon_mesh", 'sphere', 'solar_pipeline', color=np.array((0.6, 0.6, 0.6)))
    graph.add_mesh_instance(
        "moon_axis", 'axis', 'axis_pipeline', transform=tr.uniformScale(0.25)
    )

    graph.add_edge("earth", "moon")
    graph.add_edge("moon", "moon_geometry")
    graph.add_edge("moon_geometry", "moon_mesh")
    graph.add_edge("moon", "moon_axis")


    total_time = 0.0
    view = tr.lookAt(np.array([5, 5, 5]), np.array([0, 0, 0]), np.array([0, 1, 0]))
    projection = tr.perspective(45, float(width) / float(height), 0.1, 100)

    graph.register_view_transform(view)
    graph.set_global_attributes(projection=projection)

    @window.event
    def on_draw():
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        GL.glLineWidth(2.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_DEPTH_TEST)

        window.clear()

        graph.render()

    # esta función actualiza el grafo de escena en función del tiempo
    # en este caso, hace algo similar a lo que hemos hecho en ejemplos anteriores
    # al asignar rotaciones que dependen del tiempo transcurrido en el programa
    def update_solar_system(dt, window):
        nonlocal total_time
        total_time += dt
        # para acceder a un nodo del grafo utilizamos su atributo .nodes
        # cada nodo es almacenado como un diccionario
        # por tanto, accedemos a él y a sus atributos con llaves de diccionario
        # que conocemos porque nosotres construimos el grafo
        graph.nodes["earth"]["transform"] = tr.rotationY(2 * total_time) @ tr.translate(
            2.5, 0.0, 0.0
        )
        graph.nodes["moon"]["transform"] = tr.rotationY(3 * total_time) @ tr.translate(
            0.5, 0.0, 0.0
        )

    pyglet.clock.schedule_interval(update_solar_system, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
