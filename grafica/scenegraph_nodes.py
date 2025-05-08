import networkx as nx
import trimesh as tm
import grafica.transformations as tr
import pyglet.gl as GL
import numpy as np
from grafica.textures import texture_2D_setup


def _node_from_mesh(mesh, id=None, parent=None, transform=None, fix_normals=True, smooth=True, smooth_threshold=100000):
    if transform is None:
        transform = tr.identity()

    if fix_normals:
        mesh.fix_normals()

    vertex_list = tm.rendering.mesh_to_vertexlist(mesh, smooth=smooth, smooth_threshold=smooth_threshold)

    node = {
        'object': mesh,
        'mesh': {
            'n_vertices': len(vertex_list[4][1]) // 3,
            'texture': None
        },
        'attributes':{
            'position': vertex_list[4][1],
            'uv': None,
            'normal': vertex_list[5][1],
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

    has_texture = hasattr(mesh.visual, "material")
    if has_texture:
        node['attributes']['uv'] = vertex_list[6][1]
        node['mesh']['texture'] = texture_2D_setup(mesh.visual.material.image)
        node['has_texture'] = True
    else:
        node['attributes']['color'] = vertex_list[6][1]

    return node



def _node_from_file(filename, id=None, parent=None, rezero=True, normalize=True, fix_normals=True, smooth=True, smooth_threshold=100000):
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
        node = _node_from_mesh(object_geometry, fix_normals=fix_normals, smooth=smooth, smooth_threshold=smooth_threshold)
        base['children'].append(node)
        base['has_texture'] = node['has_texture']

    return base
    
