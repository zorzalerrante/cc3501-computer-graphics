import numpy as np
import trimesh
from OpenGL.GL import *
from PIL import Image

SIZE_IN_BYTES = 4


def prepare_gpu_buffer(
    pipeline, vertices, indices, normals=True, texture=True, colors=False, color_alpha=False
):
    vertices = np.array(vertices, dtype=np.float32)
    indices = np.array(indices, dtype=np.uint32)

    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)
    size = len(indices)

    vertex_len = 3
    pos_offset = 0
    normal_offset = 0
    color_offset = 0
    texture_offset = 0

    if normals:
        vertex_len += 3
        normal_offset += 3
        texture_offset += 3
        color_offset += 3
    if colors:
        vertex_len += 3 + int(color_alpha)
        texture_offset += 3
        color_offset += 3 + int(color_alpha)
    if texture:
        vertex_len += 2
        texture_offset += 3

    stride = SIZE_IN_BYTES * vertex_len

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)

    position = glGetAttribLocation(pipeline, "position")
    glVertexAttribPointer(
        position, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(pos_offset)
    )
    glEnableVertexAttribArray(position)

    if colors:
        color = glGetAttribLocation(pipeline, "color")
        if color >= 0:
            glVertexAttribPointer(
                color,
                3 + int(color_alpha),
                GL_FLOAT,
                GL_FALSE,
                stride,
                ctypes.c_void_p(color_offset * SIZE_IN_BYTES),
            )
            glEnableVertexAttribArray(color)

    if texture:
        texCoords = glGetAttribLocation(pipeline, "texCoords")
        if texCoords >= 0:
            glVertexAttribPointer(
                texCoords,
                2,
                GL_FLOAT,
                GL_FALSE,
                stride,
                ctypes.c_void_p(texture_offset * SIZE_IN_BYTES),
            )
            glEnableVertexAttribArray(texCoords)

    # Unbinding current vao
    glBindVertexArray(0)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(
        GL_ARRAY_BUFFER, len(vertices) * SIZE_IN_BYTES, vertices, GL_STATIC_DRAW
    )

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(
        GL_ELEMENT_ARRAY_BUFFER, len(indices) * SIZE_IN_BYTES, indices, GL_STATIC_DRAW
    )
    return {"vbo": vbo, "vao": vao, "ebo": ebo, "size": size}


def texture_setup(image, sWrapMode, tWrapMode, minFilterMode, maxFilterMode):
    # wrapMode: GL_REPEAT, GL_CLAMP_TO_EDGE
    # filterMode: GL_LINEAR, GL_NEAREST
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)

    # texture wrapping params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, sWrapMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, tWrapMode)

    # texture filtering params
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, minFilterMode)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, maxFilterMode)

    image = image.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = np.array(image, np.uint8)

    if image.mode == "RGB":
        internalFormat = GL_RGB
        format = GL_RGB
    elif image.mode == "RGBA":
        internalFormat = GL_RGBA
        format = GL_RGBA
    else:
        print("Image mode not supported.")
        raise Exception()

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        internalFormat,
        image.size[0],
        image.size[1],
        0,
        format,
        GL_UNSIGNED_BYTE,
        img_data,
    )

    return texture


def trimesh_to_gpu(mesh, pipeline):
    gpu_mesh = {}
    import sys
    for mesh_name, submesh in mesh.geometry.items():
        mesh_parts = trimesh.rendering.mesh_to_vertexlist(submesh)
        print(mesh_parts[6], len(mesh_parts[6][1]))

        if mesh_parts[6][0].startswith('t2f'):
            material_size = 2
            material_part = np.array(mesh_parts[6][1]).reshape(-1, material_size)
        elif mesh_parts[6][0].startswith('c4B'):
            material_size = 4
            material_part = np.array(mesh_parts[6][1]).reshape(-1, material_size) / 255.0 
        else:
            raise ValueError('unsupported mesh. maybe add colors/textures?')
        
        mesh_vertex_data = np.hstack(
            [
                np.array(mesh_parts[4][1]).reshape(-1, 3),
                np.array(mesh_parts[5][1]).reshape(-1, 3),
                material_part,
            ]
        ).reshape(1, -1)
        
        mesh_vertex_data = np.array(np.squeeze(mesh_vertex_data))
        # print(mesh_vertex_data.shape)
        # print(mesh_vertex_data[0:10])
        # mesh_indices = list(zip(mesh_parts[3][0::3], mesh_parts[3][1::3], mesh_parts[3][2::3]))
        mesh_indices = mesh_parts[3]
        # print(mesh_indices[0:10])
        gpu_mesh[mesh_name] = prepare_gpu_buffer(
            pipeline, mesh_vertex_data, mesh_indices, texture=material_size == 2, colors=material_size == 4, color_alpha=True
        )
        # print(mesh_name, mesh_parts[4][0], mesh_parts[5][0], mesh_parts[6][0])

        if submesh.visual.material.image is not None:
            gpu_mesh[mesh_name]["texture"] = texture_setup(
                submesh.visual.material.image, GL_REPEAT, GL_REPEAT, GL_LINEAR, GL_LINEAR
            )
        # print(mesh_name, self.gpu_birds[mesh_name])

    return gpu_mesh
