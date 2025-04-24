import networkx as nx
from .scenegraph_nodes import node_from_file, add_node_pipeline, instance_node
import grafica.transformations as tr

class Scenegraph(nx.DiGraph):
    def __init__(self, root_key, transform=None):
        super().__init__()
        self.root_key = root_key

        if transform is None:
            transform = tr.identity()

        self.add_transform(root_key, transform)

    def add_transform(self, name, transform):
        print(name, transform)
        self.add_node(name, transform=transform)

    def add_instance(self, name, mesh, pipeline, **instance_attributes):
        if instance_attributes is None:
            instance_attributes = {}

        self.add_node(name, **instance_node(mesh, pipeline, instance_attributes))

    def render(self):
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
                current_pipeline = current_node["pipeline"]
                current_pipeline.use()

                current_pipeline["transform"] = transformations[dst].reshape(
                    16, 1, order="F"
                )

                if 'instance_attributes' in current_node:
                    instance_attrs = current_node['instance_attributes']
                    for attr in instance_attrs.keys():
                        if attr == 'transform':
                            continue
                        #print('instance attr', attr, instance_attrs[attr])
                        current_attr = instance_attrs[attr]
                        current_size = instance_attrs[attr].shape[0]

                        if len(instance_attrs[attr].shape) > 1:
                            current_size = current_size * instance_attrs[attr].shape[1]
                            
                        current_pipeline[attr] = instance_attrs[attr].reshape(
                            current_size, 1, order="F"
                        )

                current_node["mesh_gpu"].draw(current_node.get("GL_TYPE"))