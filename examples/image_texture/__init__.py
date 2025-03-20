import pyglet
from OpenGL import GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path
import click

from grafica.utils import load_pipeline


@click.command("image_texture", short_help="Visor de imágenes (versión textura)")
@click.argument("filename", type=str)
def image_viewer(filename):
    pic = pyglet.image.load(filename)

    win = pyglet.window.Window(pic.width, pic.height)

    texture = pic.get_texture()

    vertices = np.array([-1, -1, 1, -1, 1,  1, -1,  1, ], dtype=np.float32)
    uv = np.array([0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0], dtype=np.float32)
    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    pipeline_color = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program.glsl",
    )
    
    gpu_data = pipeline_color.vertex_list_indexed(4, GL.GL_TRIANGLES, indices)
    gpu_data.position[:] = vertices
    gpu_data.uv[:] = uv

    pipeline_greyscale = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program_grey.glsl",
    )

    print(texture.target, texture.id)
  
    pipelines = {True: pipeline_color, False: pipeline_greyscale}
    current_pipeline = True

    @win.event
    def on_key_press(symbol, modifiers):
        nonlocal current_pipeline
        if symbol == pyglet.window.key.SPACE:
            current_pipeline = not current_pipeline

    @win.event
    def on_draw():
        win.clear()

        pipelines[current_pipeline].use()
        GL.glBindTexture(texture.target, texture.id)
        gpu_data.draw(GL.GL_TRIANGLES)

    pyglet.app.run()
