import grafica.transformations as tr
import numpy as np
import pyglet.gl as GL

def unit_axes_node(id=None, parent=None):
    # creamos los ejes. los graficaremos con GL_LINES
    positions = np.array([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1])
    colors = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1])
    indices = np.array([0, 1, 2, 3, 4, 5])

    return {
        'mesh': {
            'object': None,
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
    }
