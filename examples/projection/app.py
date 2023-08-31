import os
import sys
from itertools import chain
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL
import trimesh as tm
# importamos esta función de trimesh porque nos permitirá asignarle una propiedad a cada vértice
# y pintaremos el conejo en función de esa propiedad
# en este caso, es la curvatura de la superficie
from trimesh.curvature import discrete_gaussian_curvature_measure

if sys.path[0] != "":
    sys.path.insert(0, "")

import grafica.transformations as tr

if __name__ == "__main__":
    # noten que esta vez guardamos el ancho y alto de nuestra ventana en variables.
    # las usaremos
    width = 960
    height = 960

    window = pyglet.window.Window(width, height)

    # primer elemento: el rectángulo de fondo
    vertices = np.array(
        [
            -1, -1, 0.0,  # inf izq
             1, -1, 0.0,  # if der
             1,  1, 0.0,  # sup der
            -1,  1, 0.0,  # sup izq
        ],
        dtype=np.float32,
    )

    vertex_colors = np.array(
        [
            1.0, 204 / 255.0, 1.0,  # inf izq
            1.0, 204 / 255.0, 1.0,  # if der
            204 / 255.0, 1.0, 1.0,  # sup der
            204 / 255.0, 1.0, 1.0,  # sup izq
        ],
        dtype=np.float32,
    )

    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    # reusamos nuestros shaders
    with open(
        Path(os.path.dirname(__file__)) / ".." / "hello_world" / "vertex_program.glsl"
    ) as f:
        vertex_source_code = f.read()

    with open(
        Path(os.path.dirname(__file__)) / ".." / "hello_world" / "fragment_program.glsl"
    ) as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    bg_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    bg_gpu_data = bg_pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, indices)
    bg_gpu_data.position[:] = vertices
    bg_gpu_data.color[:] = vertex_colors

    # segundo, el conejo
    bunny = tm.load("assets/Stanford_Bunny.stl")

    # model transform del conejo. la aplicamos directamente en trimesh
    # noten que esta vez solamente escalamos al conejo, ¡no lo estamos rotando!
    bunny_scale = tr.uniformScale(1.0 / bunny.scale)
    bunny_translate = tr.translate(*-bunny.centroid)
    bunny.apply_transform(bunny_scale @ bunny_translate)
    # el conejo ya está transformado. pero lo movimos al origen, 
    # cuando en realidad queremos que esté sobre el suelo
    # con esto dejamos la parte baja del conejo en z = 0
    # asumiento que z apunta hacia arriba en nuestro mundo
    bunny.apply_transform(tr.translate(0, 0, -bunny.vertices[:, 2].min()))

    # aquí calculamos la curvatura. pueden ver la documentación de trimesh para saber qué es.
    bunny_curvature = discrete_gaussian_curvature_measure(bunny, bunny.vertices, 0.01)
    # la curvatura está definida entre -1 y 1, así que la convertimos al rango 0 a 1.
    # usaremos este valor para pintar cada vértice en el vertex shader
    bunny_curvature = (bunny_curvature + 1) / 2

    # cargamos el shader que usaremos para graficar al conejo
    # noten que no cargamos fragment shader: usaremos el mismo del fondo.
    # eso es posible porque ese shader solo pinta colores interpolados.
    with open(Path(os.path.dirname(__file__)) / "mesh_vertex_program.glsl") as f:
        vertex_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    bunny_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    bunny_vertex_list = tm.rendering.mesh_to_vertexlist(bunny)
    bunny_gpu = bunny_pipeline.vertex_list_indexed(
        len(bunny_vertex_list[4][1]) // 3, GL.GL_TRIANGLES, bunny_vertex_list[3]
    )
    bunny_gpu.position[:] = bunny_vertex_list[4][1]

    # en este caso sabemos que trimesh nos entregó una "sopa de triángulos"
    # donde algunos vértices se repiten. entonces, no podemos entregarle directamente
    # la curvatura que hemos calculado.
    # así que construimos la curvatura correspondiente a cada vértice de cada triángulo
    # nos ayudamos de los índices de las caras (bunny.faces) y el método numpy.take
    bunny_gpu.curvature[:] = np.take(bunny_curvature, bunny.faces).reshape(
        -1, 1, order="C"
    )

    # el tercer elemento es una grilla que graficaremos con GL_LINES (líneas)
    # nuevamente reusamos el fragment program. solo debemos cargar el vertex program
    with open(Path(os.path.dirname(__file__)) / "grid_vertex_program.glsl") as f:
        vertex_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    grid_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # construimos nuestra grilla.
    grid_resolution = 10

    xv, yv = np.meshgrid(
        np.linspace(0, 1, grid_resolution),
        np.linspace(0, 1, grid_resolution),
        indexing="xy",
    )

    grid_vertices = np.vstack(
        (
            xv.reshape(1, -1),
            yv.reshape(1, -1),
            np.zeros(shape=(1, grid_resolution**2)),
        )
    ).T

    grid_indices = [
        [
            (grid_resolution * row + i, grid_resolution * row + i + 1)
            for i in range(grid_resolution - 1)
        ]
        for row in range(grid_resolution)
    ]
    
    grid_indices.extend(
        [
            [
                (
                    grid_resolution * column + i,
                    grid_resolution * column + i + grid_resolution,
                )
                for i in range(grid_resolution)
            ]
            for column in range(grid_resolution - 1)
        ]
    )
    
    grid_indices = list(chain(*chain(*grid_indices)))
    
    grid_gpu = grid_pipeline.vertex_list_indexed(
        grid_resolution**2, GL.GL_LINES, grid_indices
    )
    
    grid_gpu.position[:] = grid_vertices.reshape(-1, 1, order="C")

    # agregamos la vista y la proyección a nuestro estado de programa
    window.program_state = {
        # al conejo le aplicamos la identidad por ahora.
        "bunny": tr.identity(),
        # nuestra grilla se define entre 0 y 1, movámosla para centrarla en el origen
        "grid": tr.translate(-0.5, -0.5, 0),
        "total_time": 0.0,
        # transformación de la vista
        "view": tr.lookAt(
            np.array([-1.0, 0, 0.25]),  # posición de la cámara
            np.array([0, 0, 0.25]),  # hacia dónde apunta
            np.array([0.0, 0.0, 1.0]),  # vector para orientarla (arriba)
        ),
        # transformación de proyección, en este caso, en perspectiva
        "projection": tr.perspective(60, width / height, 0.001, 5.0),
    }

    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glLineWidth(1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        window.clear()

        # desactivamos el test de profundidad porque el fondo es eso, un fondo
        GL.glDisable(GL.GL_DEPTH_TEST)
        bg_pipeline.use()
        bg_gpu_data.draw(GL.GL_TRIANGLES)

        # lo activamos a la hora de graficar nuestra escena
        GL.glEnable(GL.GL_DEPTH_TEST)

        # hora de dibujar al conejo! activamos su shader
        bunny_pipeline.use()

        bunny_pipeline["transform"] = window.program_state["bunny"].reshape(
            16, 1, order="F"
        )
        # le entregamos los nuevos parámetros al pipeline
        bunny_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        bunny_pipeline["projection"] = window.program_state["projection"].reshape(
            16, 1, order="F"
        )
        bunny_gpu.draw(GL.GL_TRIANGLES)

        # ahora la grilla. activamos su shader y le pasamos los parámetros correspondientes
        grid_pipeline.use()
        grid_pipeline["transform"] = window.program_state["grid"].reshape(
            16, 1, order="F"
        )
        grid_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        grid_pipeline["projection"] = window.program_state["projection"].reshape(
            16, 1, order="F"
        )
        # como dibujaremos líneas y no polígonos, debemos especificarlo en la llamada a draw
        grid_gpu.draw(GL.GL_LINES)

    def update_world(dt, window):
        window.program_state["total_time"] += dt
        total_time = window.program_state["total_time"]

        # actualizamos la transformación del conejo.
        # esta vez respecto al eje Z, es decir, en el "mundo del conejo"
        # y no en las coordenadas de OpenGL :)
        window.program_state["bunny"] = tr.rotationZ(total_time * 2.0)

    pyglet.clock.schedule_interval(update_world, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
