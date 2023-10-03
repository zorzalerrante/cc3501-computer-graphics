from OpenGL.GL import (
    glGenTextures,
    GL_TEXTURE_2D,
    glTexParameteri,
    GL_TEXTURE_MIN_FILTER,
    GL_TEXTURE_MAG_FILTER,
    glBindTexture,
    GL_TEXTURE_WRAP_S,
    GL_TEXTURE_WRAP_T,
    GL_RGB,
    GL_RGBA,
    glTexImage2D,
    GL_UNSIGNED_BYTE,
    GL_CLAMP_TO_EDGE,
    GL_LINEAR,
    GL_NEAREST,
    GL_REPEAT,
)

from PIL import Image
import numpy as np

SIZE_IN_BYTES = 4


def texture_2D_setup(
    image,
    sWrapMode=GL_CLAMP_TO_EDGE,
    tWrapMode=GL_CLAMP_TO_EDGE,
    minFilterMode=GL_LINEAR,
    maxFilterMode=GL_LINEAR,
    flip_top_bottom=True
):
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

    if flip_top_bottom:
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
