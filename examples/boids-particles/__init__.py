import numpy as np
import pyglet
import OpenGL.GL as GL

import grafica.transformations as tr
from .world import World
import os

from pathlib import Path
from grafica.utils import load_pipeline
import click

# variables del estado del programa
program_state = {
    "paused": False,
    "bird_camera": False,
    "view_matrix": None,
    "projection_matrix": None,
}

# variables del mundo que simularemos
world_parameters = {
    "vision": {"min": 60, "max": 200, "default": 100},
    "cohere_factor": {"min": 0.0001, "max": 0.001, "default": 0.00075},
    "separation_factor": {"min": 0.0001, "max": 0.01, "default": 0.0075},
    "match_factor": {"min": 0.0001, "max": 0.01, "default": 0.0075},
    "distance": {"min": 20, "max": 60, "default": 25},
    "speed": {"min": 0.01, "max": 1.0, "default": 0.75},
}

@click.command("boids_particles", short_help='Simulador de vuelo de pajaritos usando Agent-Based Modeling (versión partículas)')
@click.option("--n_pajaritos", type=int, default=60)
@click.option("--width", type=int, default=1024)
@click.option("--height", type=int, default=768)
def boids_particles(n_pajaritos, width, height):
    # noten que el tamaño de la ventana es independiente del tamaño del mundo.
    window = pyglet.window.Window(width=width, height=height)

    pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program.glsl",
    )

    pipeline.use()
    pipeline['resolution'] = (width, height)

    # este es el mundo a simular.
    flock = World(
        n_pajaritos,
        # y muchos parámetros
        width=width,
        height=height,
        speed=world_parameters["speed"]["default"],
        vision=world_parameters["vision"]["default"],
        distance=world_parameters["distance"]["default"],
        cohere_factor=world_parameters["cohere_factor"]["default"],
        separation_factor=world_parameters["separation_factor"]["default"],
        match_factor=world_parameters["match_factor"]["default"],
    )
    
    # aquí guardaremos a nuestros pajaritos para graficación
    particle_data = None

    # esta función ejecutará un paso de la simulación
    def tick(time):
        if not program_state["paused"]:
            flock.step()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.P:
            program_state["paused"] = not program_state["paused"]

    @window.event
    def on_draw():
        GL.glClearColor(0.85, 0.85, 0.85, 1.0)
        GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        window.clear()

        build_particle_data()

        if particle_data is not None:
            pipeline.use()
            particle_data.draw(pyglet.gl.GL_TRIANGLES)        

    def build_particle_data():
        nonlocal particle_data
        if particle_data is not None:
            particle_data.delete()
            particle_data = None

        positions = np.zeros(n_pajaritos * 3 * 2, dtype=np.float32)
        colors = np.zeros(n_pajaritos * 3 * 3, dtype=np.float32)
        
        for i, boid in enumerate(flock.iter_agents()):
            angle = np.arctan2(boid.velocity[1], boid.velocity[0])

            # Tamaño del triángulo
            size = 10.0

            # Vértices del triángulo orientado en la dirección del movimiento
            # El primer vértice es la punta, los otros dos forman la base
            v1 = (boid.pos[0] + size * np.cos(angle), 
                boid.pos[1] + size * np.sin(angle))
            v2 = (boid.pos[0] + size * 0.5 * np.cos(angle + np.pi * 2/3), 
                boid.pos[1] + size * 0.5 * np.sin(angle + np.pi * 2/3))
            v3 = (boid.pos[0] + size * 0.5 * np.cos(angle - np.pi * 2/3), 
                boid.pos[1] + size * 0.5 * np.sin(angle - np.pi * 2/3))

            positions[i*6:i*6+2] = v1
            positions[i*6+2:i*6+4] = v2
            positions[i*6+4:i*6+6] = v3

            r = min(1.0, boid.current_speed / world_parameters["speed"]["max"])
            g = min(1.0, 1.0 - r)
            b = 0.5

            # Asignar los colores a cada vértice del triángulo
            for j in range(3):
                colors[i*9+j*3:i*9+j*3+3] = (r, g, b)

        particle_data = pipeline.vertex_list(
            n_pajaritos * 3, pyglet.gl.GL_TRIANGLES, position="f", color="f"
        )

        particle_data.position[:] = positions
        particle_data.color[:] = colors
        
    

    pyglet.clock.schedule_interval(tick, 1 / 60)
    pyglet.app.run()


if __name__ == "__main__":
    main()
