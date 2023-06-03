import pyglet
import trimesh as tm
from pathlib import Path
import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
)

from OpenGL import GL
from PIL import Image
import grafica.transformations as tr
from grafica.lighting_shaders import SimpleGouraudShaderProgram as Gouraud
from grafica.gpu_shape import GPUShape
import numpy as np
from pyglet.graphics.shader import Shader, ShaderProgram
from itertools import chain

def trimesh_to_gpu(mesh, pipeline):
    gpu_shapes = {}

    for mesh_name, submesh in mesh.geometry.items():
        mesh_parts = tm.rendering.mesh_to_vertexlist(submesh)
        # print(mesh_parts[6], len(mesh_parts[6][1]))

        if mesh_parts[6][0].startswith("t2f"):
            material_size = 2
            material_part = np.array(mesh_parts[6][1]).reshape(-1, material_size)
        elif mesh_parts[6][0].startswith("c4B"):
            material_size = 4
            material_part = (
                np.array(mesh_parts[6][1]).reshape(-1, material_size) / 255.0
            )
        else:
            raise ValueError("unsupported mesh. maybe add colors/textures?")

        print(submesh.vertices.shape)
        n_vertices = submesh.vertices.shape[0]
        mesh_vertex_data = np.hstack(
            [
                # posiciones
                np.array(mesh_parts[4][1]).reshape(n_vertices, 3),
                # colores (el shader que usamos pide colores y el pajarito no trae, así que le ponemos un color blanco)
                np.ones(shape=(n_vertices, 3)) * 0.5,
                # normales
                np.array(mesh_parts[5][1]).reshape(n_vertices, 3),
                # texcoords
                # material_part,
            ]
        ).reshape(1, -1)

        mesh_vertex_data = np.array(np.squeeze(mesh_vertex_data))
        mesh_indices = mesh_parts[3]

        gpu_shapes[mesh_name] = GPUShape().initBuffers()
        pipeline.setupVAO(gpu_shapes[mesh_name])
        gpu_shapes[mesh_name].fillBuffers(
            mesh_vertex_data, mesh_indices, GL.GL_STATIC_DRAW
        )

    return gpu_shapes


def setup_light(pipeline):
    GL.glUseProgram(pipeline.shaderProgram)

    # White light in all components: ambient, diffuse and specular.
    GL.glUniform3f(GL.glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
    GL.glUniform3f(GL.glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
    GL.glUniform3f(GL.glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

    # Object is barely visible at only ambient. Bright white for diffuse and specular components.
    GL.glUniform3f(GL.glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
    GL.glUniform3f(GL.glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
    GL.glUniform3f(GL.glGetUniformLocation(pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)

    # TO DO: Explore different parameter combinations to understand their effect!

    GL.glUniform3f(
        GL.glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), -2, 2, -1
    )
    GL.glUniform1ui(GL.glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

    GL.glUniform1f(
        GL.glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001
    )
    GL.glUniform1f(
        GL.glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03
    )
    GL.glUniform1f(
        GL.glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01
    )

def setup_matrices(pipeline, model, view, projection):
    GL.glUseProgram(pipeline.shaderProgram)
    GL.glUniformMatrix4fv(
        GL.glGetUniformLocation(gouraud.shaderProgram, "model"),
        1,
        GL.GL_TRUE,
        model,
    )
    GL.glUniformMatrix4fv(
        GL.glGetUniformLocation(gouraud.shaderProgram, "projection"),
        1,
        GL.GL_TRUE,
        projection,
    )
    GL.glUniformMatrix4fv(
        GL.glGetUniformLocation(gouraud.shaderProgram, "view"), 1, GL.GL_TRUE, view
    )

def create_quad():
    vertices = np.array(
        [
            -1,
            -1,
            0.0,
            1.0,
            204 / 255.0,
            1.0,  # inf izq
            1,
            -1,
            0.0,
            1.0,
            204 / 255.0,
            1.0,  # if der
            1,
            1,
            0.0,
            204 / 255.0,
            1.0,
            1.0,  # sup der
            -1,
            1,
            0.0,
            204 / 255.0,
            1.0,
            1.0,  # sup izq
        ],
        dtype=np.float32,
    )

    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
    return vertices, indices

if __name__ == "__main__":
    win = pyglet.window.Window(640, 480)
    # cargamos al zorzal
    zorzal = tm.load(
        Path(os.path.dirname(__file__)) / ".." / ".." / "assets" / "zorzal2.obj"
    )

    
    # usaremos un shader del modulo gráfica. por ej., el de Gouraud.
    # noten que ese shader tiene variables específicas. 
    # así que la función trimesh_to_gpu está adaptada para ese shader
    gouraud = Gouraud()
    zorzal_gpu_shape = trimesh_to_gpu(zorzal, gouraud)

    # usaremos estas matrices. las configuramos
    viewPos = np.array([0, 0, 2])
    view = tr.lookAt(viewPos, np.array([0, 0, 0]), np.array([0, 1, 0]))
    projection = tr.perspective(60, float(win.width) / float(win.height), 0.001, 100)

    # pára llevar el modelo al origen y verlo de perfil hacemos esto.
    # (como en el ej de los pajaritos boids)
    zorzal_centroid = zorzal.centroid
    model_transform = tr.matmul(
        [tr.rotationY(np.pi * 0.5), tr.translate(*-zorzal_centroid)]
    )

    setup_matrices(gouraud, model_transform, view, projection)
    setup_light(gouraud)

    # ahora configuraremos un shader de pyglet. usaremos el cuadro de fondo 
    # del programa de los pajaritos. es la misma función!
    bg_vertices, bg_indices = create_quad()

    # creamos el shader. puede ser con un archivo como en el ejemplo de partículas
    # o bien con el texto directo puesto aquí.
    pyglet_vert_shader = Shader("""
    #version 330
    in vec3 position;
    in vec3 color;

    out vec3 fragColor;

    void main()
    {
        fragColor = color;
        gl_Position = vec4(position, 1.0f);
    }
    """, "vertex")

    pyglet_frag_shader = Shader("""
    #version 330

    in vec3 fragColor;
    out vec4 outColor;

    void main()
    {
        outColor = vec4(fragColor, 1.0f);
    }
    """, "fragment")

    pyglet_pipeline = ShaderProgram(pyglet_vert_shader, pyglet_frag_shader)
    
    # ahora le entregaremos los datos de nuestro objeto a la gpu.
    # noten que lo dibujaremos con GL_TRIANGLES
    bg_data = pyglet_pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, bg_indices)
    
    # ojo: bg_vertices _ya está_ en formato lista. por ej: [px, py, pz, cr, cg, cb, px, py...]
    # necesitamos separar las posiciones de los colores para entregárselos a pyglet
    # podemos hacer magia Pythonica con chain y zip :)

    bg_data.position[:] = tuple(chain(*zip(bg_vertices[0::6], bg_vertices[1::6], bg_vertices[2::6])))
    bg_data.color[:] = tuple(chain(*zip(bg_vertices[3::6], bg_vertices[4::6], bg_vertices[5::6])))
    # NANI!??? qué significa eso? propuesto ;)
    
    

    @win.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        win.clear()

        # aquí dibujamos algo con los shaders de pyglet
        GL.glDisable(GL.GL_DEPTH_TEST)
        pyglet_pipeline.use()
        bg_data.draw(GL.GL_TRIANGLES)

        # aquí dibujamos algo con los shaders del módulo grafica
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        GL.glUseProgram(gouraud.shaderProgram)

        GL.glUniform3fv(
            GL.glGetUniformLocation(gouraud.shaderProgram, "viewPosition"), 1, viewPos
        )

        for gpu_shape in zorzal_gpu_shape.values():
            gouraud.drawCall(gpu_shape)

    pyglet.app.run()
