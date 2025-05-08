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

    if texture:
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

