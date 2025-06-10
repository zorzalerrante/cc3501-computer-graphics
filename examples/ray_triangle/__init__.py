import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import sys
from pathlib import Path
import os

import grafica.transformations as tr
from grafica.intersections import intersect_mesh, ray_triangle_intersection
from grafica.utils import load_pipeline

# ============================================
# INICIALIZACIÓN
# ============================================

import click

current_path = Path(os.path.dirname(__file__))

@click.command("ray_triangle", short_help="Demostración de intersección rayo-triángulo")
@click.argument("filename", type=str)
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=720)
def ray_triangle_example(filename, width, height):
    window = pyglet.window.Window(width, height)

    # Cargar y preparar la malla 3D
    mesh = tm.load(filename)
    if hasattr(mesh, 'geometry'):
        mesh = list(mesh.geometry.values())[0]

    mesh.fix_normals()

    # Centrar en origen y escalar a tamaño unitario
    mesh.apply_translation(-mesh.centroid) # Trasladar centro a origen
    mesh.apply_scale(2.3 / mesh.scale) # Escalar para que quepa en [-1,1]

    print(f"Mesh loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    print(f"Mesh bounds: min={mesh.vertices.min(axis=0)}, max={mesh.vertices.max(axis=0)}")
    print(f"Mesh centered at origin, scaled to [-1, 1]")
    print(f"Camera at: [0, 0, 3], looking at: [0, 0, 0]")

    # Calcular normales por vértice para iluminación suave
    vertex_normals = mesh.vertex_normals

    # Estado: matriz de rotación acumulada del modelo
    rotation = np.eye(4)

    # ============================================
    # SHADERS
    # ============================================

    # Shader para renderizar el modelo con iluminación
    model_shader = load_pipeline(current_path / 'mesh_vp.glsl', current_path / 'mesh_fp.glsl')
    # Shader para debug (rayo y punto de impacto)
    debug_shader = load_pipeline(current_path / 'debug_vp.glsl', current_path / 'debug_fp.glsl')

    # Preparar datos de vértices para OpenGL
    vertices = mesh.vertices.flatten()
    normals = vertex_normals.flatten()
    indices = mesh.faces.flatten()

    model_vertex_list = model_shader.vertex_list_indexed(
        len(mesh.vertices),
        GL.GL_TRIANGLES,
        indices,
        position=('f', vertices),
        normal=('f', normals)
    )

    # Configurar cámara
    aspect = width / height
    projection = tr.perspective(45.0, aspect, 0.1, 100.0)
    view = tr.lookAt(np.array([0, 0, 3]), np.array([0, 0, 0]), np.array([0, 1, 0]))

    # Variables para visualización de debug en ESPACIO LOCAL
    debug_lines_local = None
    debug_points_local = None
    hit_triangle_local = None
    verify_mode = False
    show_bbox = False
    bbox_lines = None
    test_both_sides = False

    # ============================================
    # BOUNDING BOX
    # ============================================

    def create_bbox_lines():
        """Crea líneas para visualizar el bounding box del modelo"""
        nonlocal bbox_lines
        
        # Obtener límites del modelo
        min_bounds = mesh.vertices.min(axis=0)
        max_bounds = mesh.vertices.max(axis=0)
        
        # 8 vértices del bounding box
        corners = np.array([
            [min_bounds[0], min_bounds[1], min_bounds[2]],
            [max_bounds[0], min_bounds[1], min_bounds[2]],
            [max_bounds[0], max_bounds[1], min_bounds[2]],
            [min_bounds[0], max_bounds[1], min_bounds[2]],
            [min_bounds[0], min_bounds[1], max_bounds[2]],
            [max_bounds[0], min_bounds[1], max_bounds[2]],
            [max_bounds[0], max_bounds[1], max_bounds[2]],
            [min_bounds[0], max_bounds[1], max_bounds[2]]
        ])
        
        # 12 aristas del cubo
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),  # cara inferior
            (4, 5), (5, 6), (6, 7), (7, 4),  # cara superior
            (0, 4), (1, 5), (2, 6), (3, 7)   # aristas verticales
        ]
        
        # Crear vértices y colores para las líneas
        line_vertices = []
        line_colors = []
        
        for edge in edges:
            line_vertices.extend(corners[edge[0]])
            line_vertices.extend(corners[edge[1]])
            # Color verde para el bbox
            line_colors.extend([0, 1, 0])
            line_colors.extend([0, 1, 0])
        
        if bbox_lines:
            bbox_lines.delete()
        
        bbox_lines = debug_shader.vertex_list(
            24,  # 12 aristas × 2 vértices
            GL.GL_LINES,
            position=('f', np.array(line_vertices, dtype=np.float32)),
            color=('f', np.array(line_colors, dtype=np.float32))
        )

    # ============================================
    # RAY CASTING
    # ============================================

    def screen_to_ray_simple(x, y):
        """
        Convierte coordenadas de pantalla a un rayo 3D.
        Retorna el rayo directamente en el espacio local del modelo.
        """
        # Paso 1: Píxeles a NDC
        ndc_x = (2.0 * x / width) - 1.0
        ndc_y = (2.0 * y / height) - 1.0
        
        # Paso 2: Puntos en clip space
        near_clip = np.array([ndc_x, ndc_y, -1.0, 1.0])
        far_clip = np.array([ndc_x, ndc_y, 1.0, 1.0])
        
        # Paso 3: Unproject usando MVP completa
        # Esto nos da el rayo directamente en espacio local del modelo
        mvp = projection @ view @ rotation
        mvp_inv = np.linalg.inv(mvp)
        
        # Transformar y des-homogeneizar
        near_local = mvp_inv @ near_clip
        far_local = mvp_inv @ far_clip
        near_local /= near_local[3]
        far_local /= far_local[3]
        
        # Paso 4: Definir el rayo en espacio local
        origin = near_local[:3]
        direction = far_local[:3] - near_local[:3]
        direction /= np.linalg.norm(direction)
        
        return origin, direction

    create_bbox_lines()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        """
        Maneja clicks del mouse para ray casting.
        """
        nonlocal debug_lines_local, debug_points_local, hit_triangle_local
        
        if button == pyglet.window.mouse.LEFT:
            # Obtener rayo directamente en espacio local
            local_origin, local_direction = screen_to_ray_simple(x, y)
            
            print(f"\n=== Click at ({x}, {y}) ===")
            print(f"Local ray origin: {local_origin}")
            print(f"Local ray direction: {local_direction}")
            
            # Intersección con la malla (ya estamos en espacio local)
            hit, hit_point_local, face_idx, distance = intersect_mesh(
                local_origin, local_direction, mesh.vertices, mesh.faces
            )
            
            # Crear visualización del rayo EN ESPACIO LOCAL
            ray_length = 5.0
            ray_end_local = local_origin + local_direction * ray_length
            line_vertices = np.array([local_origin, ray_end_local], dtype=np.float32).flatten()
            line_colors = np.array([[1, 1, 0], [1, 1, 0]], dtype=np.float32).flatten()
            
            if debug_lines_local:
                debug_lines_local.delete()
            
            debug_lines_local = debug_shader.vertex_list(
                2,
                GL.GL_LINES,
                position=('f', line_vertices),
                color=('f', line_colors)
            )
            
            if hit:
                print(f"Hit found! Face {face_idx}")
                print(f"Local point: {hit_point_local}")
                print(f"Distance: {distance:.6f}")
                
                # Crear visualización del triángulo impactado EN ESPACIO LOCAL
                face = mesh.faces[face_idx]
                v0 = mesh.vertices[face[0]]
                v1 = mesh.vertices[face[1]]
                v2 = mesh.vertices[face[2]]
                
                if hit_triangle_local:
                    hit_triangle_local.delete()
                
                triangle_vertices = []
                triangle_colors = []
                
                # Los vértices ya están en espacio local
                triangle_vertices.extend(v0)
                triangle_vertices.extend(v1)
                triangle_colors.extend([1, 0, 1])  # Magenta
                triangle_colors.extend([1, 0, 1])
                
                triangle_vertices.extend(v1)
                triangle_vertices.extend(v2)
                triangle_colors.extend([1, 0, 1])
                triangle_colors.extend([1, 0, 1])
                
                triangle_vertices.extend(v2)
                triangle_vertices.extend(v0)
                triangle_colors.extend([1, 0, 1])
                triangle_colors.extend([1, 0, 1])
                
                hit_triangle_local = debug_shader.vertex_list(
                    6,
                    GL.GL_LINES,
                    position=('f', np.array(triangle_vertices, dtype=np.float32)),
                    color=('f', np.array(triangle_colors, dtype=np.float32))
                )
                
                # Visualizar punto de impacto EN ESPACIO LOCAL
                if debug_points_local:
                    debug_points_local.delete()
                
                debug_points_local = debug_shader.vertex_list(
                    1,
                    GL.GL_POINTS,
                    position=('f', hit_point_local.astype(np.float32)),
                    color=('f', np.array([1, 0, 0], dtype=np.float32))
                )
                
                # Comparar con trimesh si está en modo verificación
                if verify_mode:
                    print("\n--- Trimesh comparison ---")
                    tm_locations, tm_ray_indices, tm_face_indices = mesh.ray.intersects_location(
                        ray_origins=[local_origin],
                        ray_directions=[local_direction]
                    )
                    if len(tm_locations) > 0:
                        print(f"Trimesh found {len(tm_locations)} hits")
                        for i, (loc, face) in enumerate(zip(tm_locations, tm_face_indices)):
                            dist = np.linalg.norm(loc - local_origin)
                            print(f"  Hit {i}: Face {face}, distance {dist:.6f}")
                            if face == face_idx:
                                print(f"  ✓ Same face as our implementation")
                    else:
                        print("WARNING: Trimesh found no hit!")
            else:
                print("No hit")
                
                if debug_points_local:
                    debug_points_local.delete()
                    debug_points_local = None
                if hit_triangle_local:
                    hit_triangle_local.delete()
                    hit_triangle_local = None
                
                # Comparar con trimesh si está en modo verificación
                if verify_mode:
                    print("\n--- Trimesh comparison ---")
                    tm_locations, tm_ray_indices, tm_face_indices = mesh.ray.intersects_location(
                        ray_origins=[local_origin],
                        ray_directions=[local_direction]
                    )
                    if len(tm_locations) > 0:
                        print(f"WARNING: Trimesh FOUND {len(tm_locations)} hits!")
                        for i, (loc, face) in enumerate(zip(tm_locations, tm_face_indices)):
                            dist = np.linalg.norm(loc - local_origin)
                            print(f"  Hit {i}: Face {face}, distance {dist:.6f}")
                    else:
                        print("Trimesh also found no hit")

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        """Rotación interactiva del modelo"""
        nonlocal rotation
        if buttons & pyglet.window.mouse.RIGHT:
            new_rot_y = tr.rotationY(dx * 0.01)
            new_rot_x = tr.rotationX(-dy * 0.01)
            
            # Aplicar rotaciones
            rotation = new_rot_y @ rotation
            rotation = new_rot_x @ rotation
            
            # Re-ortogonalizar la matriz de rotación para evitar drift
            rot3x3 = rotation[:3, :3]
            u, s, vt = np.linalg.svd(rot3x3)
            rot3x3 = u @ vt
            rotation[:3, :3] = rot3x3

    @window.event
    def on_key_press(symbol, modifiers):
        """Controles de teclado"""
        nonlocal debug_lines_local, debug_points_local, verify_mode, show_bbox, hit_triangle_local, rotation
        if symbol == pyglet.window.key.C:
            if debug_lines_local:
                debug_lines_local.delete()
                debug_lines_local = None
            if debug_points_local:
                debug_points_local.delete()
                debug_points_local = None
            if hit_triangle_local:
                hit_triangle_local.delete()
                hit_triangle_local = None
        elif symbol == pyglet.window.key.B:
            show_bbox = not show_bbox
        elif symbol == pyglet.window.key.R:
            # Reset rotación
            rotation = np.eye(4)
            print("\nRotation reset to identity")
        elif symbol == pyglet.window.key.V:
            # Toggle modo verificación con Trimesh
            verify_mode = not verify_mode
            print(f"\nVerification mode: {'ON' if verify_mode else 'OFF'}")
        elif symbol == pyglet.window.key.D:
            # Debug: mostrar información detallada de la rotación
            print("\n=== ROTATION DEBUG ===")
            print("Rotation matrix:")
            print(rotation)
            print(f"\nDeterminant: {np.linalg.det(rotation[:3,:3]):.6f}")
            
            # Verificar ortogonalidad
            rot3 = rotation[:3,:3]
            should_be_identity = rot3 @ rot3.T
            print("\nR @ R.T (should be identity):")
            print(should_be_identity)
            print(f"Max error from identity: {np.max(np.abs(should_be_identity - np.eye(3))):.9f}")
            
            # Extraer ángulos de Euler (aproximados)
            sy = np.sqrt(rot3[0,0]**2 + rot3[1,0]**2)
            x = np.arctan2(rot3[2,1], rot3[2,2])
            y = np.arctan2(-rot3[2,0], sy)
            z = np.arctan2(rot3[1,0], rot3[0,0])
            print(f"\nApprox Euler angles (deg): x={np.degrees(x):.1f}, y={np.degrees(y):.1f}, z={np.degrees(z):.1f}")

    @window.event
    def on_draw():
        """
        Renderizado de la escena con iluminación.
        """
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glPointSize(10)
        window.clear()
        
        # Matriz Model-View-Projection completa
        mvp = projection @ view @ rotation
        
        # Dibujar malla con iluminación
        model_shader.use()
        model_shader['mvp'] = mvp.astype(np.float32).flatten('F')
        model_shader['model'] = rotation.astype(np.float32).flatten('F')
        model_shader['color'] = (0.7, 0.7, 0.8)
        model_shader['lightPos'] = np.array([5.0, 5.0, 5.0], dtype=np.float32)
        model_shader['viewPos'] = np.array([0.0, 0.0, 3.0], dtype=np.float32)
        model_vertex_list.draw(GL.GL_TRIANGLES)
        
        # Dibujar elementos de debug - TODOS usando la misma MVP que el modelo
        if debug_lines_local or debug_points_local or hit_triangle_local or (show_bbox and bbox_lines):
            debug_shader.use()
            # Usar la MISMA matriz MVP que el modelo
            debug_shader['mvp'] = mvp.astype(np.float32).flatten('F')
            
            # Todos estos elementos están en espacio local y serán transformados por la GPU
            if debug_lines_local:
                debug_lines_local.draw(GL.GL_LINES)
            if debug_points_local:
                debug_points_local.draw(GL.GL_POINTS)
            if hit_triangle_local:
                hit_triangle_local.draw(GL.GL_LINES)
            if show_bbox and bbox_lines:
                bbox_lines.draw(GL.GL_LINES)

    # ============================================
    # INFORMACIÓN
    # ============================================

    print("\n=============================")
    print("CONTROLES:")
    print("Click izquierdo: Lanzar rayo")
    print("Arrastrar derecho: Rotar modelo")
    print("C: Limpiar visualización")
    print("B: Toggle bounding box")
    print("R: Reset rotación")
    print("V: Toggle modo verificación (comparar con Trimesh)")
    print("D: Debug - mostrar info de rotación")
    print("=============================\n")

    pyglet.app.run()
