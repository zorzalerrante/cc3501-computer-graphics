import networkx as nx
from .scenegraph_nodes import _node_from_file
import grafica.transformations as tr
import pyglet.gl as GL
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
        
        self.add_instance(name, self.meshes[mesh_name], pipeline, **instance_attributes)

    def add_instance(self, name, mesh, pipeline, **instance_attributes):
        if instance_attributes is None:
            instance_attributes = {}

        self.add_node(name, **self._instance_node(mesh, pipeline, instance_attributes))

        for i, child in enumerate(mesh['children']):
            child_name = f'{name}_child_{i}'
            self.add_node(child_name, **self._instance_node(child, pipeline, instance_attributes))
            self.add_edge(name, child_name)

    def render(self, **pipeline_attrs):
        for pipeline in self.pipelines.values():
            for attr, value in self.global_attributes.items():
                if hasattr(pipeline, attr):
                    if type(value) == float:
                        pipeline[attr] = value
                    else:
                        size = value.shape[0]

                        if len(value.shape) > 1:
                            size = size * value.shape[1]
                            
                        pipeline[attr] = value.reshape(
                            size, 1, order="F"
                        )
        # tenemos que hacer un recorrido basado en profundidad (DFS).
        # networkx provee una función que nos entrega dicho recorrido!
        # hay que recorrerlo desde un nodo raíz, que almacenamos como atributo del grafo
        edges = list(nx.edge_dfs(self, source=self.root_key))
        
        # a medida que nos movemos por las aristas vamos a necesitar la transformación de cada nodo
        # partimos con la transformación del nodo raíz
        transformations = {self.root_key: self.nodes[self.root_key]["transform"]}

        for src, dst in edges:
            current_node = self.nodes[dst]
            
            if not dst in transformations:
                dst_transform = current_node["transform"]

                if 'instance_attributes' in current_node and 'transform' in current_node['instance_attributes']:
                    dst_transform = dst_transform @ current_node['instance_attributes']['transform']

                transformations[dst] = transformations[src] @ dst_transform

            if "mesh" in current_node:
                if current_node['pipeline'] is None:
                    continue
                current_pipeline = self.pipelines[current_node["pipeline"]]
                current_pipeline.use()

                current_pipeline["transform"] = transformations[dst].reshape(
                    16, 1, order="F"
                )

                if 'instance_attributes' in current_node:
                    instance_attrs = current_node['instance_attributes']

                    for attr in instance_attrs.keys():
                        if attr == 'transform':
                            continue

                        current_attr = instance_attrs[attr]
                        current_size = instance_attrs[attr].shape[0]

                        if len(instance_attrs[attr].shape) > 1:
                            current_size = current_size * instance_attrs[attr].shape[1]
                            
                        current_pipeline[attr] = instance_attrs[attr].reshape(
                            current_size, 1, order="F"
                        )

                if 'texture' in current_node['mesh'] and current_node['mesh']['texture'] is not None:
                    GL.glBindTexture(GL.GL_TEXTURE_2D, current_node['mesh']['texture'])
                else:
                    # esto "activa" una textura nula
                    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

                current_node["mesh_gpu"].draw(current_node.get("GL_TYPE"))

    def __add_pipeline_single_node(self, node, pipeline_name):   
        print(pipeline_name)
        if 'mesh' not in node or node['mesh'] is None:
            node['pipeline'] = None
            return
        
        pipeline = self.pipelines[pipeline_name]

        mesh_gpu = pipeline.vertex_list_indexed(
            node['mesh']['n_vertices'], node['GL_TYPE'], node['indices']
        )

        node['pipeline'] = pipeline_name
        node['mesh_gpu'] = mesh_gpu

        for attr in node['attributes']:
            if node['attributes'][attr] is not None and hasattr(mesh_gpu, attr):
                getattr(mesh_gpu, attr)[:] = node['attributes'][attr]


    def _add_node_pipeline(self, node, pipeline):
        self.__add_pipeline_single_node(node, pipeline)
        for child in node['children']:
            self.__add_pipeline_single_node(child, pipeline)


    def _instance_node(self, node, pipeline, instance_attrs=None):
        instance = copy(node)
        self._add_node_pipeline(instance, pipeline)
        instance['instance_attributes'] = instance_attrs

        return instance
    
    def apply_instance_attributes(self, node_key, **attrs):
        """
        Aplica o actualiza atributos de instancia a un nodo existente
        
        Parámetros:
        node_key -- La clave/ID del nodo al que aplicar los atributos
        **attrs -- Diccionario de atributos a aplicar/actualizar
        """
            
        node = self.nodes[node_key]
        if 'instance_attributes' not in node:
            node['instance_attributes'] = {}
            
        # Actualizar los atributos existentes o añadir nuevos
        for key, value in attrs.items():
            node['instance_attributes'][key] = value

    def set_global_attributes(self, **attrs):
        self.global_attributes.update(attrs)
        