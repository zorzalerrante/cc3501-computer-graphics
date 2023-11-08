import os

import pyglet
import trimesh as tm
import OpenGL.GL as GL

import sys
if sys.path[0] != "":
    sys.path.insert(0, "")

import grafica.transformations as tr
from grafica.textures import texture_2D_setup

from pathlib import Path


class Pajarito(object):
    def __init__(self, *args, **kwargs):
        self.zorzal = tm.load("assets/zorzal.obj")

        self.zorzal.apply_translation(-self.zorzal.centroid)
        self.zorzal.apply_scale(1.0 / self.zorzal.scale)

        self.centroid = self.zorzal.centroid
        self.setup_program()

    def setup_program(self):
        with open(Path(os.path.dirname(__file__)) / "vertex_program.glsl") as f:
            vertex_source_code = f.read()

        with open(Path(os.path.dirname(__file__)) / "fragment_program.glsl") as f:
            fragment_source_code = f.read()

        vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")

        self.pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

        self.vertex_lists = {}

        for object_id, object_geometry in self.zorzal.geometry.items():
            mesh = {}
            object_vlist = tm.rendering.mesh_to_vertexlist(object_geometry)
            mesh["gpu_data"] = self.pipeline.vertex_list_indexed(
                len(object_vlist[4][1]) // 3, GL.GL_TRIANGLES, object_vlist[3]
            )

            mesh["texture"] = texture_2D_setup(object_geometry.visual.material.image)

            mesh["gpu_data"].position[:] = object_vlist[4][1]
            #mesh["gpu_data"].normal[:] = object_vlist[5][1]
            mesh["gpu_data"].uv[:] = object_vlist[6][1]
            self.vertex_lists[object_id] = mesh
            print(self.vertex_lists)

    def setup_transforms(self, view, projection):
        self.pipeline.use()
        self.pipeline["view"] = view.reshape(16, 1, order="F")
        self.pipeline["projection"] = projection.reshape(16, 1, order="F")

    def draw(self, transform=tr.identity()):
        self.pipeline.use()
        self.pipeline["transform"] = transform.reshape(16, 1, order="F")

        for object_geometry in self.vertex_lists.values():
            GL.glBindTexture(GL.GL_TEXTURE_2D, object_geometry["texture"])
            object_geometry["gpu_data"].draw(pyglet.gl.GL_TRIANGLES)

