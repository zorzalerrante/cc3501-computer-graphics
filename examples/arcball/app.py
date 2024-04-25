import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path
import sys

if sys.path[0] != "":
    sys.path.insert(0, "")

# una función auxiliar para cargar shaders
from grafica.utils import load_pipeline

from grafica.arcball import Arcball
from grafica.textures import texture_2D_setup

if __name__ == "__main__":
    width = 960
    height = 960
    window = pyglet.window.Window(width, height)

    # dependiendo de lo que contenga el archivo a cargar,
    # trimesh puede entregar una malla (mesh)
    # o una escena (compuesta de mallas)
    # con esto forzamos que siempre entregue una escena
    asset = tm.load(sys.argv[1], force="scene")

    # de acuerdo a la documentación de trimesh, esto centra la escena
    # no es igual a trabajar con una malla directamente
    asset.rezero()

    # y esto la escala. se crea una copia, por eso la asignación
    asset = asset.scaled(2.0 / asset.scale)

    # como no todos los archivos que carguemos tendrán textura,
    # tendremos dos pipelines
    tex_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program.glsl",
    )

    notex_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program_notex.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program_notex.glsl",
    )

    # aquí guardaremos las mallas del modelo que graficaremos
    vertex_lists = {}

    # con esto iteramos sobre las mallas
    for object_id, object_geometry in asset.geometry.items():
        mesh = {}

        # por si acaso, para que la malla tenga normales consistentes
        object_geometry.fix_normals(True)

        object_vlist = tm.rendering.mesh_to_vertexlist(object_geometry)

        n_triangles = len(object_vlist[4][1]) // 3

        # el pipeline a usar dependerá de si el objeto tiene textura
        # OJO: asumimos que si tiene material, tiene textura
        # pero no siempre es así.
        if hasattr(object_geometry.visual, "material"):
            mesh["pipeline"] = tex_pipeline
            has_texture = True
        else:
            mesh["pipeline"] = notex_pipeline
            has_texture = False

        # inicializamos los datos en la GPU
        mesh["gpu_data"] = mesh["pipeline"].vertex_list_indexed(
            n_triangles, GL.GL_TRIANGLES, object_vlist[3]
        )

        # copiamos la posición de los vértices
        mesh["gpu_data"].position[:] = object_vlist[4][1]

        # las normales vienen en vertex_list[5]
        # las manipulamos del mismo modo que los vértices
        mesh["gpu_data"].normal[:] = object_vlist[5][1]

        # con (o sin) textura es diferente el procedimiento
        # aunque siempre en vertex_list[6] viene la información de material
        if has_texture:
            # copiamos la textura
            # trimesh ya la cargó, solo debemos copiarla a la GPU
            # si no se usa trimesh, el proceso es el mismo,
            # pero se debe usar Pillow para cargar la imagen
            mesh["texture"] = texture_2D_setup(object_geometry.visual.material.image)
            # copiamos las coordenadas de textura en el parámetro uv
            mesh["gpu_data"].uv[:] = object_vlist[6][1]
        else:
            # usualmente el color viene como c4B/static en vlist[6][0], lo que significa "color de 4 bytes". idealmente eso debe verificarse
            mesh["gpu_data"].color[:] = object_vlist[6][1]

        vertex_lists[object_id] = mesh

    # instanciamos nuestra Arcball
    arcball = Arcball(
        np.identity(4),
        np.array((width, height), dtype=float),
        1.5,
        np.array([0.0, 0.0, 0.0]),
    )

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        print("press", x, y, button, modifiers)
        arcball.down((x, y))

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        print("release", x, y, button, modifiers)
        print(arcball.pose)

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        print("drag", x, y, dx, dy, buttons, modifiers)
        arcball.drag((x, y))

    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glLineWidth(1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        window.clear()

        for object_geometry in vertex_lists.values():
            # dibujamos cada una de las mallas con su respectivo pipeline
            pipeline = object_geometry["pipeline"]
            pipeline.use()

            pipeline["transform"] = arcball.pose.reshape(16, 1, order="F")
            pipeline["light_position"] = np.array([-1.0, 1.0, -1.0])

            if "texture" in object_geometry:
                GL.glBindTexture(GL.GL_TEXTURE_2D, object_geometry["texture"])
            else:
                # esto "activa" una textura nula
                GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

            object_geometry["gpu_data"].draw(pyglet.gl.GL_TRIANGLES)

    pyglet.app.run()
