import networkx as nx
from .scenegraph_nodes import _node_from_file
import grafica.transformations as tr
import pyglet.gl as GL
import pyglet
from copy import copy


class Scenegraph(nx.DiGraph):
    def __init__(self, root_key, transform=None):
        super().__init__()
        self.root_key = root_key

        if transform is None:
            transform = tr.identity()

        self.add_transform(root_key, transform)

        self.meshes = {}
        self.pipelines = {}
        self.global_attributes = {}
        self.global_transforms = {}

    def register_pipeline(self, name, pipeline):
        self.pipelines[name] = pipeline

    def add_transform(self, name, transform):
        print(name, transform)
        self.add_node(name, transform=transform)

    def load_and_register_mesh(self, name, filename, rezero=True, normalize=True):
        self.meshes[name] = _node_from_file(filename, name)

    def register_mesh(self, name, mesh):
        self.meshes[name] = mesh

    def add_mesh_instance(self, name, mesh_name, pipeline, **instance_attributes):

        self._add_instance(
            name, self.meshes[mesh_name], pipeline, **instance_attributes
        )

    def _add_instance(self, name, mesh, pipeline, **instance_attributes):
        if instance_attributes is None:
            instance_attributes = {}

        self.add_node(name, **self._instance_node(mesh, pipeline, instance_attributes))

        for i, child in enumerate(mesh["children"]):
            child_name = f"{name}_child_{i}"
            self.add_node(
                child_name, **self._instance_node(child, pipeline, instance_attributes)
            )
            self.add_edge(name, child_name)

    def render(self, recalculate_transforms=True, **pipeline_attrs):
        """
        Renderiza el grafo de escena.
        
        Parámetros:
        recalculate_transforms -- Si es True, recalcula las transformaciones globales
        **pipeline_attrs -- Atributos adicionales para las pipelines
        """
        # por cada pipeline, configuramos sus atributos uniform
        for pipeline_name, pipeline in self.pipelines.items():
            pipeline.use()

            for attr, value in self.global_attributes.items():
                # print(f"setting {attr} with {value}, type: {type(value)}")
                if not (type(value) == float or type(value) == int):
                    size = value.shape[0]

                    if len(value.shape) > 1:
                        size = size * value.shape[1]

                    value = value.reshape(size, 1, order="F")

                # esto no es lo más adecuado
                # (pero no logré hacerlo de otra forma)
                try:
                    pipeline[attr] = value
                except pyglet.graphics.shader.ShaderException:
                    continue

            pipeline.stop()

        # Calcular transformaciones globales si es necesario
        if recalculate_transforms or not self.global_transforms:
            self.calculate_global_transforms()

        for node_key, current_node in self.nodes.items():
            if "mesh" in current_node:
                if current_node["pipeline"] is None:
                    continue
                current_pipeline = self.pipelines[current_node["pipeline"]]
                current_pipeline.use()

                 # Usar la transformación global ya calculada
                current_pipeline["transform"] = self.global_transforms[node_key].reshape(16, 1, order="F")

                # Aplicar atributos de instancia
                if "instance_attributes" in current_node:
                    instance_attrs = current_node["instance_attributes"]

                    for attr in instance_attrs.keys():
                        if attr == "transform":
                            continue

                        current_attr = instance_attrs[attr]

                        if type(current_attr) == float or type(current_attr) == int:
                            current_pipeline[attr] = current_attr
                        else:
                            current_size = instance_attrs[attr].shape[0]

                            if len(instance_attrs[attr].shape) > 1:
                                current_size = (
                                    current_size * instance_attrs[attr].shape[1]
                                )

                            current_pipeline[attr] = instance_attrs[attr].reshape(
                                current_size, 1, order="F"
                            )

                # Configurar textura
                if (
                    "texture" in current_node["mesh"]
                    and current_node["mesh"]["texture"] is not None
                ):
                    GL.glBindTexture(GL.GL_TEXTURE_2D, current_node["mesh"]["texture"])
                else:
                    # esto "activa" una textura nula
                    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

                # Dibujar!
                current_node["mesh_gpu"].draw(current_node.get("GL_TYPE"))

    def __add_pipeline_single_node(self, node, pipeline_name):
        if "mesh" not in node or node["mesh"] is None:
            node["pipeline"] = None
            return

        pipeline = self.pipelines[pipeline_name]

        mesh_gpu = pipeline.vertex_list_indexed(
            node["mesh"]["n_vertices"], node["GL_TYPE"], node["indices"]
        )

        node["pipeline"] = pipeline_name
        node["mesh_gpu"] = mesh_gpu

        for attr in node["attributes"]:
            if node["attributes"][attr] is not None and hasattr(mesh_gpu, attr):
                getattr(mesh_gpu, attr)[:] = node["attributes"][attr]

    def _add_node_pipeline(self, node, pipeline):
        self.__add_pipeline_single_node(node, pipeline)
        for child in node["children"]:
            self.__add_pipeline_single_node(child, pipeline)

    def _instance_node(self, node, pipeline, instance_attrs=None):
        instance = copy(node)
        self._add_node_pipeline(instance, pipeline)
        instance["instance_attributes"] = instance_attrs

        return instance

    def apply_instance_attributes(self, node_key, **attrs):
        """
        Aplica o actualiza atributos de instancia a un nodo existente

        Parámetros:
        node_key -- La clave/ID del nodo al que aplicar los atributos
        **attrs -- Diccionario de atributos a aplicar/actualizar
        """

        node = self.nodes[node_key]
        if "instance_attributes" not in node:
            node["instance_attributes"] = {}

        # Actualizar los atributos existentes o añadir nuevos
        for key, value in attrs.items():
            node["instance_attributes"][key] = value

    def set_global_attributes(self, **attrs):
        self.global_attributes.update(attrs)

    def calculate_global_transforms(self):
        """
        Calcula las transformaciones globales para todos los nodos del grafo
        y las almacena en self.global_transforms.
        """
        self.global_transforms = {self.root_key: self.nodes[self.root_key]["transform"]}
        
        # tenemos que hacer un recorrido basado en profundidad (DFS).
        # networkx provee una función que nos entrega dicho recorrido!
        # hay que recorrerlo desde un nodo raíz, que almacenamos como atributo del grafo
        edges = list(nx.edge_dfs(self, source=self.root_key))
        
        for src, dst in edges:
            if dst not in self.global_transforms:
                dst_transform = self.nodes[dst].get("transform", tr.identity())
                
                # Considerar transformaciones de instancia si existen
                if (
                    "instance_attributes" in self.nodes[dst]
                    and "transform" in self.nodes[dst]["instance_attributes"]
                ):
                    dst_transform = dst_transform @ self.nodes[dst]["instance_attributes"]["transform"]
                
                self.global_transforms[dst] = self.global_transforms[src] @ dst_transform
        
        return self.global_transforms
    
    def get_global_transform(self, node_key):
        """
        Obtiene la transformación global para un nodo específico.
        Si las transformaciones globales no están calculadas, las calcula primero.
        """
        if not self.global_transforms or node_key not in self.global_transforms:
            self.calculate_global_transforms()
        
        return self.global_transforms.get(node_key, tr.identity())
    
    def get_global_position(self, node_key):
        """
        Obtiene la posición global de un nodo.
        """
        transform = self.get_global_transform(node_key)
        return transform[0:3, 3]
