import os
from pathlib import Path

import click
import numpy as np
import pyglet
from OpenGL import GL

from grafica.utils import load_pipeline


@click.command("sr_jengibre", short_help="Señor Jengibre")
@click.option("--width", type=int, default=800)
@click.option("--height", type=int, default=800)
@click.option("--x0", type=float, default=-0.01)
@click.option("--y0", type=float, default=0.0)
def sr_jengibre(width, height, x0, y0):
    win = pyglet.window.Window(width, height)

    vertices = np.array([-1, -1, 1, -1, 1,  1, -1,  1], dtype=np.float32)
    uv = np.array([0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0], dtype=np.float32)
    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    pipeline_iteration = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "iteration.glsl",
    )

    pipeline_visualization = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "visualization.glsl",
    )
    
    accumulation_buffer = pyglet.image.Texture.create(width, height)
    framebuffer_accumulation = pyglet.image.Framebuffer()
    framebuffer_accumulation.attach_texture(accumulation_buffer, attachment=GL.GL_COLOR_ATTACHMENT0)

    iteration_buffer = pyglet.image.Texture.create(width, height)
    framebuffer_iteration = pyglet.image.Framebuffer()
    framebuffer_iteration.attach_texture(iteration_buffer, attachment=GL.GL_COLOR_ATTACHMENT0)

    visualization_buffer = pyglet.image.Texture.create(width, height)
    framebuffer_visualization = pyglet.image.Framebuffer()
    framebuffer_visualization.attach_texture(visualization_buffer, attachment=GL.GL_COLOR_ATTACHMENT0)

    gpu_data = pipeline_visualization.vertex_list_indexed(4, GL.GL_TRIANGLES, indices)
    gpu_data.position[:] = vertices
    gpu_data.uv[:] = uv
    
    pipeline_iteration['resolution'] = (width, height)

    min_x, max_x = -3.0, 8.0  # Rango aproximado del atractor en x
    min_y, max_y = -3.0, 8.0  # Rango aproximado del atractor en y
    raw_pos = (x0, y0)  # Posición matemática real
    norm_pos = (  # Posición normalizada para visualización
        (x0 - min_x) / (max_x - min_x),
        (y0 - min_y) / (max_y - min_y)
    )

    @win.event
    def on_draw():
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        win.clear()
                   
        pipeline_visualization.use()
        GL.glBindTexture(visualization_buffer.target, visualization_buffer.id)   
        gpu_data.draw(GL.GL_TRIANGLES)     


    def update(dt, window):
        nonlocal raw_pos, norm_pos

        x, y = raw_pos
        raw_pos = (1 - y + abs(x), x)
        
        norm_pos = (
            (raw_pos[0] - min_x) / (max_x - min_x),
            (raw_pos[1] - min_y) / (max_y - min_y)
        )

        # render to texture
        # aquí pintamos un píxel de blanco si le toca ser el siguiente
        # y los que no, pierden algo de color
        framebuffer_iteration.bind()
        pipeline_iteration.use()
        GL.glBindTexture(iteration_buffer.target, iteration_buffer.id)
        pipeline_iteration['current_pos'] = norm_pos
        gpu_data.draw(GL.GL_TRIANGLES)
        framebuffer_iteration.unbind()

        # render to texture
        # aquí copiamos los resultados en dos texturas diferentes:
        # una, la textura que lee el programa anterior
        # la otra, la textura que se grafica
        # en ambos casos solo graficamos directamente el color de la textura
        framebuffer_accumulation.bind()
        pipeline_visualization.use()
        gpu_data.draw(GL.GL_TRIANGLES)
        framebuffer_accumulation.unbind()

        framebuffer_visualization.bind()
        pipeline_visualization.use()
        gpu_data.draw(GL.GL_TRIANGLES)
        framebuffer_visualization.unbind()


    pyglet.clock.schedule_interval(update, 1 / 120.0, win)
    pyglet.app.run()
