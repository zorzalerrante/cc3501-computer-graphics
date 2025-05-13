import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path
import click


# una función auxiliar para cargar shaders
from grafica.utils import load_pipeline

from grafica.arcball import Arcball
from grafica.textures import texture_2D_setup
from grafica.scenegraph import Scenegraph

# from grafica.scenegraph_nodes import node_from_file
from grafica.scenegraph_premade import rectangle_2d
import grafica.transformations as tr


@click.command("arcball_example", short_help="Visor interactivo de modelos 3D")
@click.argument("filename", type=str)
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=720)
def arcball_example(filename, width, height):
    window = pyglet.window.Window(width, height)

    graph = Scenegraph("root")
    graph.load_and_register_mesh("object", filename)

    # como no todos los archivos que carguemos tendrán textura,
    # tendremos dos pipelines
    base_path = Path(os.path.dirname(__file__))
    # uno para archivos con textura
    tex_pipeline = load_pipeline(
        base_path / "vertex_program.glsl",
        base_path / "fragment_program.glsl",
    )

    # y otro para archivos sin ella
    notex_pipeline = load_pipeline(
        base_path / "vertex_program_notex.glsl",
        base_path / "fragment_program_notex.glsl",
    )

    # también tenemos un pipeline para ver profundidad!
    depth_pipeline = load_pipeline(
        base_path / "z_vertex_program.glsl",
        base_path / "z_fragment_program.glsl",
    )

    main_pipeline = tex_pipeline if graph.meshes["object"]["has_texture"] else notex_pipeline

    current_pipeline = 0
    pipelines = [main_pipeline, depth_pipeline]
    graph.register_pipeline("pipeline", main_pipeline)

    graph.add_mesh_instance("object", "object", "pipeline")
    graph.add_edge("root", "object")

    near_plane = 0.1
    far_plane = 5.0

    projection = tr.perspective(45, float(width) / float(height), near_plane, far_plane)
    view = tr.lookAt(np.array([0, 0, 2]), np.array([0, 0, 0]), np.array([0, 1, 0]))

    graph.register_view_transform(view)

    # instanciamos nuestra Arcball
    arcball = Arcball(
        np.linalg.inv(view),
        np.array((width, height), dtype=float),
        1.5,
        np.array([0.0, 0.0, 0.0]),
    )

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        # print("press", x, y, button, modifiers)
        # Botón izquierdo (button=1) para rotación
        if button == pyglet.window.mouse.LEFT:
            arcball.set_state(Arcball.STATE_ROTATE)
        # Botón derecho (button=4) para traslación
        elif button == pyglet.window.mouse.RIGHT:
            arcball.set_state(Arcball.STATE_PAN)
        # Botón central (button=2) para zoom (opcional)
        elif button == pyglet.window.mouse.MIDDLE:
            arcball.set_state(Arcball.STATE_ZOOM)

        arcball.down((x, y))

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        # print("release", x, y, button, modifiers)
        # Opcional: volver al estado de rotación por defecto
        arcball.set_state(Arcball.STATE_ROTATE)
        # print(arcball.pose)

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        # print("drag", x, y, dx, dy, buttons, modifiers)
        arcball.drag((x, y))

    @window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        # print("scroll", x, y, scroll_x, scroll_y)
        arcball.scroll(scroll_y)

    @window.event
    def on_key_press(symbol, modifiers):
        nonlocal current_pipeline
        if symbol == pyglet.window.key.SPACE:
            current_pipeline = not current_pipeline
            graph.register_pipeline('pipeline', pipelines[current_pipeline])

    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        window.clear()

        graph.nodes["root"]["transform"] = np.linalg.inv(arcball.pose)

        graph.set_global_attributes(
            projection=projection, far_plane=far_plane, near_plane=near_plane
        )

        graph.render()

    pyglet.app.run()
