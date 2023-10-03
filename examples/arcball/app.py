import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path
import sys

if sys.path[0] != "":
    sys.path.insert(0, "")

import grafica.transformations as tr

from grafica.arcball import Arcball
from grafica.textures import texture_2D_setup

if __name__ == "__main__":
    width = 960
    height = 960
    window = pyglet.window.Window(width, height)

    zorzal = tm.load("assets/zorzal.obj")

    zorzal.apply_translation(-zorzal.centroid)
    zorzal.apply_scale(2.0 / zorzal.scale)

    with open(Path(os.path.dirname(__file__)) / "vertex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "fragment_program.glsl") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
    pipeline.use()
    vertex_lists = {}
    print(type(zorzal.geometry))

    for object_id, object_geometry in zorzal.geometry.items():
        mesh = {}
        object_vlist = tm.rendering.mesh_to_vertexlist(object_geometry)
        mesh["gpu_data"] = pipeline.vertex_list_indexed(
            len(object_vlist[4][1]) // 3, GL.GL_TRIANGLES, object_vlist[3]
        )

        mesh["texture"] = texture_2D_setup(object_geometry.visual.material.image)

        mesh["gpu_data"].position[:] = object_vlist[4][1]
        mesh["gpu_data"].normal[:] = object_vlist[5][1]
        mesh["gpu_data"].uv[:] = object_vlist[6][1]
        vertex_lists[object_id] = mesh

        # en vertex_list[6] vienen las coordenadas de textura o de color
        print(object_id, object_vlist[4][0], object_vlist[5][0], object_vlist[6][0])

    arcball = Arcball(
        np.identity(4),
        np.array((width, height), dtype=float),
        1,
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

        pipeline.use()
        pipeline["transform"] = arcball.pose.reshape(16, 1, order="F")

        for object_geometry in vertex_lists.values():
            GL.glBindTexture(GL.GL_TEXTURE_2D, object_geometry["texture"])
            object_geometry["gpu_data"].draw(pyglet.gl.GL_TRIANGLES)

    pyglet.app.run()
