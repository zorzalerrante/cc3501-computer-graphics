# coding=utf-8
"""Using OpenMesh to compute normals for lighting effects"""

import glfw
import copy
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import openmesh
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls
from grafica.assets_path import getAssetPath

__author__ = "Daniel Calderon"
__license__ = "MIT"


# A class to store the application control
class Controller:
    def __init__(self):
        self.fillPolygon = True


# We will use the global controller as communication with the callback function
controller = Controller()

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    global controller

    if key == glfw.KEY_SPACE:
        controller.fillPolygon = not controller.fillPolygon

    elif key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)


def createPyramidMesh(textured=False):

    mesh = openmesh.TriMesh()

    nw = mesh.add_vertex(np.array([-0.5, 0.5, 0.0]))
    ne = mesh.add_vertex(np.array([0.5, 0.5, 0.0]))
    sw = mesh.add_vertex(np.array([-0.5, -0.5, 0.0]))
    se = mesh.add_vertex(np.array([0.5, -0.5, 0.0]))
    t = mesh.add_vertex(np.array([0.0, 0.0, 1.0])) # Top Vertex

    mesh.add_face([ne, nw, t]) # N
    mesh.add_face([se, ne, t]) # E
    mesh.add_face([sw, se, t]) # S
    mesh.add_face([nw, sw, t]) # W
    mesh.add_face([ne, se, sw]) # Bottom
    mesh.add_face([sw, nw, ne]) # Bottom

    if textured:
        # Do note the trick, faces at the east and west are sampling the texture in the opposite direction.
        # If you do not want to do this, you need to replicate the spatial vertex and assign different texture coordinates to each of them.
        # This is only to use the same texture on each side of the pyramid.
        mesh.set_texcoord2D(nw, [1.0, 1.0])
        mesh.set_texcoord2D(ne, [0.0, 1.0])
        mesh.set_texcoord2D(sw, [0.0, 1.0])
        mesh.set_texcoord2D(se, [1.0, 1.0])
        mesh.set_texcoord2D(t,  [0.5, 0.0])

    return mesh


def toShape(mesh, color=None, textured=False, verbose=False):
    assert isinstance(mesh, openmesh.TriMesh)
    assert (color != None) != textured, "The mesh will be colored or textured, only one of these need to be specified."

    # Requesting normals per face
    mesh.request_face_normals()

    # Requesting normals per vertex
    mesh.request_vertex_normals()

    # Computing all requested normals
    mesh.update_normals()

    # You can also update specific normals
    #mesh.update_face_normals()
    #mesh.update_vertex_normals()
    #mesh.update_halfedge_normals()

    # At this point, we are sure we have normals computed for each face.
    assert mesh.has_face_normals()

    vertices = []
    indices = []

    # To understand how iteraors and circulators works in OpenMesh, check the documentation at:
    # https://www.graphics.rwth-aachen.de:9000/OpenMesh/openmesh-python/-/blob/master/docs/iterators.rst

    def extractCoordinates(numpyVector3):
        assert len(numpyVector3) == 3
        x = vertex[0]
        y = vertex[1]
        z = vertex[2]
        return [x,y,z]

    # This is inefficient, but it works!
    # You can always optimize it further :)

    # Checking each face
    for faceIt in mesh.faces():
        faceId = faceIt.idx()
        if verbose: print("face: ", faceId)

        # Checking each vertex of the face
        for faceVertexIt in mesh.fv(faceIt):
            faceVertexId = faceVertexIt.idx()

            # Obtaining the position and normal of each vertex
            vertex = mesh.point(faceVertexIt)
            normal = mesh.normal(faceVertexIt)
            if verbose: print("vertex ", faceVertexId, "-> position: ", vertex, " normal: ", normal)

            x, y, z = extractCoordinates(vertex)
            nx, ny, nz = extractCoordinates(normal)

            if textured:
                assert mesh.has_vertex_texcoords2D()

                texcoords = mesh.texcoord2D(faceVertexIt)
                tx = texcoords[0]
                ty = texcoords[1]
                
                vertices += [x, y, z, tx, ty, nx, ny, nz]
                indices += [len(vertices)//8 - 1]
            else:
                assert color != None

                r = color[0]
                g = color[1]
                b = color[2]

                vertices += [x, y, z, r, g, b, nx, ny, nz]
                indices += [len(vertices)//9 - 1]
        
        if verbose: print()

    return bs.Shape(vertices, indices)


if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        sys.exit(1)

    width = 600
    height = 600

    window = glfw.create_window(width, height, "OpenMesh Lighting Demo", None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, on_key)

    # Different shader programs for different lighting strategies
    lightingPipeline = ls.SimplePhongShaderProgram()
    texturePipeline = ls.SimpleTexturePhongShaderProgram()
    # if your machine does not support phong, you can use Gouraud instead.
    #lightingPipeline = ls.SimpleGouraudShaderProgram()
    #texturePipeline = ls.SimpleTextureGouraudShaderProgram()

    # This shader program does not consider lighting
    colorPipeline = es.SimpleModelViewProjectionShaderProgram()

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # As we work in 3D, we need to check which part is in front,
    # and which one is at the back
    glEnable(GL_DEPTH_TEST)

    # Convenience function to ease initialization
    def createGPUShape(pipeline, shape):
        gpuShape = es.GPUShape().initBuffers()
        pipeline.setupVAO(gpuShape)
        gpuShape.fillBuffers(shape.vertices, shape.indices, GL_STATIC_DRAW)
        return gpuShape

    # Creating shapes on GPU memory
    gpuAxis = createGPUShape(colorPipeline, bs.createAxis(4))

    # Note: the vertex attribute layout (stride) is the same for the 3 lighting pipelines in
    # this case: flatPipeline, gouraudPipeline and phongPipeline. Hence, the VAO setup can
    # be the same.
    meshPyramid = createPyramidMesh()
    shapePyramid = toShape(meshPyramid, color=(0.6, 0.1, 0.1), verbose=True)
    gpuPyramid = createGPUShape(lightingPipeline, shapePyramid)

    meshTexturedPyramid = createPyramidMesh(True)
    shapeTexturedPyramid = toShape(meshTexturedPyramid, textured=True, verbose=False)
    gpuTexturedPyramid = createGPUShape(texturePipeline, shapeTexturedPyramid)
    gpuTexturedPyramid.texture = es.textureSimpleSetup(
        getAssetPath("bricks.jpg"), GL_CLAMP_TO_EDGE, GL_CLAMP_TO_EDGE, GL_LINEAR, GL_LINEAR)
    
    #print(shapeTexturedPyramid)

    t0 = glfw.get_time()
    camera_theta = np.pi/4

    def setupLightingDefaults(pipeline):
        glUseProgram(pipeline.shaderProgram)

        # White light in all components: ambient, diffuse and specular.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "La"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ld"), 1.0, 1.0, 1.0)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ls"), 1.0, 1.0, 1.0)

        # Object is barely visible at only ambient. Bright white for diffuse and specular components.
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ka"), 0.2, 0.2, 0.2)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Kd"), 0.9, 0.9, 0.9)
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "Ks"), 1.0, 1.0, 1.0)
        
        glUniform3f(glGetUniformLocation(pipeline.shaderProgram, "lightPosition"), -5, -5, 5)
        glUniform1ui(glGetUniformLocation(pipeline.shaderProgram, "shininess"), 100)

        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "constantAttenuation"), 0.0001)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "linearAttenuation"), 0.03)
        glUniform1f(glGetUniformLocation(pipeline.shaderProgram, "quadraticAttenuation"), 0.01)

    # Setting up uniforms for both lighting pipelines, colored and textured
    setupLightingDefaults(lightingPipeline)
    setupLightingDefaults(texturePipeline)

    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Getting the time difference from the previous iteration
        t1 = glfw.get_time()
        dt = t1 - t0
        t0 = t1

        if (glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS):
            camera_theta -= 2 * dt

        if (glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS):
            camera_theta += 2* dt
            
        projection = tr.perspective(45, float(width)/float(height), 0.1, 100)

        camX = 3 * np.sin(camera_theta)
        camY = 3 * np.cos(camera_theta)

        viewPos = np.array([camX,camY,2])

        view = tr.lookAt(
            viewPos,
            np.array([0,0,0]),
            np.array([0,0,1])
        )

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Filling or not the shapes depending on the controller state
        if (controller.fillPolygon):
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

        # The axis is drawn without lighting effects
        glUseProgram(colorPipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(colorPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        colorPipeline.drawCall(gpuAxis, GL_LINES)

        # Drawing the single color pyramid
        glUseProgram(lightingPipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(lightingPipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(lightingPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(0.75,0,0))
        lightingPipeline.drawCall(gpuPyramid)

        # Drawing the textured pyramid
        glUseProgram(texturePipeline.shaderProgram)
        glUniform3f(glGetUniformLocation(texturePipeline.shaderProgram, "viewPosition"), viewPos[0], viewPos[1], viewPos[2])
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "view"), 1, GL_TRUE, view)
        glUniformMatrix4fv(glGetUniformLocation(texturePipeline.shaderProgram, "model"), 1, GL_TRUE, tr.translate(-0.75,0,0))
        texturePipeline.drawCall(gpuTexturedPyramid)
        
        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)

    # freeing GPU memory
    gpuAxis.clear()
    gpuPyramid.clear()
    gpuTexturedPyramid.clear()

    glfw.terminate()
