import networkx as nx
import trimesh as tm
import grafica.transformations as tr
import pyglet.gl as GL
import numpy as np
from grafica.textures import texture_2D_setup
from copy import copy

def node_from_mesh(mesh, id=None, parent=None, transform=None):
    if transform is None:
        transform = tr.identity()
    
    vertex_list = tm.rendering.mesh_to_vertexlist(mesh)

    node = {
        'mesh': {
            'object': mesh,
            'n_vertices': len(vertex_list[4][1]) // 3,
            'texture': None
        },
        'attributes':{
            'position': vertex_list[4][1],
            'uv': None,
            'normal': None,
            'color': None
        },
        'indices': vertex_list[3],
        'GL_TYPE': GL.GL_TRIANGLES,
        'transform': transform,
        'id': None,
        'children': [],
        'parent': parent,
    }

    has_texture = hasattr(mesh.visual, "material")
    if has_texture:
        node['attributes']['uv'] = vertex_list[6][1]
        node['mesh']['texture'] = texture_2D_setup(mesh.visual.material.image)
    else:
        node['attributes']['color'] = vertex_list[6][1]

    return node



def node_from_file(filename, id=None, parent=None, rezero=True, normalize=True):
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
    }

    for object_id, object_geometry in scene.geometry.items():
        node = node_from_mesh(object_geometry)
        base['children'].append(node)

    return base
    
def __add_pipeline_single_node(node, pipeline):   
    if 'mesh' not in node:
        node['pipeline'] = None
        return
    
    print(node['mesh'])
    
    mesh_gpu = pipeline.vertex_list_indexed(
        node['mesh']['n_vertices'], node['GL_TYPE'], node['indices']
    )

    node['pipeline'] = pipeline
    node['mesh_gpu'] = mesh_gpu

    for attr in node['attributes']:
        if node['attributes'][attr] is not None and hasattr(mesh_gpu, attr):
            getattr(mesh_gpu, attr)[:] = node['attributes'][attr]


def add_node_pipeline(node, pipeline):
    __add_pipeline_single_node(node, pipeline)
    for child in node['children']:
        __add_pipeline_single_node(child, pipeline)


def instance_node(node, pipeline, instance_attrs=None):
    instance = copy(node)
    instance['instance_attributes'] = instance_attrs

    return instance