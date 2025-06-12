import os
import sys
import math
import random
from itertools import chain
from pathlib import Path
import click
import numpy as np
import pyglet
from pyglet.graphics.shader import Shader, ShaderProgram
from .cloth_utils import Cloth
from pyglet.math import Vec2
import pymunk

if sys.path[0] != "":
    sys.path.insert(0, "")

from grafica.utils import load_pipeline
import grafica.transformations as tr

@click.command("cloth_pymunk", short_help='Simulación interactiva de tela')
@click.option("--width", type=int, default=1920)
@click.option("--height", type=int, default=1080)
@click.option("--vertical_resolution", type=int, default=20)
@click.option("--horizontal_resolution", type=int, default=40)
@click.option("--spacing", type=int, default=20)
def cloth_pymunk(width, height, vertical_resolution, horizontal_resolution, spacing):

    win = pyglet.window.Window(width, height)
    win.set_caption("Tela Interactiva - SPACE: viento, ↑↓: rigidez, R: reset, Mouse: arrastrar")

    # Usar coordenadas de pantalla directamente (más simple)
    pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "point_vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "point_fragment_program.glsl",
    )

    # Proyección ortográfica simple que mapea 1:1 con coordenadas de pantalla
    projection = tr.ortho(0, width, 0, height, 0.001, 10.0)
    view = tr.lookAt(
        np.array([0, 0, 1.0]),
        np.array([0, 0, 0.0]),
        np.array([0.0, 1.0, 0.0]),
    )

    pipeline.use()
    pipeline["projection"] = projection.reshape(16, 1, order="F")
    pipeline["view"] = view.reshape(16, 1, order="F")

    # Estado de la simulación
    class SimulationState:
        def __init__(self):
            self.wind_active = False
            self.wind_strength = 8000  # Más fuerte para ser visible
            self.mouse_pos = (0, 0)
            self.dragging = False
            self.drag_body = None
            self.drag_joint = None
            self.material_stiffness = 5000.0  # Muy bajo para empezar
            self.material_damping = 800  # Mucha amortiguación
            self.time = 0.0
    
    state = SimulationState()

    def setup_cloth():
        # Crear tela en coordenadas de pantalla
        start_x = width // 2 - (horizontal_resolution * spacing) // 2
        start_y = height * 0.8  # Más cerca de la parte superior
        
        win.cloth = Cloth(
            width, height,
            Vec2(start_x, start_y),
            horizontal_resolution, vertical_resolution, spacing,
        )

        win.node_data = pipeline.vertex_list(
            len(win.cloth.vertices), pyglet.gl.GL_POINTS, position="f"
        )

        win.joint_data = pipeline.vertex_list_indexed(
            len(win.cloth.vertices), pyglet.gl.GL_LINES,
            tuple(chain(*(j for j in win.cloth.joints))),
            position="f",
        )

        # Configurar espacio de física en coordenadas de pantalla
        win.space = pymunk.Space()
        win.space.gravity = (0, -1000)  # Gravedad muy suave
        win.space.damping = 0.95  # Mucha amortiguación global

        win.bodies = {}
        win.springs = []
        cloth_group = 1

        # Crear cuerpos para vértices
        for i, vertex in enumerate(win.cloth.vertices):
            # Anclar más puntos en la parte superior para estabilidad
            row = i // horizontal_resolution
            col = i % horizontal_resolution
            
            if row == 0 and col % 8 == 0:  # Anclar cada 8 puntos en la fila superior
                b = pymunk.Body(body_type=pymunk.Body.STATIC)
            else:
                mass = 8.0  # Masa alta para estabilidad
                b = pymunk.Body(mass, 0.1)

            b.position = pymunk.Vec2d(vertex.position.x, vertex.position.y)
            
            s = pymunk.Circle(b, 3)  # Radio muy pequeño
            s.filter = pymunk.ShapeFilter(group=cloth_group)
            s.friction = 0.1
            
            win.space.add(b, s)
            win.bodies[i] = b

        # Crear resortes muy suaves
        for joint in win.cloth.joints:
            a = win.bodies[joint[0]]
            b = win.bodies[joint[1]]
            rest_length = a.position.get_distance(b.position)
            
            # Solo resortes principales (no diagonales para simplicidad)
            row_diff = abs(joint[0] // horizontal_resolution - joint[1] // horizontal_resolution)
            col_diff = abs(joint[0] % horizontal_resolution - joint[1] % horizontal_resolution)
            
            if (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1):
                spring = pymunk.DampedSpring(
                    a, b, (0, 0), (0, 0),
                    rest_length=rest_length,
                    stiffness=state.material_stiffness,
                    damping=state.material_damping
                )
                win.space.add(spring)
                win.springs.append(spring)

    def update_cloth_system(dt, win):
        state.time += dt
        
        # Aplicar viento más visible
        if state.wind_active:
            wind_force = state.wind_strength * (1.0 + 0.5 * math.sin(state.time * 2))
            
            for body in win.bodies.values():
                if body.body_type != pymunk.Body.STATIC:
                    # Viento horizontal más fuerte
                    force = (wind_force, wind_force * 0.1)
                    body.apply_force_at_world_point(force, body.position)

        # Muchas subdivisiones para estabilidad máxima
        subdivisions = 20
        dt_sub = dt / subdivisions
        
        for _ in range(subdivisions):
            win.space.step(dt_sub)

    @win.event
    def on_draw():
        win.clear()

        # Actualizar posiciones directamente en coordenadas de pantalla
        positions = []
        for i, body in win.bodies.items():
            positions.extend([body.position.x, body.position.y, 0.0])

        win.node_data.position[:] = positions
        win.joint_data.position[:] = positions

        # Dibujar
        pipeline.use()
        win.node_data.draw(pyglet.gl.GL_POINTS)
        win.joint_data.draw(pyglet.gl.GL_LINES)

        # UI simple
        try:
            info = f"Viento: {'ON' if state.wind_active else 'OFF'} | Rigidez: {state.material_stiffness:.0f}"
            label = pyglet.text.Label(
                info, font_name='Arial', font_size=14,
                x=10, y=height - 30, color=(255, 255, 255, 255)
            )
            label.draw()
        except:
            pass

    @win.event
    def on_mouse_press(x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT:
            print(f"Click en: ({x}, {y})")
            
            # Buscar el cuerpo más cercano
            closest_body = None
            min_distance = float('inf')
            
            for i, body in win.bodies.items():
                if body.body_type != pymunk.Body.STATIC:
                    # Las coordenadas ahora coinciden directamente
                    distance = math.sqrt((body.position.x - x)**2 + (body.position.y - y)**2)
                    print(f"Cuerpo {i} en ({body.position.x:.1f}, {body.position.y:.1f}), distancia: {distance:.1f}")
                    
                    if distance < min_distance and distance < 80:  # Área generosa
                        min_distance = distance
                        closest_body = body
            
            if closest_body:
                print(f"Arrastrando cuerpo a distancia {min_distance:.1f}")
                state.dragging = True
                state.drag_body = closest_body
                
                # Crear arrastre con fuerza mucho mayor
                drag_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
                drag_body.position = x, y
                
                # Usar DampedSpring en lugar de PinJoint para mejor respuesta
                joint = pymunk.DampedSpring(
                    drag_body, closest_body, 
                    (0, 0), (0, 0),
                    rest_length=0,  # Longitud cero para "pegar" al mouse
                    stiffness=500000,  # MUCHO más rígido que los resortes de la tela
                    damping=10000   # Con mucha amortiguación para suavidad
                )
                
                win.space.add(drag_body, joint)
                state.drag_joint = (drag_body, joint)
                
                print(f"DampedSpring creado con stiffness {joint.stiffness} (100x más que tela)")
            else:
                print("No se encontró cuerpo cercano")

    @win.event
    def on_mouse_release(x, y, button, modifiers):
        if button == pyglet.window.mouse.LEFT and state.dragging:
            print("Soltando arrastre")
            state.dragging = False
            if state.drag_joint:
                drag_body, joint = state.drag_joint
                win.space.remove(drag_body, joint)
                state.drag_joint = None
            state.drag_body = None

    @win.event
    def on_mouse_motion(x, y, dx, dy):
        state.mouse_pos = (x, y)

    @win.event  
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        """Este evento se activa específicamente cuando se arrastra con el mouse"""
        if state.dragging and state.drag_joint:
            drag_body, joint = state.drag_joint
            old_pos = drag_body.position
            drag_body.position = x, y
            print(f"Arrastrando de ({old_pos.x:.1f}, {old_pos.y:.1f}) a ({x}, {y})")

    @win.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            state.wind_active = not state.wind_active
            print(f"Viento: {'ON' if state.wind_active else 'OFF'}")
        
        elif symbol == pyglet.window.key.R:
            print("Reiniciando...")
            setup_cloth()
        
        elif symbol == pyglet.window.key.UP:
            state.material_stiffness = min(state.material_stiffness * 1.2, 15000)
            update_spring_properties()
            print(f"Rigidez: {state.material_stiffness:.0f}")
        
        elif symbol == pyglet.window.key.DOWN:
            state.material_stiffness = max(state.material_stiffness * 0.8, 1000)
            update_spring_properties()
            print(f"Rigidez: {state.material_stiffness:.0f}")

    def update_spring_properties():
        """Actualiza las propiedades de los resortes"""
        for spring in win.springs:
            spring.stiffness = state.material_stiffness

    # Inicializar
    setup_cloth()
    
    # Programar actualizaciones
    pyglet.clock.schedule(update_cloth_system, win)
    pyglet.app.run()