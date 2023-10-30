import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path
from itertools import chain

from Box2D import b2PolygonShape, b2World

import sys

if sys.path[0] != "":
    sys.path.insert(0, "")

import grafica.transformations as tr

if __name__ == "__main__":
    width = 960
    height = 960
    window = pyglet.window.Window(width, height)

    # usaremos un cubo para graficar los objetos que pondremos en el mundo.
    # estos objetos serán cuadrados, así que es una buena manera de representarlos.
    cube = tm.load("assets/cube.off")
    # normalizamos el cubo.
    cube.apply_translation(-cube.centroid)
    cube.apply_scale(np.sqrt(3) / cube.scale)
    # nota: dividimos por la raíz de 3 porque el atributo scale entrega la diagonal de la caja que contiene al objeto.

    with open(Path(os.path.dirname(__file__)) / "vertex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "fragment_program.glsl") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    cube_vertex_list = tm.rendering.mesh_to_vertexlist(cube)

    cube_gpu = pipeline.vertex_list_indexed(
        len(cube_vertex_list[4][1]) // 3, GL.GL_TRIANGLES, cube_vertex_list[3]
    )

    cube_gpu.position[:] = cube_vertex_list[4][1]

    # construimos nuestra grilla para representar el "suelo" del mundo.
    grid_resolution = 100

    xv, yv = np.meshgrid(
        np.linspace(-1, 1, grid_resolution),
        np.linspace(-1, 1, grid_resolution),
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

    grid_gpu = pipeline.vertex_list_indexed(
        grid_resolution**2, GL.GL_LINES, grid_indices
    )

    grid_gpu.position[:] = grid_vertices.reshape(-1, 1, order="C")

    # elementos físicos
    # el mundo. si no le especificamos parámetros, asume que hay gravedad, y que las unidades son kilos, metros y segundos.
    world = b2World()
    # un objeto estático: en este caso, el suelo del mundo. este objeto nunca cambiará su posición y orientación.
    # ojo: box recibe la mitad de cada lado
    groundBody = world.CreateStaticBody(
        position=(0, -10),
        shapes=b2PolygonShape(box=(50, 10)),
    )

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        # esta función crea un cuerpo en la simulación al hacer clic.
        # el cuerpo es dinámico: se le pueden aplicar fuerzas.
        # tiene una posición inicial específica.
        body = world.CreateDynamicBody(position=(-10 + 20 * np.random.random(), 20))
        # se le debe asignar una forma (o "fixture"). en este caso, es una caja.
        box = body.CreatePolygonFixture(box=(0.5, 0.5), density=1, friction=0.3)

        # guardamos el cuerpo porque sus atributos de posición y orientación cambiarán con el tiempo.
        window.program_state['bodies'].append(body)

    time_step = 1.0 / 60

    window.program_state = {
        # simulación
        "bodies": [],
        "world": world,
        "total_time": 0.0,
        # parámetros para el integrador
        "vel_iters": 6,
        "pos_iters": 2,
        # despliegue gráfico
        "transform": tr.uniformScale(2),
        "view": tr.lookAt(
            np.array([0.0, 10, 15]),
            np.array([0, 4, 0]),  
            np.array([0.0, 0.1, 0]),
        ),
        "projection": tr.perspective(60, width / height, 0.001, 100.0),
        "grid_transform": tr.rotationX(np.pi / 2.0) @ tr.uniformScale(100),
    }

    def update_world(dt, window):
        # aquí actualizamos el mundo.
        window.program_state["total_time"] += dt
        world = window.program_state["world"]
        world.Step(
            dt, window.program_state["vel_iters"], window.program_state["pos_iters"]
        )

        # si ya se aplicaron las fuerzas, hay que eliminarlas de la simulación.
        # la única que se mantiene de manera automática es la gravedad.
        world.ClearForces()

    pyglet.clock.schedule_interval(update_world, time_step, window)

    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glLineWidth(1.0)

        window.clear()

        pipeline.use()

        pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        pipeline["projection"] = window.program_state["projection"].reshape(
            16, 1, order="F"
        )

        for body in window.program_state["bodies"]:
            # iteramos sobre cada uno de los cuerpos. en este caso, usamos el mismo modelo 3d para cada cuerpo.
            pipeline["transform"] = (
                tr.translate(body.position[0], body.position[1], 0.0)
                @ tr.rotationZ(body.angle)
            ).reshape(16, 1, order="F")
            cube_gpu.draw(pyglet.gl.GL_TRIANGLES)

        pipeline["transform"] = window.program_state["grid_transform"].reshape(
            16, 1, order="F"
        )

        grid_gpu.draw(GL.GL_LINES)

    pyglet.app.run()
