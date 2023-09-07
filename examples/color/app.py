import pyglet
from OpenGL import GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path

if __name__ == "__main__":
    width = 800
    height = 600
    win = pyglet.window.Window(width, height)

    vertices = np.array(
        [-1, -1, 0.0,  # inf izq
          1, -1, 0.0,  # if der
          1,  1, 0.0,  # sup der
         -1,  1, 0.0,  # sup izq
        ],
        dtype=np.float32,
    )

    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    with open(Path(os.path.dirname(__file__)) / ".." / "hello_world" / "vertex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "fragment_program.glsl") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    gpu_data = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, indices)
    gpu_data.position[:] = vertices
    # ¿por qué estamos comentando esto si usamos el shader que sí tiene este parámetro?
    #gpu_data.color[:] = vertex_colors

    pipeline.use()
    pipeline['resolution'] = np.array([width, height])
    win.program_state = {'total_time': 0.0}

    @win.event
    def on_draw():
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        win.clear()
        pipeline['time'] = win.program_state['total_time']
        pipeline.use()
        gpu_data.draw(GL.GL_TRIANGLES)

    def update(dt, window):
        window.program_state['total_time'] += dt

    pyglet.clock.schedule_interval(update, 1 / 60.0, win)
    pyglet.app.run()
