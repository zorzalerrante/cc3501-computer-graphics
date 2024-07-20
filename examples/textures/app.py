import os.path
import numpy as np
import pyglet
import OpenGL.GL as GL
import sys
import trimesh as tm
from PIL import Image
from pyglet.window import key


if sys.path[0] != "":
    sys.path.insert(0, "")

import grafica.transformations as tr

#funcion auxiliar para cargar shaders
from grafica.utils import load_pipeline

#funcion auxiliar para asignar texturas a archivos .obj
from grafica.textures import texture_2D_setup

from grafica.arcball import Arcball
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
from pathlib import Path


# funcion para leer un mesh
#recibe un mesh y dos shaders una para los elementos con textura (tex_pipeline) y para los que no (notex_pipeline)
#nos devuelve un diccionario con la info del mesh, su archivo gpu, su pipeline y la respectiva textura
#o mas de uno si se desea
def setupMesh(file_path, tex_pipeline, notex_pipeline, scale): 
    # dependiendo de lo que contenga el archivo a cargar,
    # trimesh puede entregar una malla (mesh) o una escena (compuesta de mallas)
    # con esto forzamos que siempre entregue una escena
    asset = tm.load(file_path, force="scene")
    asset.rezero()

    #esto la escala con lo que decidamos printea tambien un cubo que contiene todo el modelo para tener como referencia
    asset = asset.scaled(scale / asset.scale)
    #esto printea tambien un cubo que contiene todo el modelo para tener como referencia 
    #(después puede servir para simulación física)
    print(asset.bounds)

    # aquí guardaremos las mallas del modelo que graficaremos
    vertex_lists = {}

    # con esto iteramos sobre las mallas
    for object_id, object_geometry in asset.geometry.items():
        mesh = {}

        # por si acaso, para que la malla tenga normales consistentes
        object_geometry.fix_normals(True)

        object_vlist = tm.rendering.mesh_to_vertexlist(object_geometry)

        n_triangles = len(object_vlist[4][1]) // 3

        # el pipeline a usar dependerá de si el objeto tiene textura
        # OJO: asumimos que si tiene material, tiene textura
        # print(dir(object_geometry.visual.material))
        #print(object_geometry.visual.material.image)
        if object_geometry.visual.material.image != None:
            print('has texture')
            mesh["pipeline"] = tex_pipeline
            has_texture = True
        else:
            print('no texture')
            mesh["pipeline"] = notex_pipeline
            has_texture = False

        # inicializamos los datos en la GPU
        mesh["gpu_data"] = mesh["pipeline"].vertex_list_indexed(
            n_triangles, GL.GL_TRIANGLES, object_vlist[3])

        # copiamos la posición de los vértices
        mesh["gpu_data"].position[:] = object_vlist[4][1]

        mesh["image"] = object_geometry.visual.material.image

        #para el zorzal no necesitamos esto, pero lo necesitarán si definen normales en el shader
        # las normales vienen en vertex_list[5]
        # las manipulamos del mismo modo que los vértices
        #mesh["gpu_data"].normal[:] = object_vlist[5][1]

        # con (o sin) textura es diferente el procedimiento
        # aunque siempre en vertex_list[6] viene la información de material
        if has_texture:
            # copiamos la textura
            # trimesh ya la cargó, solo debemos copiarla a la GPU
            mesh["texture"] = texture_2D_setup(object_geometry.visual.material.image)
            #copiamos las coordenadas de textura en el parámetro uv
            mesh["gpu_data"].uv[:] = object_vlist[6][1]
        else:
            # usualmente el color viene como c4B/static en vlist[6][0], lo que significa "color de 4 bytes". idealmente eso debe verificarse
            mesh["gpu_data"].color[:] = object_vlist[6][1]
        mesh['id'] = object_id[0:-4]
        vertex_lists[object_id] = mesh
    return vertex_lists


#class controller para interactuar
class Controller:
    def __init__(self):
        self.type = False
    

if __name__ == "__main__":
    width = 1500
    height = 600
    window = pyglet.window.Window(width, height)

    window.program_state = {
        "total_time": 0.0,
        "view": tr.lookAt(
            np.array([0, 1, 1]),  # posición de la cámara
            np.array([0, 0, 0]),  # hacia dónde apunta
            np.array([0, 1, 0]),  # vector para orientarla (arriba)
        ),
        "projection": tr.perspective(60, float(width) / float(height), 0.001, 100),
    }

    # tendremos dos pipelines uno para los mesh con textura y otro para los que no
    #(para el ejemplo solo estaremos dibujando con texturas)
    tex_pipeline = load_pipeline(   
        Path(os.path.dirname(__file__)) / "vertex_program.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program.glsl",
    )

    notex_pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_program_notex.glsl",
        Path(os.path.dirname(__file__)) / "fragment_program_notex.glsl",
    )

    #creamos el dicc vertex_list donde se almacenará la info de setupMesh de los mesh que le entreguemos
    vertex_lists = {}
    vertex_lists = setupMesh('./assets/zorzal.obj', tex_pipeline, notex_pipeline, 1)


    #ahora lo haremos de otra forma para asignar texturas a una malla
    #lo haremos para visualizar las texturas del zorzal
    with open(Path(os.path.dirname(__file__)) / "vertex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "fragment_program.glsl") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")

    #creamos los pipelines de las imagenes de las texturas
    cuerpo_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
    plumas_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    
    #hacemos un cuadrado para poner las imagenes
    shape = bs.createTextureQuad(1, 1)

    #extraemos las texturas de los cuadrados
    img_cuerpo = Image.open("./assets/zorzal_uv.png")
    img_plumas = Image.open("./assets/plumas_uv.png")


    #notamos que la funcion createTextureQuad nos entrega las coordenadas de los vertices y normales juntas
    #pero solo necesitamos los vertices por lo que los extraemos
    vertices = [0, 0, 0,
                0, 0, 0,
                0, 0, 0,
                0, 0, 0]
    for i in range(0,4):
        vertices[3*i] = shape.vertices[5*i]
        vertices[3*i+1] = shape.vertices[5*i+1]
        vertices[3*i+2] = shape.vertices[5*i+2]


    #configuramos el pipeline para la imagen del cuerpo
    cuerpo = cuerpo_pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, shape.indices)
    cuerpo.position[:] = vertices
    cuerpo.uv[:] = np.array([0, 0,    #las imagenes son de lado 1 por lo que acá estamos recorriendo...
                             0, 1,    #sus vértices desde el (0,0) pues queremos toda la imagen
                             1, 1,
                             1, 0])
    

    #configuramos el pipeline para la imagen de las plumas
    plumas = plumas_pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, shape.indices)
    plumas.position[:] = vertices
    plumas.uv[:] = np.array([0, 0, 
                             0, 1,
                             1, 1,
                             1, 0])

    
    #instanciamos nuestra Arcball, esto es netamente para mover a nuestro zorzal y se aprecie mejor
    arcball = Arcball(
        np.identity(4),
        np.array((width, height), dtype=float),
        1.5,
        np.array([0.0, 0.0, 0.0]),
    )

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        arcball.down((x, y))

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        arcball.drag((x, y))

    #apetando el espacio se podrá ver la malla del zorzal
    controller = Controller()

    @window.event
    def on_key_press(symbol, modifier):
        if(pyglet.window.key.SPACE == symbol):
            controller.type = True
       
    @window.event
    def on_key_release(symbol, modifier):
        if(pyglet.window.key.SPACE == symbol):
            controller.type = False


    @window.event
    def on_draw():
        #asignamos un color de fondo claro para que se vean las texturas y el pajarito
        GL.glClearColor(0.88, 0.88, 0.88, 1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)

        window.clear()

        for object_geometry in vertex_lists.values():
            # dibujamos cada una de las mallas con su respectivo pipeline
            pipeline = object_geometry["pipeline"]
            pipeline.use()

            pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
            pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")

            #definimos las transformaciones, en este caso son para todo igual... 
            #porque tenemos un solo objeto almacenado en vertex_list
            pipeline["transform"] = (tr.translate(0.7, 0, 0) @ arcball.pose @ tr.rotationX(-np.pi/4) 
                                     @ tr.uniformScale(1.5)).reshape(16, 1, order="F")
            
            if "texture" in object_geometry:
                GL.glBindTexture(GL.GL_TEXTURE_2D, object_geometry["texture"])
            else:
                # esto activa una textura nula
                GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

            if controller.type:
                object_geometry["gpu_data"].draw(pyglet.gl.GL_LINES)
            else:
                object_geometry["gpu_data"].draw(pyglet.gl.GL_TRIANGLES)

        
        #ahora dibujamos las imagenes que seteamos antes del on_draw()
        cuerpo_pipeline.use()
        cuerpo_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        cuerpo_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")
        cuerpo_pipeline["transform"] = (tr.translate(-0.45, 0, 0) @ tr.rotationX(-np.pi/4)).reshape(16, 1, order="F")
        
        #llamamos a la textura
        tex_cuerpo = texture_2D_setup(img_cuerpo)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tex_cuerpo) 
        cuerpo.draw(pyglet.gl.GL_TRIANGLES) #dibujamos

        #lo mismo con las plumas
        plumas_pipeline.use()
        plumas_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        plumas_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")
        plumas_pipeline["transform"] = (tr.translate(-1.5, 0, 0) @ tr.rotationX(-np.pi/4)).reshape(16, 1, order="F")
        
        tex_plumas = texture_2D_setup(img_plumas)
        GL.glBindTexture(GL.GL_TEXTURE_2D, tex_plumas)
        plumas.draw(pyglet.gl.GL_TRIANGLES)
    
    pyglet.app.run()



        


