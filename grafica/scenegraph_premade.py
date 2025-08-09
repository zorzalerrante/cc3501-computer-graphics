import grafica.transformations as tr
import numpy as np
import pyglet.gl as GL
from itertools import chain

def unit_axes_node(id=None, parent=None):
    # creamos los ejes. los graficaremos con GL_LINES
    positions = np.array([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1])
    colors = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1])
    indices = np.array([0, 1, 2, 3, 4, 5])

    return {
        'mesh': {
            'n_vertices': 6
        },
        'attributes':{
            'position': positions,
            'color': colors
        },
        'indices': indices,
        'GL_TYPE': GL.GL_LINES,
        'transform': tr.identity(),
        'id': id,
        'children': [],
        'parent': parent,
        'object': None,
    }

def rectangle_2d(id=None, parent=None, texture=None):
    vertices = np.array([-1, -1, 1, -1, 1,  1, -1,  1], dtype=np.float32)
    uv = np.array([0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0], dtype=np.float32)
    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    node = {
        'mesh': {
            'n_vertices': 4
        },
        'attributes':{
            'position': vertices,
        },
        'indices': indices,
        'GL_TYPE': GL.GL_TRIANGLES,
        'transform': tr.identity(),
        'id': id,
        'children': [],
        'parent': parent,
        'object': None,
    }

    if texture is not None:
        node['attributes']['uv'] = uv
        node['mesh']['texture'] = texture.id
        node['has_texture'] = True
    else:
        node['has_texture'] = False

    return node

def grid_2d(resolution, id=None, parent=None):
    # construimos nuestra grilla.
    xv, yv = np.meshgrid(
        np.linspace(0, 1, resolution),
        np.linspace(0, 1, resolution),
        indexing="xy",
    )

    vertices = np.vstack(
        (
            xv.reshape(1, -1),
            yv.reshape(1, -1),
            np.zeros(shape=(1, resolution**2)),
        )
    ).T

    indices = [
        [
            (resolution * row + i, resolution * row + i + 1)
            for i in range(resolution - 1)
        ]
        for row in range(resolution)
    ]

    indices.extend(
        [
            [
                (
                    resolution * column + i,
                    resolution * column + i + resolution,
                )
                for i in range(resolution)
            ]
            for column in range(resolution - 1)
        ]
    )

    indices = list(chain(*chain(*indices)))

    # return {
    #     "position": vertices.reshape(-1, 1, order="C"),
    #     "indices": indices,
    #     "n_vertices": resolution**2,
    #     "gl_type": GL.GL_LINES,
    # }

    return {
        'mesh': {
            'n_vertices': resolution**2
        },
        'attributes':{
            'position': vertices.reshape(-1, 1, order="C"),
        },
        'indices': indices,
        'GL_TYPE': GL.GL_LINES,
        'transform': tr.identity(),
        'id': id,
        'children': [],
        'parent': parent,
        'object': None,
    }

def bounding_box_node(min_bounds, max_bounds, id=None, parent=None):
    """
    Crea un nodo con las líneas de un bounding box.
    
    Parámetros:
    min_bounds -- Array numpy con las coordenadas mínimas [x, y, z]
    max_bounds -- Array numpy con las coordenadas máximas [x, y, z]
    """
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
    
    # 12 aristas del cubo (cada arista se define por 2 índices)
    edges = [
        0, 1, 1, 2, 2, 3, 3, 0,  # cara inferior
        4, 5, 5, 6, 6, 7, 7, 4,  # cara superior
        0, 4, 1, 5, 2, 6, 3, 7   # aristas verticales
    ]
    
    # Aplanar las posiciones
    positions = corners.flatten()
    
    # Color verde para todas las líneas
    colors = np.tile([0, 1, 0], 24)  # 24 vértices × 3 componentes RGB
    
    return {
        'mesh': {
            'n_vertices': 24,
            'texture': None,
            'textures': {}
        },
        'attributes': {
            'position': positions,
            'color': colors,
            'uv': None,
            'normal': None
        },
        'indices': edges,
        'GL_TYPE': GL.GL_LINES,
        'transform': tr.identity(),
        'id': id,
        'children': [],
        'parent': parent,
        'object': None,
        'has_texture': False
    }

def line_node(start_point, end_point, color=[1, 1, 0], id=None, parent=None):
    """
    Crea un nodo con una línea entre dos puntos.
    
    Parámetros:
    start_point -- Punto inicial [x, y, z]
    end_point -- Punto final [x, y, z]
    color -- Color RGB de la línea [r, g, b]
    """
    positions = np.array([start_point, end_point]).flatten()
    colors = np.tile(color, 2)
    
    return {
        'mesh': {
            'n_vertices': 2,
            'texture': None,
            'textures': {}
        },
        'attributes': {
            'position': positions,
            'color': colors,
            'uv': None,
            'normal': None
        },
        'indices': [0, 1],
        'GL_TYPE': GL.GL_LINES,
        'transform': tr.identity(),
        'id': id,
        'children': [],
        'parent': parent,
        'object': None,
        'has_texture': False
    }

def point_node(position, color=[1, 0, 0], id=None, parent=None):
    """
    Crea un nodo con un punto.
    
    Parámetros:
    position -- Posición del punto [x, y, z]
    color -- Color RGB del punto [r, g, b]
    """
    return {
        'mesh': {
            'n_vertices': 1,
            'texture': None,
            'textures': {}
        },
        'attributes': {
            'position': np.array(position, dtype=np.float32),
            'color': np.array(color, dtype=np.float32),
            'uv': None,
            'normal': None
        },
        'indices': [0],
        'GL_TYPE': GL.GL_POINTS,
        'transform': tr.identity(),
        'id': id,
        'children': [],
        'parent': parent,
        'object': None,
        'has_texture': False
    }

def triangle_lines_node(v0, v1, v2, color=[1, 0, 1], id=None, parent=None):
    """
    Crea un nodo con las líneas de un triángulo.
    
    Parámetros:
    v0, v1, v2 -- Vértices del triángulo
    color -- Color RGB de las líneas [r, g, b]
    """
    positions = np.array([
        v0, v1,  # línea v0 -> v1
        v1, v2,  # línea v1 -> v2
        v2, v0   # línea v2 -> v0
    ]).flatten()
    
    colors = np.tile(color, 6)  # 6 vértices
    
    return {
        'mesh': {
            'n_vertices': 6,
            'texture': None,
            'textures': {}
        },
        'attributes': {
            'position': positions,
            'color': colors,
            'uv': None,
            'normal': None
        },
        'indices': [0, 1, 2, 3, 4, 5],
        'GL_TYPE': GL.GL_LINES,
        'transform': tr.identity(),
        'id': id,
        'children': [],
        'parent': parent,
        'object': None,
        'has_texture': False
    }