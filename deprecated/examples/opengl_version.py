# coding=utf-8
"""
Sample code to determine OpenGL version available on the current machine.
It attempts to set OpenGL core profile 3.3.
"""

import glfw
from OpenGL.GL import *
import sys


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    window = glfw.create_window(1, 1, "OpenGL versions", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    print("=== Lastest OpenGL version on this machine ===")
    print("GPU                      : ", glGetString(GL_VENDOR))
    print("Renderer                 : ", glGetString(GL_RENDERER))
    print("OpenGL                   : ", glGetString(GL_VERSION))
    print("Shading Language Version : ", glGetString(GL_SHADING_LANGUAGE_VERSION))
    print()

    # We terminate and initialize again glfw in order to specify another context
    glfw.terminate()
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    # Here is an attempt to use OpenGL core profile 3.3
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # if you comment the previous hints, it will use the newer OpenGL version available on the machine.

    window = glfw.create_window(1, 1, "OpenGL versions", None, None)

    if not window:
        glfw.terminate()
        print("Failed to create an GLFW window")
        sys.exit()

    glfw.make_context_current(window)

    print("=== Setting to OpenGL 3.3 ===")
    print("GPU                      : ", glGetString(GL_VENDOR))
    print("Renderer                 : ", glGetString(GL_RENDERER))
    print("OpenGL                   : ", glGetString(GL_VERSION))
    print("Shading Language Version : ", glGetString(GL_SHADING_LANGUAGE_VERSION))

    glfw.terminate()