import os.path
import sys
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL
from pyglet.window import key

import click

import grafica.transformations as tr
from grafica.utils import load_pipeline
from grafica.scenegraph import Scenegraph
from grafica.scenegraph_premade import unit_axes_node


def evaluate_bezier(control_points, t):
    """
    Evalúa una curva de Bézier cúbica en el parámetro t.
    control_points: lista de 4 puntos (arrays de numpy de 3 elementos)
    t: parámetro en [0, 1]
    """
    # Algoritmo de De Casteljau
    if len(control_points) != 4:
        raise ValueError("Se requieren exactamente 4 puntos de control")
    
    # Primera iteración: interpolación lineal entre puntos adyacentes
    q0 = (1 - t) * control_points[0] + t * control_points[1]
    q1 = (1 - t) * control_points[1] + t * control_points[2]
    q2 = (1 - t) * control_points[2] + t * control_points[3]
    
    # Segunda iteración
    r0 = (1 - t) * q0 + t * q1
    r1 = (1 - t) * q1 + t * q2
    
    # Tercera iteración (resultado final)
    s = (1 - t) * r0 + t * r1
    
    return s


def create_line_mesh(points, color):
    """
    Crea una malla de líneas a partir de una lista de puntos.
    """
    vertices = []
    indices = []
    colors = []
    
    for i, point in enumerate(points):
        vertices.extend([point[0], point[1], point[2]])
        colors.extend(color)
        if i > 0:
            indices.extend([i-1, i])
    
    return vertices, indices, colors


def generate_curve_points(control_points, resolution=50):
    """
    Genera puntos a lo largo de una curva de Bézier.
    """
    points = []
    for i in range(resolution + 1):
        t = i / resolution
        point = evaluate_bezier(control_points, t)
        points.append(point)
    return points


def create_bezier_line_node(control_points, color, resolution=50):
    """
    Crea un nodo de malla de línea para una curva de Bézier.
    """
    points = generate_curve_points(control_points, resolution)
    vertices, indices, colors = create_line_mesh(points, color)
    
    # Crear estructura de nodo compatible con el grafo de escena
    node = {
        'name': 'bezier_curve',
        'mesh': {
            'n_vertices': len(vertices) // 3,
            'vertices': vertices,
            'indices': indices,
            'texture': None
        },
        'attributes': {
            'position': vertices,
            'color': colors
        },
        'indices': indices,
        'GL_TYPE': GL.GL_LINES,
        'children': []
    }
    
    return node


def create_control_polygon_node(control_points, color):
    """
    Crea un nodo de malla de línea para el polígono de control.
    """
    vertices = []
    indices = []
    colors = []
    
    for i, point in enumerate(control_points):
        vertices.extend([point[0], point[1], point[2]])
        colors.extend(color)
        if i > 0:
            indices.extend([i-1, i])
    
    # Crear estructura de nodo
    node = {
        'name': 'control_polygon',
        'mesh': {
            'n_vertices': len(vertices) // 3,
            'vertices': vertices,
            'indices': indices,
            'texture': None
        },
        'attributes': {
            'position': vertices,
            'color': colors
        },
        'indices': indices,
        'GL_TYPE': GL.GL_LINES,
        'children': []
    }
    
    return node


@click.command("camera_path", short_help="Trayectoria de cámara con curvas de Bézier")
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=960)
def camera_path(width, height):
    window = pyglet.window.Window(width, height)

    # Cargar pipelines
    solar_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "mesh_vertex_program.glsl",
        Path(os.path.dirname(__file__))
        / ".."
        / "hello_world"
        / "fragment_program.glsl",
    )

    axis_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "line_vertex_program.glsl",
        Path(os.path.dirname(__file__))
        / ".."
        / "hello_world"
        / "fragment_program.glsl",
    )

    # Crear grafo de escena
    graph = Scenegraph("root")
    graph.load_and_register_mesh('sphere', "assets/sphere.off")
    graph.register_mesh('axis', unit_axes_node())
    graph.register_pipeline('solar_pipeline', solar_pipeline)
    graph.register_pipeline('axis_pipeline', axis_pipeline)

    # Definir puntos de control para trayectoria de cámara (loop cerrado)
    camera_control_points = [
        np.array([5.0, 3.0, 5.0]),    # P0
        np.array([7.0, 5.0, 0.0]),    # P1
        np.array([5.0, 4.0, -5.0]),   # P2
        np.array([0.0, 2.0, -7.0])    # P3 (conectará con el siguiente segmento)
    ]
    
    # Puntos para el segundo segmento (para hacer el loop)
    camera_control_points_2 = [
        np.array([0.0, 2.0, -7.0]),   # P0 (mismo que P3 anterior)
        np.array([-5.0, 3.0, -5.0]),  # P1
        np.array([-7.0, 4.0, 0.0]),   # P2
        np.array([-5.0, 2.0, 5.0])    # P3
    ]
    
    # Puntos para el tercer segmento (cierra el loop)
    camera_control_points_3 = [
        np.array([-5.0, 2.0, 5.0]),   # P0
        np.array([-3.0, 1.0, 7.0]),   # P1
        np.array([3.0, 2.0, 7.0]),    # P2
        np.array([5.0, 3.0, 5.0])     # P3 (vuelve al inicio)
    ]

    # Definir puntos de control para hacia dónde mira la cámara (también loop)
    lookat_control_points = [
        np.array([0.0, 0.0, 0.0]),    # Mira al centro
        np.array([1.0, 0.5, 0.0]),    # Control 1
        np.array([0.0, 0.5, -1.0]),   # Control 2
        np.array([-1.0, 0.0, 0.0])    # Punto final
    ]
    
    lookat_control_points_2 = [
        np.array([-1.0, 0.0, 0.0]),   # Continuación
        np.array([0.0, -0.5, 1.0]),   # Control 1
        np.array([1.0, -0.5, 0.0]),   # Control 2
        np.array([0.0, 0.0, 0.0])     # Vuelve al centro
    ]

    # Registrar mallas de curvas
    graph.register_mesh('camera_curve_1', create_bezier_line_node(camera_control_points, [1.0, 0.5, 0.5], 30))
    graph.register_mesh('camera_curve_2', create_bezier_line_node(camera_control_points_2, [1.0, 0.5, 0.5], 30))
    graph.register_mesh('camera_curve_3', create_bezier_line_node(camera_control_points_3, [1.0, 0.5, 0.5], 30))
    
    graph.register_mesh('lookat_curve_1', create_bezier_line_node(lookat_control_points, [0.5, 0.5, 1.0], 30))
    graph.register_mesh('lookat_curve_2', create_bezier_line_node(lookat_control_points_2, [0.5, 0.5, 1.0], 30))
    
    # Registrar polígonos de control
    graph.register_mesh('camera_polygon_1', create_control_polygon_node(camera_control_points, [0.5, 0.0, 0.0]))
    graph.register_mesh('camera_polygon_2', create_control_polygon_node(camera_control_points_2, [0.5, 0.0, 0.0]))
    graph.register_mesh('camera_polygon_3', create_control_polygon_node(camera_control_points_3, [0.5, 0.0, 0.0]))
    
    graph.register_mesh('lookat_polygon_1', create_control_polygon_node(lookat_control_points, [0.0, 0.0, 0.5]))
    graph.register_mesh('lookat_polygon_2', create_control_polygon_node(lookat_control_points_2, [0.0, 0.0, 0.5]))

    # Crear escena de ejemplo (sistema solar completo)
    # Sol
    graph.add_transform("sun_geometry", tr.uniformScale(0.8))
    graph.add_mesh_instance("sun_mesh", 'sphere', 'solar_pipeline', 
                           color=np.array((1.0, 0.73, 0.03)))
    graph.add_mesh_instance("sun_axis", 'axis', 'axis_pipeline', 
                           transform=tr.uniformScale(1))
    
    graph.add_edge("root", "sun_geometry")
    graph.add_edge("sun_geometry", "sun_mesh")
    graph.add_edge("root", "sun_axis")

    # Tierra
    graph.add_transform("earth", tr.translate(2.5, 0.0, 0.0))
    graph.add_transform("earth_geometry", tr.uniformScale(0.3))
    graph.add_mesh_instance("earth_mesh", 'sphere', 'solar_pipeline', 
                           color=np.array((0.0, 0.59, 0.78)))
    graph.add_mesh_instance("earth_axis", 'axis', 'axis_pipeline', 
                           transform=tr.uniformScale(0.5))
    
    graph.add_edge("root", "earth")
    graph.add_edge("earth", "earth_geometry")
    graph.add_edge("earth_geometry", "earth_mesh")
    graph.add_edge("earth", "earth_axis")

    # Luna
    graph.add_transform("moon", tr.translate(0.5, 0.0, 0.0))
    graph.add_transform("moon_geometry", tr.uniformScale(0.1))
    graph.add_mesh_instance("moon_mesh", 'sphere', 'solar_pipeline', 
                           color=np.array((0.6, 0.6, 0.6)))
    graph.add_mesh_instance("moon_axis", 'axis', 'axis_pipeline', 
                           transform=tr.uniformScale(0.25))
    
    graph.add_edge("earth", "moon")
    graph.add_edge("moon", "moon_geometry")
    graph.add_edge("moon_geometry", "moon_mesh")
    graph.add_edge("moon", "moon_axis")

    # Agregar las curvas al grafo
    graph.add_mesh_instance("camera_curve_instance_1", 'camera_curve_1', 'axis_pipeline')
    graph.add_mesh_instance("camera_curve_instance_2", 'camera_curve_2', 'axis_pipeline')
    graph.add_mesh_instance("camera_curve_instance_3", 'camera_curve_3', 'axis_pipeline')
    graph.add_mesh_instance("lookat_curve_instance_1", 'lookat_curve_1', 'axis_pipeline')
    graph.add_mesh_instance("lookat_curve_instance_2", 'lookat_curve_2', 'axis_pipeline')
    
    graph.add_edge("root", "camera_curve_instance_1")
    graph.add_edge("root", "camera_curve_instance_2")
    graph.add_edge("root", "camera_curve_instance_3")
    graph.add_edge("root", "lookat_curve_instance_1")
    graph.add_edge("root", "lookat_curve_instance_2")
    
    # Agregar polígonos de control
    graph.add_mesh_instance("camera_polygon_instance_1", 'camera_polygon_1', 'axis_pipeline')
    graph.add_mesh_instance("camera_polygon_instance_2", 'camera_polygon_2', 'axis_pipeline')
    graph.add_mesh_instance("camera_polygon_instance_3", 'camera_polygon_3', 'axis_pipeline')
    graph.add_mesh_instance("lookat_polygon_instance_1", 'lookat_polygon_1', 'axis_pipeline')
    graph.add_mesh_instance("lookat_polygon_instance_2", 'lookat_polygon_2', 'axis_pipeline')
    
    graph.add_edge("root", "camera_polygon_instance_1")
    graph.add_edge("root", "camera_polygon_instance_2")
    graph.add_edge("root", "camera_polygon_instance_3")
    graph.add_edge("root", "lookat_polygon_instance_1")
    graph.add_edge("root", "lookat_polygon_instance_2")

    # Agregar puntos de control como esferas pequeñas
    all_camera_points = camera_control_points + camera_control_points_2[1:] + camera_control_points_3[1:-1]
    all_lookat_points = lookat_control_points + lookat_control_points_2[1:]
    
    # Puntos de control de cámara (rojos)
    for i, point in enumerate(all_camera_points):
        graph.add_transform(f"cam_control_{i}", tr.translate(*point) @ tr.uniformScale(0.15))
        graph.add_mesh_instance(f"cam_control_mesh_{i}", 'sphere', 'solar_pipeline',
                               color=np.array((1.0, 0.0, 0.0)))
        
        graph.add_edge("root", f"cam_control_{i}")
        graph.add_edge(f"cam_control_{i}", f"cam_control_mesh_{i}")

    # Puntos de control de look-at (azules)
    for i, point in enumerate(all_lookat_points):
        graph.add_transform(f"lookat_control_{i}", tr.translate(*point) @ tr.uniformScale(0.1))
        graph.add_mesh_instance(f"lookat_control_mesh_{i}", 'sphere', 'solar_pipeline',
                               color=np.array((0.0, 0.0, 1.0)))
        
        graph.add_edge("root", f"lookat_control_{i}")
        graph.add_edge(f"lookat_control_{i}", f"lookat_control_mesh_{i}")

    # Agregar indicador de posición actual de cámara (esfera verde)
    graph.add_transform("current_cam_pos", tr.translate(*camera_control_points[0]) @ tr.uniformScale(0.12))
    graph.add_mesh_instance("current_cam_mesh", 'sphere', 'solar_pipeline',
                           color=np.array((0.0, 1.0, 0.0)))
    
    graph.add_edge("root", "current_cam_pos")
    graph.add_edge("current_cam_pos", "current_cam_mesh")

    # Agregar indicador de posición de look-at (esfera amarilla)
    graph.add_transform("current_lookat_pos", tr.translate(*lookat_control_points[0]) @ tr.uniformScale(0.08))
    graph.add_mesh_instance("current_lookat_mesh", 'sphere', 'solar_pipeline',
                           color=np.array((1.0, 1.0, 0.0)))
    
    graph.add_edge("root", "current_lookat_pos")
    graph.add_edge("current_lookat_pos", "current_lookat_mesh")

    # Variables de estado
    total_time = 0.0
    animation_speed = 0.2
    is_paused = False
    show_curves = True
    show_control_polygon = False
    current_camera_mode = "fixed"  # "fixed" o "path"

    # Vista fija inicial (para ver los puntos de control)
    fixed_view = tr.lookAt(np.array([10, 8, 10]), np.array([0, 0, 0]), np.array([0, 1, 0]))
    projection = tr.perspective(45, float(width) / float(height), 0.1, 100)

    # Registrar ambas vistas
    graph.register_view_transform(fixed_view, 'fixed', set_as_current=True)
    graph.register_view_transform(fixed_view, 'path', set_as_current=False)  # Se actualizará dinámicamente
    graph.set_global_attributes(projection=projection)

    def evaluate_piecewise_bezier(t_global, segments):
        """
        Evalúa una curva de Bézier por partes.
        t_global: parámetro global en [0, 1] para toda la curva
        segments: lista de segmentos de puntos de control
        """
        n_segments = len(segments)
        segment_length = 1.0 / n_segments
        
        # Determinar en qué segmento estamos
        segment_index = int(t_global / segment_length)
        if segment_index >= n_segments:
            segment_index = n_segments - 1
        
        # Calcular t local para este segmento
        t_local = (t_global - segment_index * segment_length) / segment_length
        t_local = max(0.0, min(1.0, t_local))
        
        # Evaluar en el segmento correspondiente
        return evaluate_bezier(segments[segment_index], t_local)

    @window.event
    def on_draw():
        GL.glClearColor(0.05, 0.05, 0.15, 1.0)
        GL.glLineWidth(3.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_DEPTH_TEST)

        window.clear()
        graph.render()

        # Mostrar información en pantalla
        mode_text = "VISTA FIJA" if current_camera_mode == "fixed" else "VISTA TRAYECTORIA"
        info_label = pyglet.text.Label(
            f'Velocidad: {animation_speed:.2f} | {mode_text} | '
            f'{"PAUSADO" if is_paused else "REPRODUCIENDO"} | '
            f'Curvas: {"SÍ" if show_curves else "NO"} | '
            f'Polígonos: {"SÍ" if show_control_polygon else "NO"}',
            font_name='Arial', font_size=14,
            x=10, y=height-25, color=(255, 255, 255, 255)
        )
        info_label.draw()

        controls_label = pyglet.text.Label(
            'Controles: ESPACIO=pausa, +/- =velocidad, R=reiniciar, V=cambiar cámara, C=curvas, P=polígonos',
            font_name='Arial', font_size=10,
            x=10, y=height-45, color=(200, 200, 200, 255)
        )
        controls_label.draw()

        # Mostrar leyenda de colores
        legend_label = pyglet.text.Label(
            'Rojo=control cámara, Azul=control mira, Verde=pos cámara, Amarillo=pos mira, Rosa=curva cámara, Celeste=curva mira',
            font_name='Arial', font_size=12,
            x=10, y=height-65, color=(180, 180, 180, 255)
        )
        legend_label.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        nonlocal is_paused, animation_speed, total_time, show_curves, current_camera_mode, show_control_polygon
        
        if symbol == key.SPACE:
            is_paused = not is_paused
            print(f"Pausa: {is_paused}")
        elif symbol == key.PLUS or symbol == key.EQUAL:
            animation_speed = min(2.0, animation_speed + 0.1)
            print(f"Velocidad aumentada: {animation_speed:.2f}")
        elif symbol == key.MINUS:
            animation_speed = max(0.1, animation_speed - 0.1)
            print(f"Velocidad disminuida: {animation_speed:.2f}")
        elif symbol == key.R:
            total_time = 0.0
            print("Reiniciado")
        elif symbol == key.V:
            # Cambiar entre vista fija y vista de trayectoria
            if current_camera_mode == "fixed":
                current_camera_mode = "path"
                graph.current_view = "path"
            else:
                current_camera_mode = "fixed"
                graph.current_view = "fixed"
            print(f"Modo de cámara: {current_camera_mode}")
        elif symbol == key.C:
            show_curves = not show_curves
            # Mostrar/ocultar las curvas
            for i in range(1, 4):
                graph.nodes[f"camera_curve_instance_{i}"]["pipeline"] = 'axis_pipeline' if show_curves else None
            for i in range(1, 3):
                graph.nodes[f"lookat_curve_instance_{i}"]["pipeline"] = 'axis_pipeline' if show_curves else None
            print(f"Mostrar curvas: {show_curves}")
        elif symbol == key.P:
            show_control_polygon = not show_control_polygon
            # Mostrar/ocultar polígonos de control
            for i in range(1, 4):
                graph.nodes[f"camera_polygon_instance_{i}"]["pipeline"] = 'axis_pipeline' if show_control_polygon else None
            for i in range(1, 3):
                graph.nodes[f"lookat_polygon_instance_{i}"]["pipeline"] = 'axis_pipeline' if show_control_polygon else None
            print(f"Mostrar polígonos de control: {show_control_polygon}")

    def update_camera_path(dt, window):
        nonlocal total_time
        
        if not is_paused:
            total_time += dt
        
        # Calcular parámetro t (con loop)
        t = (total_time * animation_speed) % 1.0
        
        # Evaluar posiciones actuales en las curvas compuestas
        camera_segments = [camera_control_points, camera_control_points_2, camera_control_points_3]
        lookat_segments = [lookat_control_points, lookat_control_points_2]
        
        camera_pos = evaluate_piecewise_bezier(t, camera_segments)
        lookat_pos = evaluate_piecewise_bezier(t, lookat_segments)
        
        # Crear vista de trayectoria
        path_view = tr.lookAt(camera_pos, lookat_pos, np.array([0, 1, 0]))
        
        # Actualizar la vista "path" en el grafo
        graph.register_view_transform(path_view, 'path', set_as_current=False)
        
        # Asegurar que la vista actual sea la correcta
        if current_camera_mode == "path":
            graph.current_view = "path"
        else:
            graph.current_view = "fixed"
        
        # Actualizar indicadores de posición actual
        graph.nodes["current_cam_pos"]["transform"] = tr.translate(*camera_pos) @ tr.uniformScale(0.12)
        graph.nodes["current_lookat_pos"]["transform"] = tr.translate(*lookat_pos) @ tr.uniformScale(0.08)
        
        # Animar el sistema solar
        graph.nodes["earth"]["transform"] = tr.rotationY(2 * total_time) @ tr.translate(2.5, 0.0, 0.0)
        graph.nodes["moon"]["transform"] = tr.rotationY(3 * total_time) @ tr.translate(0.5, 0.0, 0.0)
    
    pyglet.clock.schedule_interval(update_camera_path, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)