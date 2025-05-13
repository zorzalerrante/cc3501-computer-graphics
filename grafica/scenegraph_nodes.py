import networkx as nx
import trimesh as tm
import grafica.transformations as tr
import pyglet.gl as GL
import numpy as np
from grafica.textures import texture_2D_setup


def _node_from_mesh(mesh, id=None, parent=None, transform=None, fix_normals=False, smooth=False, smooth_threshold=100000, force_color=None, invert_normals=False):
    """
    Crea un nodo a partir de una malla.
    
    Parámetros:
    mesh -- Malla a partir de la cual crear el nodo
    id -- Identificador del nodo
    parent -- Nodo padre
    transform -- Transformación a aplicar
    fix_normals -- Si es True, corrige las normales
    smooth -- Si es True, suaviza las normales
    smooth_threshold -- Umbral para suavizado
    force_color -- Color forzado como array numpy [R,G,B,A] (valores 0-255)
                   Si es None, se usa el color original del modelo
    """
    if transform is None:
        transform = tr.identity()

    if fix_normals:
        mesh.fix_normals()

    vertex_list = tm.rendering.mesh_to_vertexlist(mesh, smooth=smooth, smooth_threshold=smooth_threshold)

    # Obtener número de vértices primero
    n_vertices = len(vertex_list[4][1]) // 3

    # Obtener normales del vertex_list
    normal_data = vertex_list[5][1]
    
    # Invertir normales si se solicita
    if invert_normals:
        # Las normales están almacenadas como un arreglo plano de floats
        # Cada 3 valores representan una normal (x, y, z)
        normal_data = -np.array(normal_data)  # Invertir todas las normales
        print("Normales invertidas para el modelo")

    node = {
        'object': mesh,
        'mesh': {
            'n_vertices': n_vertices,
            'texture': None,
            'textures': {}
        },
        'attributes':{
            'position': vertex_list[4][1],
            'uv': None,
            'normal': normal_data,
            'color': None
        },
        'indices': vertex_list[3],
        'GL_TYPE': GL.GL_TRIANGLES,
        'transform': transform,
        'id': None,
        'children': [],
        'parent': parent,
        'has_texture': False,
    }

    # Manejar la textura si existe
    if hasattr(mesh.visual, "material") and getattr(mesh.visual.material, 'image', None) is not None:
        node['attributes']['uv'] = vertex_list[6][1]
        texture_id = texture_2D_setup(mesh.visual.material.image)
        node['mesh']['texture'] = texture_id
        node['mesh']['textures'] = dict(diffuse=texture_id)
        node['has_texture'] = True
    
    # Procesar el color
    if force_color is not None and isinstance(force_color, np.ndarray) and len(force_color) == 4:
        # Usar el color forzado para todos los vértices
        colors = np.ones((n_vertices, 4), dtype=np.uint8)
        colors[:] = force_color
        node['attributes']['color'] = colors.flatten()
        print(f"Aplicando color forzado al modelo: {force_color}")
    else:
        # Procesar el color original como antes
        if len(vertex_list) > 6:
            color_format = vertex_list[6][0]
            color_data = vertex_list[6][1]
            
            if color_format.startswith('c3'):
                # Formato RGB, convertir a RGBA
                if color_format.startswith('c3f'):
                    # RGB float en rango [0,1], convertir a RGBA byte [0,255]
                    rgba_data = np.ones(n_vertices * 4, dtype=np.uint8) * 255
                    for i in range(n_vertices):
                        rgba_data[i*4] = int(color_data[i*3] * 255)
                        rgba_data[i*4+1] = int(color_data[i*3+1] * 255)
                        rgba_data[i*4+2] = int(color_data[i*3+2] * 255)
                        rgba_data[i*4+3] = 255  # Alpha = 255
                else:
                    # RGB byte, ya está en rango [0,255], convertir a RGBA byte
                    rgba_data = np.ones(n_vertices * 4, dtype=np.uint8) * 255
                    for i in range(n_vertices):
                        rgba_data[i*4] = color_data[i*3]
                        rgba_data[i*4+1] = color_data[i*3+1]
                        rgba_data[i*4+2] = color_data[i*3+2]
                        rgba_data[i*4+3] = 255  # Alpha = 255
                
                node['attributes']['color'] = rgba_data
            
            elif color_format.startswith('c4'):
                # Formato RGBA
                if color_format.startswith('c4f'):
                    # RGBA float en rango [0,1], convertir a RGBA byte [0,255]
                    rgba_data = np.ones(n_vertices * 4, dtype=np.uint8) * 255
                    for i in range(n_vertices):
                        rgba_data[i*4] = int(color_data[i*4] * 255)
                        rgba_data[i*4+1] = int(color_data[i*4+1] * 255)
                        rgba_data[i*4+2] = int(color_data[i*4+2] * 255)
                        rgba_data[i*4+3] = int(color_data[i*4+3] * 255)
                else:
                    # RGBA byte, ya está en rango [0,255]
                    rgba_data = color_data
                
                node['attributes']['color'] = rgba_data
            
            else:
                # Formato desconocido, crear un color por defecto (BLANCO)
                print(f"Formato de color no reconocido: {color_format}, usando color blanco por defecto")
                node['attributes']['color'] = np.ones(n_vertices * 4, dtype=np.uint8) * 255
        else:
            # Si no hay información de color, crear un color por defecto (BLANCO)
            node['attributes']['color'] = np.ones(n_vertices * 4, dtype=np.uint8) * 255
            print("No se encontró información de color, usando color blanco por defecto")

    return node



def _node_from_file(filename, id=None, parent=None, rezero=True, normalize=True, fix_normals=True, smooth=False, smooth_threshold=100000, force_color=None, invert_normals=False):
    scene = tm.load(filename, force="scene")
    if rezero:
        scene.rezero()

    if normalize:
        scene = scene.scaled(2.0 / scene.scale)

    base = {
        'mesh': None,
        'GL_TYPE': None,
        'transform': tr.identity(),
        'id': id,
        'children': [],
        'parent': parent,
        'has_texture': False,
        'object': scene
    }

    for object_id, object_geometry in scene.geometry.items():
        node = _node_from_mesh(object_geometry, fix_normals=fix_normals, smooth=smooth, smooth_threshold=smooth_threshold, force_color=force_color, invert_normals=invert_normals)
        base['children'].append(node)
        base['has_texture'] = node['has_texture']

    return base
    
