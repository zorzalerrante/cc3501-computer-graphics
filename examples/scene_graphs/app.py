import os.path
import sys
from pathlib import Path

import networkx as nx
import numpy as np
import pyglet
import pyglet.gl as GL
import trimesh as tm

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
)

import grafica.transformations as tr


# esta función crea nuestro grafo de escena.
# esencialmente hace lo siguiente:
# sol -> tierra -> luna
# pero cada elemento tiene a su vez dos nodos: geometry (su modelo 3d) y axis (su eje de coordenadas)
#
# lo hacemos todo con la biblioteca networkx.
# cosas como el pipeline correspondiente a cada malla y los atributos que reciben los pipelines
# son almacenadas como atributos de cada nodo de la red.
def create_solar_system(mesh, mesh_pipeline, axis, axis_pipeline):
    graph = nx.DiGraph(root="sun")

    graph.add_node("sun", transform=tr.identity())
    graph.add_node(
        "sun_geometry",
        mesh=mesh,
        pipeline=mesh_pipeline,
        transform=tr.uniformScale(0.8),
        color=np.array((1.0, 0.73, 0.03)),
    )
    graph.add_node(
        "sun_axis",
        mesh=axis,
        pipeline=axis_pipeline,
        transform=tr.uniformScale(1.25),
        mode=GL.GL_LINES,
    )
    graph.add_edge("sun", "sun_geometry")
    graph.add_edge("sun", "sun_axis")

    graph.add_node("earth", transform=tr.translate(2.5, 0.0, 0.0))
    graph.add_node(
        "earth_geometry",
        transform=tr.uniformScale(0.3),
        mesh=mesh,
        pipeline=mesh_pipeline,
        color=np.array((0.0, 0.59, 0.78)),
    )
    graph.add_node(
        "earth_axis",
        mesh=axis,
        pipeline=axis_pipeline,
        transform=tr.uniformScale(0.25),
        mode=GL.GL_LINES,
    )
    graph.add_edge("sun", "earth")
    graph.add_edge("earth", "earth_geometry")
    graph.add_edge("earth", "earth_axis")

    graph.add_node("moon", transform=tr.translate(0.5, 0.0, 0.0))
    graph.add_node(
        "moon_geometry",
        transform=tr.uniformScale(0.1),
        mesh=mesh,
        pipeline=mesh_pipeline,
        color=np.array((0.3, 0.3, 0.3)),
    )
    graph.add_node(
        "moon_axis",
        mesh=axis,
        pipeline=axis_pipeline,
        transform=tr.uniformScale(0.25),
        mode=GL.GL_LINES,
    )
    graph.add_edge("earth", "moon")
    graph.add_edge("moon", "moon_geometry")
    graph.add_edge("moon", "moon_axis")

    return graph

# esta función actualiza el grafo de escena en función del tiempo
# en este caso, hace algo similar a lo que hemos hecho en ejemplos anteriores
# al asignar rotaciones que dependen del tiempo transcurrido en el programa
def update_solar_system(dt, window):
    window.program_state["total_time"] += dt
    total_time = window.program_state["total_time"]

    graph = window.program_state["scene_graph"]

    # para acceder a un nodo del grafo utilizamos su atributo .nodes
    # cada nodo es almacenado como un diccionario
    # por tanto, accedemos a él y a sus atributos con llaves de diccionario
    # que conocemos porque nosotres construimos el grafo
    graph.nodes["earth"]["transform"] = tr.rotationY(2 * total_time) @ tr.translate(
        2.5, 0.0, 0.0
    )
    graph.nodes["moon"]["transform"] = tr.rotationY(3 * total_time) @ tr.translate(
        0.5, 0.0, 0.0
    )


if __name__ == "__main__":
    width = 960
    height = 960

    window = pyglet.window.Window(width, height)

    # cargamos una esfera y la convertimos en una bola de diámetro 1
    mesh = tm.load("assets/sphere.off")
    model_scale = tr.uniformScale(2.0 / mesh.scale)
    model_translate = tr.translate(*-mesh.centroid)
    mesh.apply_transform(model_scale @ model_translate)

    with open(Path(os.path.dirname(__file__)) / "mesh_vertex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(
        Path(os.path.dirname(__file__)) / ".." / "hello_world" / "fragment_program.glsl"
    ) as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    solar_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    mesh_vertex_list = tm.rendering.mesh_to_vertexlist(mesh)
    mesh_gpu = solar_pipeline.vertex_list_indexed(
        len(mesh_vertex_list[4][1]) // 3, GL.GL_TRIANGLES, mesh_vertex_list[3]
    )
    mesh_gpu.position[:] = mesh_vertex_list[4][1]

    # creamos los ejes. los graficaremos con GL_LINES
    axis_positions = np.array([0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1])
    axis_colors = np.array([1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1])
    axis_indices = np.array([0, 1, 2, 3, 4, 5])

    with open(Path(os.path.dirname(__file__)) / "line_vertex_program.glsl") as f:
        vertex_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    axis_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
    axis_gpu = axis_pipeline.vertex_list_indexed(6, GL.GL_LINES, axis_indices)
    axis_gpu.position[:] = axis_positions
    axis_gpu.color[:] = axis_colors

    # creamos el grafo de escena con la función definida más arriba
    graph = create_solar_system(mesh_gpu, solar_pipeline, axis_gpu, axis_pipeline)

    # el estado del programa almacena el grafo de escena en vez de los modelos 3D
    window.program_state = {
        "scene_graph": graph,
        "total_time": 0.0,
        "view": tr.lookAt(
            np.array([5, 5, 5]), np.array([0, 0, 0]), np.array([0, 1, 0])
        ),
        "projection": tr.perspective(45, float(width) / float(height), 0.1, 100),
    }

    @window.event
    def on_draw():
        GL.glClearColor(0.1, 0.1, 0.1, 1.0)
        GL.glLineWidth(2.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_DEPTH_TEST)

        window.clear()

        # configuramos la vista y proyección de los pipelines
        # estas no cambian durante el programa. de hecho pudimos hacerlo antes
        solar_pipeline.use()

        solar_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        solar_pipeline["projection"] = window.program_state["projection"].reshape(
            16, 1, order="F"
        )

        axis_pipeline.use()

        axis_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        axis_pipeline["projection"] = window.program_state["projection"].reshape(
            16, 1, order="F"
        )

        # ahora procederemos a dibujar nuestro grafo de escena.
        graph = window.program_state["scene_graph"]

        # hay que recorrerlo desde un nodo raíz, que almacenamos como atributo del grafo
        root_key = graph.graph["root"]
        # tenemos que hacer un recorrido basado en profundidad (DFS).
        # networkx provee una función que nos entrega dicho recorrido!
        edges = list(nx.edge_dfs(graph, source=root_key))

        # a medida que nos movemos por las aristas vamos a necesitar la transformación de cada nodo
        # partimos con la transformación del nodo raíz
        transformations = {root_key: graph.nodes[root_key]["transform"]}

        for src, dst in edges:
            current_node = graph.nodes[dst]

            if not dst in transformations:
                dst_transform = current_node["transform"]
                transformations[dst] = transformations[src] @ dst_transform

            if "mesh" in current_node:
                current_pipeline = current_node["pipeline"]
                current_pipeline.use()

                current_pipeline["transform"] = transformations[dst].reshape(
                    16, 1, order="F"
                )

                for attr in current_node.keys():
                    if attr in ("mesh", "pipeline", "transform", "mode"):
                        continue

                    current_attr = current_node[attr]
                    current_size = current_node[attr].shape[0]

                    if len(current_node[attr].shape) > 1:
                        current_size = current_size * current_node[attr].shape[1]
                        
                    current_pipeline[attr] = current_node[attr].reshape(
                        current_size, 1, order="F"
                    )

                draw_mode = current_node.get("mode", GL.GL_TRIANGLES)
                current_node["mesh"].draw(draw_mode)

    pyglet.clock.schedule_interval(update_solar_system, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
