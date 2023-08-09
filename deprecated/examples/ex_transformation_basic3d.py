import glfw
from OpenGL.GL import *
import OpenGL.GL.shaders
import numpy as np
import sys
import os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr
import grafica.basic_shapes as bs
import grafica.easy_shaders as es

__author__ = "Ivan Sipiran"
__license__ = "MIT"

def on_key(window, key, scancode, action, mods):

    if action != glfw.PRESS:
        return
    
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(window, True)
    

if __name__ == "__main__":

    # Initialize glfw
    if not glfw.init():
        glfw.set_window_should_close(window, True)

    width = 1000
    height = 1000
    title = "First transformations"
    window = glfw.create_window(width, height, title, None, None)

    if not window:
        glfw.terminate()
        glfw.set_window_should_close(window, True)

    glfw.make_context_current(window)

    glfw.set_key_callback(window, on_key)

    # Defining shader programs
    mvpPipeline = es.SimpleModelViewProjectionShaderProgram()
    glUseProgram(mvpPipeline.shaderProgram)

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
    gpuAxis = createGPUShape(mvpPipeline, bs.createAxis(3))
    gpuCube = createGPUShape(mvpPipeline, bs.createFacetedCube())

    # Setting up the projection transform
    glUseProgram(mvpPipeline.shaderProgram)
    
    view = tr.lookAt(
            np.array([4,4,4]),
            np.array([0,0,0]),
            np.array([0,1,0])
        )
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "view"), 1, GL_TRUE, view)
    
    projection = tr.perspective(60, float(width)/float(height), 0.1, 100)
    glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "projection"), 1, GL_TRUE, projection)
    
    glfw.swap_interval(0)
        
    while not glfw.window_should_close(window):

        # Using GLFW to check for input events
        glfw.poll_events()

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        # Drawing shapes
        glUseProgram(mvpPipeline.shaderProgram)
       
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, tr.identity())
        mvpPipeline.drawCall(gpuAxis, GL_LINES)

        modelTransform =tr.identity()
        glUniformMatrix4fv(glGetUniformLocation(mvpPipeline.shaderProgram, "model"), 1, GL_TRUE, modelTransform)
        mvpPipeline.drawCall(gpuCube)

        # Once the drawing is rendered, buffers are swap so an uncomplete drawing is never seen.
        glfw.swap_buffers(window)
        

    # freeing GPU memory
    gpuAxis.clear()
    gpuCube.clear()

    glfw.terminate()