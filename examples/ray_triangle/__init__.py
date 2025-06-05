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

import click


@click.command("ray_triangle", short_help="Demostración de intersección rayo-triángulo")
@click.argument("filename", type=str)
@click.option("--width", type=int, default=960)
@click.option("--height", type=int, default=720)
def ray_triangle_example(filename, width, height):
    """
    1. RENDERIZADO:
    - Vértices del modelo (espacio local) 
    - → Multiplicados por Model (rotation)
    - → Multiplicados por View
    - → Multiplicados por Projection
    - → Pantalla

    2. RAY CASTING:
    - Click en pantalla
    - → NDC
    - → Unproject con (Projection × View)⁻¹ 
    - → Rayo en espacio mundial
    - → Transformar con (rotation)⁻¹
    - → Rayo en espacio local del modelo
    - → Intersección con geometría original
    - → Transformar resultado con rotation
    - → Punto en espacio mundial

    La clave es que el modelo se renderiza transformado por 'rotation',
    pero la geometría para intersección está en espacio local.
    """

    current_path = Path(os.path.dirname(__file__))
    window = pyglet.window.Window(width, height)

    # Cargar y preparar la malla 3D
    mesh = tm.load(filename)
    if hasattr(mesh, "geometry"):
        mesh = list(mesh.geometry.values())[0]

    mesh.fix_normals()

    # Centrar en origen y escalar a tamaño unitario
    mesh.apply_translation(-mesh.centroid)  # Trasladar centro a origen
    mesh.apply_scale(2.3 / mesh.scale)  # Escalar para que quepa en [-1,1]

    print(f"Mesh loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    print(
        f"Mesh bounds: min={mesh.vertices.min(axis=0)}, max={mesh.vertices.max(axis=0)}"
    )
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
    model_shader = load_pipeline(
        current_path / "mesh_vp.glsl", current_path / "mesh_fp.glsl"
    )
    # Shader para debug (rayo y punto de impacto)
    debug_shader = load_pipeline(
        current_path / "debug_vp.glsl", current_path / "debug_fp.glsl"
    )

    # Preparar datos de vértices para OpenGL
    # por ahora estamos trabajando a bajo nivel
    vertices = mesh.vertices.flatten()
    normals = vertex_normals.flatten()
    indices = mesh.faces.flatten()

    model_vertex_list = model_shader.vertex_list_indexed(
        len(mesh.vertices),
        GL.GL_TRIANGLES,
        indices,
        position=("f", vertices),
        normal=("f", normals),
    )

    # Configurar cámara
    aspect = width / height
    projection = tr.perspective(45.0, aspect, 0.1, 100.0)
    view = tr.lookAt(np.array([0, 0, 3]), np.array([0, 0, 0]), np.array([0, 1, 0]))

    # Variables para visualización de debug
    debug_lines = None
    debug_points = None
    verify_mode = False
    show_bbox = False
    bbox_lines = None
    test_both_sides = False
    hit_triangle = None

    # ============================================
    # RAY-TRIANGLE INTERSECTION MANUAL
    # ============================================

    def create_bbox_lines():
        """Crea líneas para visualizar el bounding box del modelo"""
        nonlocal bbox_lines

        # Obtener límites del modelo
        min_bounds = mesh.vertices.min(axis=0)
        max_bounds = mesh.vertices.max(axis=0)

        # 8 vértices del bounding box
        corners = np.array(
            [
                [min_bounds[0], min_bounds[1], min_bounds[2]],
                [max_bounds[0], min_bounds[1], min_bounds[2]],
                [max_bounds[0], max_bounds[1], min_bounds[2]],
                [min_bounds[0], max_bounds[1], min_bounds[2]],
                [min_bounds[0], min_bounds[1], max_bounds[2]],
                [max_bounds[0], min_bounds[1], max_bounds[2]],
                [max_bounds[0], max_bounds[1], max_bounds[2]],
                [min_bounds[0], max_bounds[1], max_bounds[2]],
            ]
        )

        # 12 aristas del cubo
        edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 0),  # cara inferior
            (4, 5),
            (5, 6),
            (6, 7),
            (7, 4),  # cara superior
            (0, 4),
            (1, 5),
            (2, 6),
            (3, 7),  # aristas verticales
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
            position=("f", np.array(line_vertices, dtype=np.float32)),
            color=("f", np.array(line_colors, dtype=np.float32)),
        )

    # ============================================
    # RAY CASTING
    # ============================================

    def screen_to_ray(x, y):
        """
        Convierte coordenadas de pantalla (píxeles) a un rayo 3D.
        """
        # Paso 1: Píxeles a NDC
        ndc_x = (2.0 * x / width) - 1.0
        ndc_y = (2.0 * y / height) - 1.0

        # Paso 2: Puntos en clip space
        near_clip = np.array([ndc_x, ndc_y, -1.0, 1.0])
        far_clip = np.array([ndc_x, ndc_y, 1.0, 1.0])

        # Paso 3: Unproject (clip space → world space)
        mvp = projection @ view @ rotation
        mvp_inv = np.linalg.inv(mvp)

        # Transformar y des-homogeneizar
        near_world = mvp_inv @ near_clip
        far_world = mvp_inv @ far_clip
        near_world /= near_world[3]
        far_world /= far_world[3]

        # Paso 4: Definir el rayo
        origin = near_world[:3]
        direction = far_world[:3] - near_world[:3]
        direction /= np.linalg.norm(direction)

        return origin, direction

    create_bbox_lines()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        """
        Maneja clicks del mouse para ray casting.
        """
        nonlocal debug_lines, debug_points, verify_mode, hit_triangle

        if button == pyglet.window.mouse.LEFT:
            # Obtener rayo en espacio mundial
            origin, direction = screen_to_ray(x, y)

            print(f"\n=== Click at ({x}, {y}) ===")
            print(f"World ray origin: {origin}")
            print(f"World ray direction: {direction}")

            # IMPORTANTE: El rayo está en espacio mundial (sin rotación del modelo)
            # El modelo está rotado por 'rotation', así que transformamos el rayo
            # al espacio local del modelo para hacer la intersección

            # Verificar que la matriz de rotación sea ortogonal
            rot_check = rotation[:3, :3]
            ortho_error = np.linalg.norm(rot_check @ rot_check.T - np.eye(3))
            if ortho_error > 1e-6:
                print(f"WARNING: Rotation matrix not orthogonal, error: {ortho_error}")

            # Transformar el rayo al espacio local del modelo
            inv_rotation = np.linalg.inv(rotation)

            # Transformar origen
            local_origin = (inv_rotation @ np.append(origin, 1.0))[:3]

            # Transformar dirección (sin traslación)
            local_direction = inv_rotation[:3, :3] @ direction
            local_direction = local_direction / np.linalg.norm(local_direction)

            print(f"Local ray origin: {local_origin}")
            print(f"Local ray direction: {local_direction}")

            # Intersección manual con la malla
            hit, hit_point_local, face_idx, distance = intersect_mesh(
                local_origin, local_direction, mesh.vertices, mesh.faces
            )

            # Visualizar el rayo EN ESPACIO MUNDIAL
            ray_length = 5.0
            ray_end = origin + direction * ray_length
            line_vertices = np.array([origin, ray_end], dtype=np.float32).flatten()
            line_colors = np.array([[1, 1, 0], [1, 1, 0]], dtype=np.float32).flatten()

            if debug_lines:
                debug_lines.delete()

            debug_lines = debug_shader.vertex_list(
                2, GL.GL_LINES, position=("f", line_vertices), color=("f", line_colors)
            )

            if hit:
                # Transformar punto al espacio mundial
                hit_point_world = (rotation @ np.append(hit_point_local, 1.0))[:3]

                # Verificar que el punto esté en el rayo
                t_verify = np.dot(hit_point_world - origin, direction)
                point_on_ray = origin + direction * t_verify
                error = np.linalg.norm(hit_point_world - point_on_ray)

                print(f"Hit found! Face {face_idx}")
                print(f"Local point: {hit_point_local}")
                print(f"World point: {hit_point_world}")
                print(f"Distance: {distance:.6f}")
                print(f"Verification error: {error:.6f}")

                # Crear visualización del triángulo impactado
                face = mesh.faces[face_idx]
                v0 = mesh.vertices[face[0]]
                v1 = mesh.vertices[face[1]]
                v2 = mesh.vertices[face[2]]

                # Transformar vértices al espacio mundial
                v0_world = (rotation @ np.append(v0, 1.0))[:3]
                v1_world = (rotation @ np.append(v1, 1.0))[:3]
                v2_world = (rotation @ np.append(v2, 1.0))[:3]

                # Crear líneas para el triángulo
                if hit_triangle:
                    hit_triangle.delete()

                triangle_vertices = []
                triangle_colors = []

                # Línea v0 -> v1
                triangle_vertices.extend(v0_world)
                triangle_vertices.extend(v1_world)
                triangle_colors.extend([1, 0, 1])  # Magenta
                triangle_colors.extend([1, 0, 1])

                # Línea v1 -> v2
                triangle_vertices.extend(v1_world)
                triangle_vertices.extend(v2_world)
                triangle_colors.extend([1, 0, 1])
                triangle_colors.extend([1, 0, 1])

                # Línea v2 -> v0
                triangle_vertices.extend(v2_world)
                triangle_vertices.extend(v0_world)
                triangle_colors.extend([1, 0, 1])
                triangle_colors.extend([1, 0, 1])

                hit_triangle = debug_shader.vertex_list(
                    6,
                    GL.GL_LINES,
                    position=("f", np.array(triangle_vertices, dtype=np.float32)),
                    color=("f", np.array(triangle_colors, dtype=np.float32)),
                )

                # Usar el punto proyectado sobre el rayo para visualización
                if error > 1e-4:
                    print(f"Using projected point due to error")
                    hit_point_world = point_on_ray

                # Visualizar punto de impacto
                if debug_points:
                    debug_points.delete()

                debug_points = debug_shader.vertex_list(
                    1,
                    GL.GL_POINTS,
                    position=("f", hit_point_world.astype(np.float32)),
                    color=("f", np.array([1, 0, 0], dtype=np.float32)),
                )
            else:
                print("No hit")

                # Limpiar visualizaciones anteriores
                if debug_points:
                    debug_points.delete()
                    debug_points = None
                if hit_triangle:
                    hit_triangle.delete()
                    hit_triangle = None

                # Comparar con trimesh si está en modo verificación
                if verify_mode:
                    print("\n--- Trimesh comparison ---")
                    tm_locations, tm_ray_indices, tm_face_indices = (
                        mesh.ray.intersects_location(
                            ray_origins=[local_origin], ray_directions=[local_direction]
                        )
                    )
                    if len(tm_locations) > 0:
                        print(f"WARNING: Trimesh FOUND {len(tm_locations)} hits!")
                        for i, (loc, face) in enumerate(
                            zip(tm_locations, tm_face_indices)
                        ):
                            dist = np.linalg.norm(loc - local_origin)
                            print(f"  Hit {i}: Face {face}, distance {dist:.6f}")
                    else:
                        print("Trimesh also found no hit")

            # Debug adicional: verificar el primer triángulo del modelo
            if (face_idx == 0 and hit) or (not hit and verify_mode):
                print("\n--- Debug: First triangle ---")
                face = mesh.faces[0]
                v0, v1, v2 = (
                    mesh.vertices[face[0]],
                    mesh.vertices[face[1]],
                    mesh.vertices[face[2]],
                )
                print(f"Triangle 0 vertices (local):")
                print(f"  v0: {v0}")
                print(f"  v1: {v1}")
                print(f"  v2: {v2}")

                # Transformar vértices al espacio mundial
                v0_world = (rotation @ np.append(v0, 1.0))[:3]
                v1_world = (rotation @ np.append(v1, 1.0))[:3]
                v2_world = (rotation @ np.append(v2, 1.0))[:3]
                print(f"Triangle 0 vertices (world):")
                print(f"  v0: {v0_world}")
                print(f"  v1: {v1_world}")
                print(f"  v2: {v2_world}")

                # Calcular normal del triángulo
                edge1 = v1 - v0
                edge2 = v2 - v0
                normal = np.cross(edge1, edge2)
                normal = normal / np.linalg.norm(normal)
                print(f"Triangle normal (local): {normal}")

                # Verificar si el rayo está cerca de este triángulo
                hit_test, t_test, u_test, v_test = ray_triangle_intersection(
                    local_origin, local_direction, v0, v1, v2
                )
                if hit_test:
                    print(f"Ray DOES intersect triangle 0 at t={t_test:.6f}")
                else:
                    print(f"Ray does NOT intersect triangle 0")

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        """Rotación interactiva del modelo"""
        nonlocal rotation
        if buttons & pyglet.window.mouse.RIGHT:
            # Volver al orden original pero con debugging
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
        nonlocal debug_lines, debug_points, verify_mode, show_bbox, hit_triangle, rotation
        if symbol == pyglet.window.key.C:
            if debug_lines:
                debug_lines.delete()
                debug_lines = None
            if debug_points:
                debug_points.delete()
                debug_points = None
            if hit_triangle:
                hit_triangle.delete()
                hit_triangle = None
        elif symbol == pyglet.window.key.B:
            show_bbox = not show_bbox
        elif symbol == pyglet.window.key.R:
            # Reset rotación
            rotation = np.eye(4)
            print("\nRotation reset to identity")
        elif symbol == pyglet.window.key.D:
            # Debug: mostrar información detallada de la rotación
            print("\n=== ROTATION DEBUG ===")
            print("Rotation matrix:")
            print(rotation)
            print(f"\nDeterminant: {np.linalg.det(rotation[:3,:3]):.6f}")

            # Verificar ortogonalidad
            rot3 = rotation[:3, :3]
            should_be_identity = rot3 @ rot3.T
            print("\nR @ R.T (should be identity):")
            print(should_be_identity)
            print(
                f"Max error from identity: {np.max(np.abs(should_be_identity - np.eye(3))):.9f}"
            )

            # Extraer ángulos de Euler (aproximados)
            sy = np.sqrt(rot3[0, 0] ** 2 + rot3[1, 0] ** 2)
            x = np.arctan2(rot3[2, 1], rot3[2, 2])
            y = np.arctan2(-rot3[2, 0], sy)
            z = np.arctan2(rot3[1, 0], rot3[0, 0])
            print(
                f"\nApprox Euler angles (deg): x={np.degrees(x):.1f}, y={np.degrees(y):.1f}, z={np.degrees(z):.1f}"
            )

    @window.event
    def on_draw():
        """
        Renderizado de la escena con iluminación.

        IMPORTANTE: La matriz MVP incluye la rotación del modelo.
        El ray casting debe tener esto en cuenta.
        """
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glPointSize(10)
        window.clear()

        # Matriz Model-View-Projection completa
        # MVP = Projection × View × Model(rotation)
        mvp = projection @ view @ rotation

        # Dibujar malla con iluminación
        model_shader.use()
        model_shader["mvp"] = mvp.astype(np.float32).flatten("F")
        model_shader["model"] = rotation.astype(np.float32).flatten("F")
        model_shader["color"] = (0.7, 0.7, 0.8)
        model_shader["lightPos"] = np.array([5.0, 5.0, 5.0], dtype=np.float32)
        model_shader["viewPos"] = np.array([0.0, 0.0, 3.0], dtype=np.float32)
        model_vertex_list.draw(GL.GL_TRIANGLES)

        # Dibujar debug si existe
        if debug_lines or debug_points or (show_bbox and bbox_lines) or hit_triangle:
            debug_shader.use()
            debug_shader["mvp"] = mvp.astype(np.float32).flatten("F")

            if debug_lines:
                debug_lines.draw(GL.GL_LINES)
            if debug_points:
                debug_points.draw(GL.GL_POINTS)
            if show_bbox and bbox_lines:
                bbox_lines.draw(GL.GL_LINES)
            if hit_triangle:
                hit_triangle.draw(GL.GL_LINES)

    print("Click izquierdo: Lanzar rayo")
    print("Arrastrar derecho: Rotar modelo")
    print("C: Limpiar visualización")
    print("B: Toggle bounding box")
    print("R: Reset rotación")
    print("D: Debug - mostrar info de rotación")
    print("=============================")

    pyglet.app.run()
