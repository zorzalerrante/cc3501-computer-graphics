import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path
from itertools import chain

# pymunk es una biblioteca de simulación física que utiliza el motor chipmunk
import pymunk

import click

import grafica.transformations as tr


@click.command(
    "falling_boxes", short_help="Ejemplo de uso de Pymunk con vectores de velocidad"
)
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=960)
def falling_boxes(width, height):
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
    world = pymunk.Space()
    world.gravity = (0, -9.81)

    # un objeto estático: en este caso, el suelo del mundo.
    # Movemos la línea central a Y=-0.05 para que la superficie superior esté exactamente en Y=0
    groundBody = pymunk.Segment(world.static_body, (-50, -0.05), (50, -0.05), 0.1)
    groundBody.friction = 1.0

    world.add(groundBody)

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        # esta función crea un cuerpo en la simulación al hacer clic.
        # el cuerpo es dinámico: se le pueden aplicar fuerzas.
        # tiene una posición inicial específica.

        mass = 1.0
        size = 0.5
        points = [(-size, -size), (-size, size), (size, size), (size, -size)]

        body = pymunk.Body(mass, pymunk.moment_for_poly(mass, points, (0, 0)))

        # NEW: Si es click derecho, aplicar velocidad inicial hacia el centro de la pantalla
        if button == pyglet.window.mouse.RIGHT:
            # Convertir coordenadas de pantalla a mundo
            center_x, center_y = width // 2, height // 2
            vel_x = (center_x - x) * 0.02  # Factor de escala
            vel_y = (center_y - y) * 0.02
            body.position = (-10 + 20 * np.random.random(), 20)
            body.velocity = (vel_x, vel_y)
        else:
            body.position = (-10 + 20 * np.random.random(), 20)

        shape = pymunk.Poly(body, points)
        shape.friction = 1
        world.add(body, shape)

        # guardamos el cuerpo porque sus atributos de posición y orientación cambiarán con el tiempo.
        window.program_state["bodies"].append(body)
        print(f"added body at {body.position}, velocity: {body.velocity}")

    # NEW: Función para crear vertex list de vectores de velocidad
    def create_velocity_vectors():
        vertices = []
        bodies = window.program_state["bodies"]

        for body in bodies:
            if len(body.shapes) == 0:  # Body fue removido
                continue

            # Posición del cuerpo
            pos_x, pos_y = body.position
            vel_x, vel_y = body.velocity

            # Solo dibujar si hay velocidad significativa
            speed = np.sqrt(vel_x**2 + vel_y**2)
            if speed < 0.1:  # Umbral mínimo para mostrar vector
                continue

            # Escalar velocidad para visualización (factor de escala)
            scale = 0.5
            end_x = pos_x + vel_x * scale
            end_y = pos_y + vel_y * scale

            # Línea desde el centro del objeto hasta la punta del vector
            vertices.extend([pos_x, pos_y, 0.0, end_x, end_y, 0.0])  # inicio  # fin

        # Crear vertex list solo si hay datos
        if vertices:
            velocity_gpu = pipeline.vertex_list(len(vertices) // 3, GL.GL_LINES)
            velocity_gpu.position[:] = vertices
            return velocity_gpu
        return None

    time_step = 1.0 / 60

    window.program_state = {
        # simulación
        "bodies": [],
        "total_time": 0.0,
        # parámetros para el integrador
        "vel_iters": 6,
        "pos_iters": 2,
        # NEW: mostrar vectores de velocidad
        "show_velocity": True,
        "velocity_gpu": None,  # Se creará dinámicamente
        # NEW: tipo de proyección
        "use_perspective": True,
        # despliegue gráfico
        "transform": tr.uniformScale(2),
        # view y projection se configuran en update_projection()
        # Grilla alineada con el piso físico en Y=0
        "grid_transform": tr.translate(0, 0, 0)
        @ tr.rotationX(np.pi / 2.0)
        @ tr.uniformScale(100),
    }

    # NEW: Función para actualizar matriz de proyección y vista
    def update_projection():
        if window.program_state["use_perspective"]:
            # Vista 3D: perspectiva con cámara diagonal
            window.program_state["projection"] = tr.perspective(
                60, width / height, 0.001, 100.0
            )
            window.program_state["view"] = tr.lookAt(
                np.array([0.0, 10, 15]),  # Cámara diagonal
                np.array([0, 4, 0]),  # Mirando hacia el centro
                np.array([0.0, 0.1, 0]),  # Up vector
            )
        else:
            # Vista 2D: ortográfica con cámara lateral (como juegos de plataformas)
            ortho_size = 15.0  # Ajustar este valor para zoom
            aspect = width / height
            window.program_state["projection"] = tr.ortho(
                -ortho_size * aspect,
                ortho_size * aspect,  # left, right
                -ortho_size,
                ortho_size,  # bottom, top
                0.001,
                100.0,  # near, far
            )
            window.program_state["view"] = tr.lookAt(
                np.array([0.0, 8, 25]),  # Cámara lateral desde Z positivo
                np.array([0, 8, 0]),  # Mirando hacia el centro del mundo
                np.array([0.0, 1.0, 0]),  # Up vector vertical puro
            )

    # NEW: Toggle para mostrar/ocultar vectores de velocidad
    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.V:
            window.program_state["show_velocity"] = not window.program_state[
                "show_velocity"
            ]
            print(
                f"Velocity vectors: {'ON' if window.program_state['show_velocity'] else 'OFF'}"
            )
        elif symbol == pyglet.window.key.C:
            # Limpiar todos los cuerpos
            for body in window.program_state["bodies"]:
                world.remove(body, *body.shapes)
            window.program_state["bodies"].clear()
            print("Cleared all bodies")
        elif symbol == pyglet.window.key.P:
            # Cambiar entre vista perspectiva y ortográfica
            window.program_state["use_perspective"] = not window.program_state[
                "use_perspective"
            ]
            update_projection()
            projection_type = (
                "Perspective"
                if window.program_state["use_perspective"]
                else "Orthographic (2D)"
            )
            print(f"Projection: {projection_type}")

    def update_world(dt, window):
        # aquí actualizamos el mundo.
        window.program_state["total_time"] += dt
        world.step(dt)

        # Crear vectores de velocidad
        window.program_state["velocity_gpu"] = create_velocity_vectors()

        # Remover cuerpos que han caído muy bajo (limpieza automática)
        bodies_to_remove = []
        for body in window.program_state["bodies"]:
            if body.position.y < -20:
                bodies_to_remove.append(body)

        for body in bodies_to_remove:
            world.remove(body, *body.shapes)
            window.program_state["bodies"].remove(body)

    # Inicializar proyección y vista
    update_projection()

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

        # Dibujar cuerpos (cajas)
        for body in window.program_state["bodies"]:
            # iteramos sobre cada uno de los cuerpos. en este caso, usamos el mismo modelo 3d para cada cuerpo.
            pipeline["transform"] = (
                tr.translate(body.position[0], body.position[1], 0.0)
                @ tr.rotationZ(body.angle)
            ).reshape(16, 1, order="F")
            cube_gpu.draw(pyglet.gl.GL_TRIANGLES)

        # NEW: Dibujar vectores de velocidad
        if (
            window.program_state["show_velocity"]
            and window.program_state["velocity_gpu"]
        ):
            GL.glLineWidth(3.0)  # Líneas más gruesas para los vectores
            pipeline["transform"] = tr.identity().reshape(16, 1, order="F")

            window.program_state["velocity_gpu"].draw(GL.GL_LINES)

            GL.glLineWidth(1.0)  # Restaurar grosor original

        # Dibujar grilla del suelo
        pipeline["transform"] = window.program_state["grid_transform"].reshape(
            16, 1, order="F"
        )
        grid_gpu.draw(GL.GL_LINES)

    print("Controles:")
    print("- Click izquierdo: Crear caja que cae")
    print("- Click derecho: Crear caja con velocidad inicial hacia el centro")
    print("- Tecla V: Mostrar/ocultar vectores de velocidad")
    print("- Tecla P: Cambiar entre vista 3D (perspectiva) y 2D (ortográfica)")
    print("- Tecla C: Limpiar todas las cajas")

    pyglet.app.run()
