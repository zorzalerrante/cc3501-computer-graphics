import numpy as np
import trimesh as tm
import grafica.transformations as tr
from itertools import chain
# importamos esta función de trimesh porque nos permitirá asignarle una propiedad a cada vértice
# y pintaremos el conejo en función de esa propiedad
# en este caso, es la curvatura de la superficie
from trimesh.curvature import discrete_gaussian_curvature_measure
import pyglet.gl as GL

def rectangulo():
    vertices = np.array(
        [
            -1,
            -1,
            0.0,  # inf izq
            1,
            -1,
            0.0,  # if der
            1,
            1,
            0.0,  # sup der
            -1,
            1,
            0.0,  # sup izq
        ],
        dtype=np.float32,
    )

    vertex_colors = np.array(
        [
            1.0,
            204 / 255.0,
            1.0,  # inf izq
            1.0,
            204 / 255.0,
            1.0,  # if der
            204 / 255.0,
            1.0,
            1.0,  # sup der
            204 / 255.0,
            1.0,
            1.0,  # sup izq
        ],
        dtype=np.float32,
    )

    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    return {
        "position": vertices,
        "color": vertex_colors,
        "indices": indices,
        "n_vertices": 4,
        'gl_type': GL.GL_TRIANGLES
    }


def stanford_bunny():
    bunny = tm.load("assets/Stanford_Bunny.stl")

    # model transform del conejo. la aplicamos directamente en trimesh
    # noten que esta vez solamente escalamos al conejo, ¡no lo estamos rotando!
    bunny_scale = tr.uniformScale(1.0 / bunny.scale)
    bunny_translate = tr.translate(*-bunny.centroid)
    bunny.apply_transform(bunny_scale @ bunny_translate)
    # el conejo ya está transformado. pero lo movimos al origen,
    # cuando en realidad queremos que esté sobre el suelo
    # con esto dejamos la parte baja del conejo en z = 0
    # asumiento que z apunta hacia arriba en nuestro mundo
    bunny.apply_transform(tr.translate(0, 0, -bunny.vertices[:, 2].min()))

    # aquí calculamos la curvatura. pueden ver la documentación de trimesh para saber qué es.
    bunny_curvature = discrete_gaussian_curvature_measure(bunny, bunny.vertices, 0.01)
    # la curvatura está definida entre -1 y 1, así que la convertimos al rango 0 a 1.
    # usaremos este valor para pintar cada vértice en el vertex shader
    bunny_curvature = (bunny_curvature + 1) / 2

    bunny_vertex_list = tm.rendering.mesh_to_vertexlist(bunny)

    return {
        "mesh": bunny,
        "position": bunny_vertex_list[4][1],
        "n_vertices": len(bunny_vertex_list[4][1]) // 3,
        "indices": bunny_vertex_list[3],
        "curvature": np.take(bunny_curvature, bunny.faces).reshape(-1, 1, order="C"),
        'gl_type': GL.GL_TRIANGLES
    }

def regular_grid(resolution=10):
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

    return {
        'position': vertices.reshape(-1, 1, order="C"),
        'indices': indices,
        'n_vertices': resolution**2,
        'gl_type': GL.GL_LINES
    }