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
        self.global_attributes = {"projection": tr.identity()}
        self.global_transforms = {}
        self.views = {None: tr.identity()}
        self.current_view = None
        self.view_parameter_name = 'view'
        self.transform_parameter_name = 'transform'

    def load_and_register_pipeline(
        self, name, vertex_program_path, fragment_program_path
    ):
        with open(vertex_program_path) as f:
            vertex_source_code = f.read()

        # y el shader de píxeles solo lee el color correspondiente al píxel
        with open(fragment_program_path) as f:
            fragment_source_code = f.read()

        vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
        frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
        pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
        self.register_pipeline(name, pipeline)

    def register_pipeline(self, name, pipeline):
        self.pipelines[name] = pipeline

    def register_view_transform(self, view_transform, name='default', set_as_current=True):
        self.views[name] = view_transform
        if set_as_current:
            self.current_view = name

    def add_transform(self, name, transform):
        self.add_node(name, transform=transform)

    def load_and_register_mesh(self, name, filename, **kwargs):
        self.meshes[name] = _node_from_file(filename, name, **kwargs)

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
            
            # configura la cámara (mat4)
            # si no se ha indicado una, utiliza la identidad
            try:
                pipeline[self.view_parameter_name] = self.views[self.current_view].reshape(16, 1, order="F")
            # esto sucederá si el shader no tiene el parámetro de vista
            except pyglet.graphics.shader.ShaderException as e:
                pass


            for attr, value in self.global_attributes.items():
                if not (type(value) == float or type(value) == int):
                    size = value.shape[0]

                    if len(value.shape) > 1:
                        size = size * value.shape[1]

                    value = value.reshape(size, 1, order="F")

                # esto no es lo más adecuado
                # (pero no logré hacerlo de otra forma)
                try:
                    pipeline[attr] = value
                except pyglet.graphics.shader.ShaderException as e:
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
                try:
                    current_pipeline[self.transform_parameter_name] = self.global_transforms[
                        node_key
                    ].reshape(16, 1, order="F")
                except pyglet.graphics.shader.ShaderException as e:
                    pass 

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

                # Configurar texturas: primero la textura por defecto (mantener compatibilidad)
                initial_texture_unit = 0
                if (
                    "texture" in current_node["mesh"]
                    and current_node["mesh"]["texture"] is not None
                ):
                    GL.glActiveTexture(GL.GL_TEXTURE0)
                    GL.glBindTexture(GL.GL_TEXTURE_2D, current_node["mesh"]["texture"])
                    initial_texture_unit = 1
                    # try:
                    #     current_pipeline["diffuse_texture"] = 0
                    # except pyglet.graphics.shader.ShaderException:
                    #     pass
                else:
                    GL.glActiveTexture(GL.GL_TEXTURE0)
                    GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
                
                # Configurar texturas adicionales usando enumerate
                if 'textures' in current_node["mesh"]:
                    for i, (tex_name, tex_id) in enumerate(current_node["mesh"]["textures"].items(), initial_texture_unit):
                        if tex_name == 'diffuse':  # Saltar 'diffuse' que ya se manejó arriba
                            continue
                            
                        GL.glActiveTexture(GL.GL_TEXTURE0 + i)
                        GL.glBindTexture(GL.GL_TEXTURE_2D, tex_id)
                        
                        # Intentar configurar el uniform en el shader
                        try:
                            current_pipeline[tex_name] = i
                        except pyglet.graphics.shader.ShaderException:
                            pass

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
                    dst_transform = (
                        dst_transform
                        @ self.nodes[dst]["instance_attributes"]["transform"]
                    )

                self.global_transforms[dst] = (
                    self.global_transforms[src] @ dst_transform
                )

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

    def add_texture_to_node(self, node_key, texture_name, texture_id):
        """
        Agrega una textura adicional a un nodo y sus hijos, si existen.
        
        Parámetros:
        node_key -- La clave del nodo
        texture_name -- Nombre identificador de la textura (ej: 'shadow_map')
        texture_id -- ID de la textura de OpenGL
        """
        node = self.nodes[node_key]
        
        # Función auxiliar para agregar textura a un solo nodo
        def _add_texture_to_single_node(current_node):
            if 'mesh' not in current_node or current_node['mesh'] is None:
                return False
            
            if 'textures' not in current_node['mesh']:
                current_node['mesh']['textures'] = {}
            
            current_node['mesh']['textures'][texture_name] = texture_id
            return True
        
        # Primero intentamos agregar al nodo principal
        added_to_main = _add_texture_to_single_node(node)
        
        # Ahora buscamos los hijos del nodo en el grafo
        children = list(self.successors(node_key))
        for child_key in children:
            _add_texture_to_single_node(self.nodes[child_key])
        
        # Si el nodo tiene información sobre sus "children" (en su estructura interna)
        if 'children' in node and node['children']:
            for child in node['children']:
                _add_texture_to_single_node(child)
        
        # Si no se agregó al nodo principal ni se encontraron hijos, advertir
        if not added_to_main and not children and (not 'children' in node or not node['children']):
            print(f"Advertencia: No se pudo agregar textura '{texture_name}' al nodo '{node_key}', no tiene malla ni hijos.")

    def remove_texture_from_node(self, node_key, texture_name):
        """
        Elimina una textura específica de un nodo y sus hijos.
        """
        node = self.nodes[node_key]
        
        # Función auxiliar para eliminar textura de un solo nodo
        def _remove_texture_from_single_node(current_node):
            if 'mesh' in current_node and current_node['mesh'] and 'textures' in current_node['mesh']:
                if texture_name in current_node['mesh']['textures']:
                    del current_node['mesh']['textures'][texture_name]
        
        # Eliminar del nodo principal
        _remove_texture_from_single_node(node)
        
        # Eliminar de los hijos en el grafo
        for child_key in self.successors(node_key):
            _remove_texture_from_single_node(self.nodes[child_key])
        
        # Eliminar de los "children" internos
        if 'children' in node and node['children']:
            for child in node['children']:
                _remove_texture_from_single_node(child)