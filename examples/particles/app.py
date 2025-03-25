import os
from collections import deque
from pathlib import Path
import random

import numpy as np
import OpenGL.GL as GL
import pyglet

import click

from grafica.utils import load_pipeline
from grafica.particle import Particle

@click.command("particles", short_help='Partículas simples con comportamiento basado en fuerzas')
@click.option("--width", type=int, default=900)
@click.option("--height", type=int, default=600)
@click.option("--max_ttl", type=int, default=3)
@click.option("--emission_rate", type=int, default=3, help="Partículas emitidas por frame")
def particulas(width, height, max_ttl, emission_rate):
    win = pyglet.window.Window(width, height)
    boundaries = (width, height)

    pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "point_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "point_fragment_program.glsl",
    )

    pipeline.use()
    pipeline["max_ttl"] = max_ttl
    pipeline['resolution'] = (width, height)

    # Colección de partículas
    particles = deque()
    particle_data = None
    
    # Tiempo global
    time = 0.0
    
    # Última posición del mouse
    last_mouse_pos = np.array([width // 2, height // 2], dtype=np.float32)

    def create_particle(position):
        """Función para crear partículas con propiedades personalizadas."""
        # Velocidad inicial aleatoria en todas direcciones
        angle = random.uniform(0, 2*np.pi)
        speed = random.uniform(10, 80)
        velocity = np.array([
            speed * np.cos(angle), 
            speed * np.sin(angle) - 30
        ], dtype=np.float32)
        
        # Aceleración inicial (gravedad)
        acceleration = np.array([0, -98], dtype=np.float32)
        
        # Masa y tiempo de vida variables
        mass = random.uniform(0.8, 1.2)
        ttl = max_ttl * random.uniform(0.7, 1.3)
        
        return Particle(position, velocity, acceleration, mass, ttl)

    def apply_forces(particle):
        """Función que aplica todas las fuerzas a una partícula."""
        # 1. Gravedad (siempre presente)
        particle.apply_force(np.array([0, -98], dtype=np.float32))
        
        # 2. Viento oscilante
        wind_force = np.array([20 * np.sin(time * 0.5), 0], dtype=np.float32)
        particle.apply_force(wind_force)
        
        # 3. Turbulencia aleatoria
        turbulence = np.random.uniform(-10, 10, 2).astype(np.float32)
        particle.apply_force(turbulence)
        
        # 4. Repulsión de los bordes
        width, height = boundaries
        edge_margin = 50
        
        # Calculamos distancias a los bordes
        dist_left = particle.position[0]
        dist_right = width - particle.position[0]
        dist_bottom = particle.position[1]
        dist_top = height - particle.position[1]
        
        # Creamos vector de repulsión
        repulsion = np.zeros(2, dtype=np.float32)
        
        # Aplicamos repulsión si está cerca de los bordes
        if dist_left < edge_margin:
            repulsion[0] += 5 * (edge_margin - dist_left)
        elif dist_right < edge_margin:
            repulsion[0] -= 5 * (edge_margin - dist_right)
            
        if dist_bottom < edge_margin:
            repulsion[1] += 5 * (edge_margin - dist_bottom)
        elif dist_top < edge_margin:
            repulsion[1] -= 5 * (edge_margin - dist_top)
            
        particle.apply_force(repulsion)

    def handle_boundary_collisions(particle):
        """Función para manejar colisiones con los límites de la ventana."""
        width, height = boundaries
        
        # Colisiones en X
        if particle.position[0] < 0:
            particle.position[0] = 0
            particle.velocity[0] *= -0.7  # Amortiguación
        elif particle.position[0] > width:
            particle.position[0] = width
            particle.velocity[0] *= -0.7
            
        # Colisiones en Y
        if particle.position[1] < 0:
            particle.position[1] = 0
            particle.velocity[1] *= -0.6  # Más amortiguación para el suelo
        elif particle.position[1] > height:
            particle.position[1] = height
            particle.velocity[1] *= -0.7

    @win.event
    def on_draw():
        win.clear()
        GL.glEnable(GL.GL_PROGRAM_POINT_SIZE)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        pipeline.use()

        if particle_data is not None:
            particle_data.draw(pyglet.gl.GL_POINTS)

    @win.event
    def on_mouse_motion(x, y, dx, dy):
        nonlocal last_mouse_pos
        # Actualizar posición del mouse
        last_mouse_pos = np.array([x, y], dtype=np.float32)
        
        # Emitir algunas partículas al mover el mouse
        for _ in range(2):
            # Variación en la posición
            jitter = np.random.uniform(-10, 10, 2).astype(np.float32)
            pos = last_mouse_pos + jitter
            particles.append(create_particle(pos))

    def emit_particles(dt, win):
        # Emitir continuamente partículas
        for _ in range(emission_rate):
            # Variación en la posición
            jitter = np.random.uniform(-15, 15, 2).astype(np.float32)
            pos = last_mouse_pos + jitter
            particles.append(create_particle(pos))

    def update_particle_system(dt, win):
        # Incrementar tiempo global
        nonlocal time, particle_data
        time += dt
        
        # Actualizar todas las partículas
        for particle in particles:
            # Actualizar estado físico
            particle.update(dt, apply_forces)
            
            # Manejar colisiones con los límites
            handle_boundary_collisions(particle)
        
        # Eliminar partículas muertas
        while particles and not particles[0].alive:
            particles.popleft()
        
        # Limitar número máximo de partículas
        max_particles = 500
        while len(particles) > max_particles:
            particles.popleft()
        
        # Actualizar datos en GPU
        if particle_data is not None:
            particle_data.delete()
            particle_data = None
        
        num_particles = len(particles)
        if num_particles > 0:
            # Crear vertex_list
            particle_data = pipeline.vertex_list(
                num_particles, pyglet.gl.GL_POINTS, position="f", ttl="f"
            )
            
            # Preparar datos de manera optimizada
            positions = np.zeros(num_particles * 2, dtype=np.float32)
            ttls = np.zeros(num_particles, dtype=np.float32)
            
            # Llenar arrays de manera optimizada
            for i, p in enumerate(particles):
                positions[i*2:i*2+2] = p.position
                ttls[i] = p.ttl
            
            # Enviar a GPU
            particle_data.position[:] = positions
            particle_data.ttl[:] = ttls

    # Programar actualización y emisión
    pyglet.clock.schedule(emit_particles, win)
    pyglet.clock.schedule(update_particle_system, win)
    
    pyglet.app.run()