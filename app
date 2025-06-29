import pyglet
from OpenGL import GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path
import sys
from pyglet.window import key
from time import time

if sys.path[0] != "":
    sys.path.insert(0, "")

from OpenGL.GL import *
import grafica.transformations as tr
import grafica.gpu_shape as gs
from trimesh.curvature import discrete_gaussian_curvature_measure

import grafica.lighting_shaders as ls
import grafica.easy_shaders as es
import grafica.lighting_shaders as ls

#Definimos la clase para controlar el sistema
class Controller:
    def __init__(self):
        self.LA = 0
        self.LD = 0
        self.LS = 0
        self.KA = 0.1
        self.KD = 0.1
        self.KS = 0.1
        self.pipetipo = 1
        self.alturaluz = 1

    def variarLA(self):
        if 0 <= self.LA and self.LA <1:
            self.LA += 0.1
        if self.LA>1:
            self.LA = 0

    def variarLD(self):
        if 0 <= self.LD and self.LD <1:
            self.LD += 0.1
        if self.LD>1:
            self.LD = 0
    
    def variarLS(self):
        if 0 <= self.LS and self.LS <1:
            self.LS += 0.1
        if self.LS>1:
            self.LS = 0

    def variarKA(self):
        if 0 <= self.KA and self.KA <1:
            self.KA += 0.1
        if self.KA>1:
            self.KA = 0
    def variarKD(self):
        if 0 <= self.KD and self.KD <1:
            self.KD += 0.1
        if self.KD>1:
            self.KD = 0
    
    def variarKS(self):
        if 0 <= self.KS and self.KS <1:
            self.KS += 0.1
        if self.KS>1:
            self.KS = 0

    def variaralturaluz(self):
        if self.alturaluz == 4:
            self.alturaluz = 0
        else:
            self.alturaluz += 0.5


print("Estas con el modelo de iluminación Phong")
print("Presionar 2 para cambiar al modelo de iluminación Flat")
print("Presionar 3 para cambiar al modelo de iluminación Gouraud")
print("Para aumentar la altura de la posición de la luz presionar K")
print("Presionar Q para aumentar La")
print("Presionar W para aumentar Ls")
print("Presionar E para aumentar Ld")
print("Presionar A para aumentar Ka")
print("Presionar S para aumentar Ks")
print("Presionar D para aumentar Kd")

if __name__ == "__main__":
    width = 660
    height = 660
    window = pyglet.window.Window(width, height)

    window.program_state = {
        "total_time": 0.0,
        "projection": tr.perspective(60, float(650) / float(700), 0.001, 100),
        "view": tr.lookAt(np.array([2, 1 ,2]), np.array([0, 0, 0]), np.array([0, 1, 0])),}
    
    controller = Controller()

    with open(
        Path(os.path.dirname(__file__)) / "FS.glsl") as f:
        fragment_source_code = f.read()
        
    with open(Path(os.path.dirname(__file__)) / "VP.glsl") as f:
        vertex_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    fig_pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)
    fig_pipeline.use()
    figmesh = tm.load("assets/helice.off")
    bunny_scale = tr.uniformScale(1.0 / figmesh.scale)
    bunny_translate = tr.translate(*-figmesh.centroid)
    figmesh.apply_transform(tr.translate(0, 0, -figmesh.vertices[:, 2].min()))
    figmesh.apply_transform(bunny_scale @ bunny_translate)
    fig_vertex_list = tm.rendering.mesh_to_vertexlist(figmesh)

    
    @window.event
    def on_key_press(symbol,modifier):
        if(key.Q == symbol):
            controller.variarLA()
        if(key.E == symbol):
            controller.variarLD()
        if(key.W == symbol):
            controller.variarLS()
        if(key.A == symbol):
            controller.variarKA()
        if(key.D == symbol):
            controller.variarKD()
        if(key.S == symbol):
            controller.variarKS()
        if(key._1 == symbol):
            controller.pipetipo = 1
        if(key._2 == symbol):
            controller.pipetipo = 2
        if(key._3 == symbol):
            controller.pipetipo = 3
        if(key.K == symbol):
            controller.variaralturaluz()
        
        
    def createGPUShape1(pipeline, shape):
            gpuShape = es.GPUShape().initBuffers()
            pipeline.setupVAO(gpuShape)
            gpuShape.fillBuffers(shape[4][1], shape[3], GL_STATIC_DRAW)
            return gpuShape
        

    @window.event
    def on_draw():
        
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glLineWidth(1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        GL.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        window.clear()
        
    
        model = tr.translate(0,0,-1.5) @ tr.uniformScale(3) 
        gouraudPipeline = ls.SimpleGouraudShaderProgram()
        flatpipeline = ls.SimpleFlatShaderProgram()
        phongpipeline = ls.SimplePhongShaderProgram()


        if controller.pipetipo == 1:
            luzpipeline = phongpipeline
        if controller.pipetipo == 2:
            luzpipeline = flatpipeline
        if controller.pipetipo == 3:
            luzpipeline = gouraudPipeline

        luzy = controller.alturaluz

        glUseProgram(luzpipeline.shaderProgram)

        LA = controller.LA
        LD = controller.LD
        LS = controller.LS
        KA = controller.KA
        KD = controller.KD
        KS = controller.KS

        #componenetes La, Ld y Ls
        glUniform3f(glGetUniformLocation(luzpipeline.shaderProgram, "La"), LA,LA, LA)
        glUniform3f(glGetUniformLocation(luzpipeline.shaderProgram, "Ld"), LD, LD, LD)
        glUniform3f(glGetUniformLocation(luzpipeline.shaderProgram, "Ls"), LS,LS, LS)
        #componenetes La, Ld y Ls
        glUniform3f(glGetUniformLocation(luzpipeline.shaderProgram, "Ka"), KA,KA,KA)
        glUniform3f(glGetUniformLocation(luzpipeline.shaderProgram, "Kd"), KD, KD, KD)
        glUniform3f(glGetUniformLocation(luzpipeline.shaderProgram, "Ks"), KS, KS, KS)
    
        #Otros elementos para la ilucionación
        b = 1
        glUniform3f(glGetUniformLocation(luzpipeline.shaderProgram, "lightPosition"),b*np.cos(time()),luzy,b*np.sin(time()))
        glUniform1f(glGetUniformLocation(luzpipeline.shaderProgram, "cutoffangle"),20)
        glUniform1ui(glGetUniformLocation(luzpipeline.shaderProgram, "shininess"), 500)
        glUniform1f(glGetUniformLocation(luzpipeline.shaderProgram, "constantAttenuation"), 0.005)
        glUniform1f(glGetUniformLocation(luzpipeline.shaderProgram, "linearAttenuation"), 0.01)
        glUniform1f(glGetUniformLocation(luzpipeline.shaderProgram, "quadraticAttenuation"), 0.04)
        

        glUniformMatrix4fv(glGetUniformLocation(luzpipeline.shaderProgram, "projection"), 1, GL_TRUE, window.program_state["projection"])
        glUniformMatrix4fv(glGetUniformLocation(luzpipeline.shaderProgram, "view"), 1, GL_TRUE, window.program_state["view"])
        glUniformMatrix4fv(glGetUniformLocation(luzpipeline.shaderProgram, "model"), 1, GL_TRUE, model)
        #creamos la figura y le aplicamos el modelo de iluminación
        fig = createGPUShape1(phongpipeline,fig_vertex_list)
        luzpipeline.drawCall(fig)
        fig.clear()

        #etiquetas
        label = pyglet.text.Label(f'Kd = {round(KD,2)}',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=45, y=30,
                anchor_x='center', anchor_y='center')
        
        label1 = pyglet.text.Label(f'Ks = {round(KS,2)}',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=45, y=60,
                anchor_x='center', anchor_y='center')
        
        label2 = pyglet.text.Label(f'Ka = {round(KA,2)}',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=45, y=90,
                anchor_x='center', anchor_y='center')
        label3 = pyglet.text.Label(f'Ld= {round(LD,2)}',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=45, y=120,
                anchor_x='center', anchor_y='center')
        
        label4 = pyglet.text.Label(f'Ls = {round(LS,2)}',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=45, y=150,
                anchor_x='center', anchor_y='center')
        
        label5 = pyglet.text.Label(f'La = {round(LA,2)}',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=45, y=180,
                anchor_x='center', anchor_y='center')
        
        label6 = pyglet.text.Label(f"Altura Luz = {luzy}",
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=65, y=210,
                anchor_x='center', anchor_y='center')
        
        coordx = 150
        coordy = 600
        if controller.pipetipo == 1:
            labelmod = pyglet.text.Label(f'Modelo de Iluminación: Phong',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=coordx, y=coordy,
                anchor_x='center', anchor_y='center')
        if controller.pipetipo == 2:
            labelmod = pyglet.text.Label(f'Modelo de Iluminación: Flat',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=coordx, y=coordy,
                anchor_x='center', anchor_y='center')
        if controller.pipetipo == 3:
            labelmod = pyglet.text.Label(f'Modelo de Iluminación: Gouraud',
                font_name='Times New Roman',
                font_size=15,
                color=(0,0,0,255),
                x=coordx, y=coordy,
                anchor_x='center', anchor_y='center')
        
        label.draw()
        label1.draw()
        label2.draw()
        label3.draw()
        label4.draw()
        label5.draw()
        label6.draw()
        labelmod.draw()
    
    pyglet.app.run()