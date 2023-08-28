import os
import sys
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL
import trimesh as tm

if sys.path[0] != "":
    sys.path.insert(0, "")

import grafica.transformations as tr

if __name__ == "__main__":
    try:
        config = pyglet.gl.Config(sample_buffers=1, samples=4)
        window = pyglet.window.Window(960, 960, config=config)
    except pyglet.window.NoSuchConfigException:
        window = pyglet.window.Window(960, 960)

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

    # noten que esta vez no lo agrandamos!
    bunny_scale = tr.uniformScale(1.0 / bunny.scale)
    bunny_translate = tr.translate(*-bunny.centroid)
    bunny_rotate = tr.rotationX(-np.pi / 2)
    bunny.apply_transform(bunny_rotate @ bunny_scale @ bunny_translate)

    # reusamos nuestros shaders
    with open(
        Path(os.path.dirname(__file__))
        / ".."
        / "transformations"
        / "vertex_program.glsl"
    ) as f:
        vertex_source_code = f.read()

    with open(
        Path(os.path.dirname(__file__))
        / ".."
        / "transformations"
        / "fragment_program.glsl"
    ) as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    bunny_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # dibujaremos cuatro conejos, pero basta que lo copiemos una única vez a la GPU
    bunny_vertex_list = tm.rendering.mesh_to_vertexlist(bunny)
    bunny_gpu = bunny_pipeline.vertex_list_indexed(
        len(bunny_vertex_list[4][1]) // 3, GL.GL_TRIANGLES, bunny_vertex_list[3]
    )
    bunny_gpu.position[:] = bunny_vertex_list[4][1]

    # tendremos cuatro transformaciones distintas, una por conejo
    window.program_state = {
        "bunny": {
            "TL": tr.identity(),
            "TR": tr.identity(),
            "BL": tr.identity(),
            "BR": tr.identity(),
        },
        "total_time": 0.0,
    }

    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glLineWidth(1.0)
        window.clear()

        # dibujamos nuestro primer objeto. este lo pintamos (GL_FILL)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        bg_pipeline.use()
        bg_gpu_data.draw(GL.GL_TRIANGLES)

        # dibujamos nuestro segundo objeto. usamos el wireframe (GL_LINE)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        bunny_pipeline.use()

        # dibujamos tantos conejos como tengamos en nuestro programa
        for transform in window.program_state["bunny"].values():
            bunny_pipeline["view_transform"] = transform.reshape(16, 1, order="F")
            bunny_gpu.draw(pyglet.gl.GL_TRIANGLES)

        # noten que no interfieren los sistemas de coordenadas ni transformaciones
        # entre ellos.

    def update_world(dt, window):
        window.program_state["total_time"] += dt
        total_time = window.program_state["total_time"]

        # actualizamos cada una de las transformaciones
        window.program_state["bunny"]["TL"] = tr.translate(-0.5, 0.5, 0) @ tr.rotationZ(
            total_time * 6.0
        )

        window.program_state["bunny"]["TR"] = (
            tr.translate(0.5, 0.5, 0)
            @ tr.rotationZ(total_time * 6.0)
            @ tr.translate(-0.25, -0.25, 0)
            @ tr.uniformScale(0.4)
        )

        window.program_state["bunny"]["BL"] = tr.translate(
            -0.5, -0.5, 0
        ) @ tr.rotationX(total_time * 6.0)

        window.program_state["bunny"]["BR"] = tr.translate(0.5, -0.5, 0) @ tr.rotationY(
            total_time * 6.0
        )

    pyglet.clock.schedule_interval(update_world, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
