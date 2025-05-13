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


from grafica.scenegraph import Scenegraph
from grafica.scenegraph_premade import grid_2d


@click.command("disco_bunny", short_help="Ejemplo de Iluminación de Phong")
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=960)
def disco_bunny(width, height):
    window = pyglet.window.Window(width, height)

    graph = Scenegraph("root")

    graph.load_and_register_mesh("stanford_bunny", "assets/Stanford_Bunny.stl")
    graph.load_and_register_mesh("sphere", "assets/sphere.off")
    graph.register_mesh("grid", grid_2d(20))

    bunny_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "bunny_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "bunny_fragment_program.glsl",
    )

    grid_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "grid_vertex_program.glsl",
        Path(os.path.dirname(__file__))
        / ".."
        / "hello_world"
        / "fragment_program.glsl",
    )

    bulb_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "bulb_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "bulb_fragment_program.glsl",
    )

    graph.register_pipeline("bunny_pipeline", bunny_pipeline)
    graph.register_pipeline("bulb_pipeline", bulb_pipeline)
    graph.register_pipeline("grid_pipeline", grid_pipeline)

    graph.add_mesh_instance(
        "grid", "grid", "grid_pipeline", transform=tr.translate(-0.5, -0.5, 0)
    )
    print(graph.meshes["stanford_bunny"]["object"].bounds)
    bunny_centroid = graph.meshes["stanford_bunny"]["object"].centroid

    graph.add_mesh_instance(
        "bunny_mesh",
        "stanford_bunny",
        "bunny_pipeline",
        transform=tr.translate(
            0, 0, -graph.meshes["stanford_bunny"]["object"].bounds[0][2] / 2
        ),
    )

    # Añadir las esferas (luces)
    bulb_scale = 0.5  # Tamaño pequeño para las esferas
    bulb_1_color = np.array([0.0, 0.8, 1.0])  # Azul claro
    bulb_2_color = np.array([1.0, 0.3, 0.0])  # Naranja

    # Instancia de la primera luz (azul)
    graph.add_mesh_instance(
        "bulb_1_mesh",
        "sphere",
        "bulb_pipeline",
        transform=tr.uniformScale(bulb_scale),
        bulb_color=bulb_1_color
    )

    # Instancia de la segunda luz (naranja)
    graph.add_mesh_instance(
        "bulb_2_mesh",
        "sphere",
        "bulb_pipeline",
        transform=tr.uniformScale(bulb_scale),
        bulb_color=bulb_2_color
    )

    graph.add_edge("root", "ground")
    graph.add_edge("ground", "grid")
    graph.add_edge("ground", "bunny")
    graph.add_edge("bunny", "bunny_mesh")

    graph.add_edge("root", "bulb_1")
    graph.add_edge("bulb_1", "bulb_1_mesh")
    
    graph.add_edge("root", "bulb_2")
    graph.add_edge("bulb_2", "bulb_2_mesh")

    view = tr.lookAt(
        np.array([-2.0, 0, 0.75]),  # posición de la cámara
        np.array([0, 0.0, 0.5]),  # hacia dónde apunta
        np.array([0.0, 0.0, 1.0]),  # vector para orientarla (arriba)
    )

    projection = tr.perspective(60, width / height, 0.001, 5.0)

    graph.register_view_transform(view)
    # agregamos la vista y la proyección a nuestro estado de programa
    total_time = 0.0

    radius = 0.8
    light1_pos = np.array([radius, 0, 0.7])
    light2_pos = np.array([0, radius, 0.4])

    @window.event
    def on_draw():
        GL.glClearColor(0.1, 0.0, 0.1, 1.0)
        GL.glLineWidth(1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_DEPTH_TEST)

        window.clear()

        # aquí le pedimos al grafo las posiciones actualizadas
        graph.set_global_attributes(
            view=view,
            projection=projection,
            light_1_position=graph.get_global_position("bulb_1"),
            light_2_position=graph.get_global_position("bulb_2")
        )

        # ya calculamos las transformaciones en el método update_world
        graph.render(recalculate_transforms=False)

    def update_world(dt, window):
        nonlocal total_time
        total_time += dt

        graph.nodes["bunny"]["transform"] = tr.rotationZ(total_time * 0.5)

        # Parámetros para animación de luces
        radius_base = 0.8
        height_base1 = 0.7
        height_base2 = 0.4

        # Primera luz (azul) - movimiento más complejo
        # Pulso en el radio - crece y decrece periódicamente
        radius_pulse1 = radius_base + 0.2 * np.sin(total_time * 5.0)
        
        # Movimiento principal con aceleración variable
        angle1 = total_time * 2.0 + np.sin(total_time * 0.8) * 0.5
        
        # Altura pulsante
        height1 = height_base1 + 0.15 * np.sin(total_time * 3.7)

        light1_x = radius_pulse1 * np.cos(angle1)
        light1_y = radius_pulse1 * np.sin(angle1)
        graph.nodes["bulb_1"]["transform"] = tr.translate(light1_x, light1_y, height1)

        # Segunda luz (naranja) - otro patrón de movimiento
        # Radio con pulso diferente
        radius_pulse2 = radius_base + 0.15 * np.cos(total_time * 4.3)
        
        # Movimiento principal con patrón diferente
        angle2 = -total_time * 3.0 + np.pi + np.sin(total_time * 1.2) * 0.7
        
        # Altura con saltos ocasionales (usando una función periódica)
        bounce_factor = max(0, np.sin(total_time * 2.5))  # Solo valores positivos
        height2 = height_base2 + 0.25 * bounce_factor * bounce_factor  # Efecto de rebote

        # Posición final de la luz 2
        light2_x = radius_pulse2 * np.cos(angle2)
        light2_y = radius_pulse2 * np.sin(angle2)
        graph.nodes["bulb_2"]["transform"] = tr.translate(light2_x, light2_y, height2)

        # Calcular transformaciones globales (esto actualiza graph.global_transforms)
        graph.calculate_global_transforms()

    pyglet.clock.schedule_interval(update_world, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
