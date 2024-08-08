import pygame as pg
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.GL.shaders import compileProgram, compileShader
import sys 
import pyrr 
import trimesh

if sys.path[0] != "":
    sys.path.insert(0, "")

class App:
    def __init__(self):
        pg.init()
        pg.display.set_mode((800,600), pg.OPENGL|pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        glClearColor(0.0, 0.0, 0.0, 1)
        glEnable(GL_DEPTH_TEST)

        self.ssao_enabled = True
        
        self.shader = self.createShader("examples/SSAO/shaders/simple_vertex_shader.glsl", "examples/SSAO/shaders/simple_fragment_shader.glsl")
        self.gBufferShader = self.createShader("examples/SSAO/shaders/g_buffer_vertex.glsl", "examples/SSAO/shaders/g_buffer_fragment.glsl")
        self.ssaoShader = self.createShader("examples/SSAO/shaders/ssao_vertex.glsl", "examples/SSAO/shaders/ssao_fragment.glsl")
        self.blurShaderH = self.createShader("examples/SSAO/shaders/blur_vertex.glsl", "examples/SSAO/shaders/blur_fragment_h.glsl")
        self.blurShaderV = self.createShader("examples/SSAO/shaders/blur_vertex.glsl", "examples/SSAO/shaders/blur_fragment_v.glsl")
        
        self.models = self.load_model("examples/SSAO/sportsCar.obj")
        self.floor = self.create_floor()

        self.projection = pyrr.matrix44.create_perspective_projection(
            fovy = 45, aspect = 800/600,
            near = 0.1, far = 100, dtype=np.float32
        )

        eye = pyrr.Vector3([0, 2, 5])
        target = pyrr.Vector3([0, 0, 0])
        up = pyrr.Vector3([0, 1, 0])
        self.view = pyrr.matrix44.create_look_at(eye, target, up)

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")
        self.viewMatrixLocation = glGetUniformLocation(self.shader, "view")
        self.projectionMatrixLocation = glGetUniformLocation(self.shader, "projection")
        self.colorLocation = glGetUniformLocation(self.shader, "color")
        self.lightPosLocation = glGetUniformLocation(self.shader, "lightPos")
        self.viewPosLocation = glGetUniformLocation(self.shader, "viewPos")
        self.ssaoTextureLocation = glGetUniformLocation(self.shader, "ssaoTexture")
        self.ssaoEnabledLocation = glGetUniformLocation(self.shader, "ssaoEnabled")

        glUseProgram(self.shader)
        glUniformMatrix4fv(self.viewMatrixLocation, 1, GL_FALSE, self.view)
        glUniformMatrix4fv(self.projectionMatrixLocation, 1, GL_FALSE, self.projection)

        self.lightPos = pyrr.Vector3([2.0, 2.0, .0])
        glUniform3f(self.lightPosLocation, self.lightPos.x, self.lightPos.y, self.lightPos.z)

        # Configurar G-Buffer
        self.gBuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.gBuffer)

        # Textura de posición
        self.gPosition = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.gPosition)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, 800, 600, 0, GL_RGB, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.gPosition, 0)

        # Textura de normales
        self.gNormal = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.gNormal)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB16F, 800, 600, 0, GL_RGB, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT1, GL_TEXTURE_2D, self.gNormal, 0)

        # Buffer de profundidad
        self.rboDepth = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, self.rboDepth)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT, 800, 600)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, self.rboDepth)

        # Indicar a OpenGL que vamos a renderizar a múltiples buffers
        glDrawBuffers(2, (GL_COLOR_ATTACHMENT0, GL_COLOR_ATTACHMENT1))

        # Verificar que el framebuffer esté completo
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("Error: Framebuffer no está completo!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Crear SSAO framebuffer
        self.ssaoFBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.ssaoFBO)
        
        # Crear textura de color para SSAO
        self.ssaoColorBuffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.ssaoColorBuffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, 800, 600, 0, GL_RED, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.ssaoColorBuffer, 0)
        
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("SSAO Framebuffer no está completo!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Crear framebuffer para el desenfoque
        self.blurFBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.blurFBO)

        # Crear textura para el resultado del desenfoque
        self.blurColorBuffer = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.blurColorBuffer)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RED, 800, 600, 0, GL_RED, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.blurColorBuffer, 0)

        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            print("Blur Framebuffer no está completo!")

        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Generar kernel SSAO y textura de ruido
        self.ssaoKernel = self.generate_ssao_kernel()
        self.noiseTexture = self.generate_noise_texture()
        self.mainLoop()

    def createShader(self, vertexfilepath, fragmentfilepath):
        with open(vertexfilepath, 'r') as f:
            vertex_src = f.readlines()
        with open(fragmentfilepath, 'r') as f:
            fragment_src = f.readlines()

        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER)
        )
        return shader

    def load_model(self, filename):
        scene = trimesh.load(filename)
        print(f"Loaded scene with {len(scene.geometry)} geometries")
        
        models = []
        
        for name, geometry in scene.geometry.items():
            print(f"Processing geometry: {name}")
            print(f"Vertex count: {len(geometry.vertices)}")
            print(f"Face count: {len(geometry.faces)}")
            
            if not geometry.vertex_normals.any():
                geometry.generate_normals()

            #Garantizar la orientación correcta de las caras y ajustar las normales
            geometry.fix_normals()
            
            vertices = np.hstack((geometry.vertices, geometry.vertex_normals))
            vertices = vertices.astype(np.float32)

            # Extraer los índices de las caras
            indices = geometry.faces.flatten().astype(np.uint32)

            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)

            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

            ebo = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

            #Extraer y normalizar color de material
            if hasattr(geometry.visual, 'material'):
                material = geometry.visual.material
                if hasattr(material, 'diffuse'):
                    color = np.array(material.diffuse[:3]) / 255.0  # Normaliza a rango 0-1 
                else:
                    color = np.array([0.8, 0.8, 0.8])
            else:
                color = np.array([0.8, 0.8, 0.8])
            
            print(f"Material color: {color}")

            models.append({
                'vao': vao,
                'vbo': vbo,
                'ebo': ebo,
                'index_count': len(indices),
                'color': color
            })

        return models

    def create_floor(self):
        vertices = np.array([
            -10, 0, -10, 0, 1, 0,
             10, 0, -10, 0, 1, 0,
             10, 0,  10, 0, 1, 0,
            -10, 0,  10, 0, 1, 0
        ], dtype=np.float32)

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

        return {'vao': vao, 'vbo': vbo, 'vertex_count': 4}

    def mainLoop(self):
        running = True 
        while running:
            for event in pg.event.get():
                if (event.type == pg.QUIT):
                    running = False
                elif event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE:
                        self.ssao_enabled = not self.ssao_enabled
                        print("SSAO:", "Activado" if self.ssao_enabled else "Desactivado")

            # Primera pasada: Renderizar al G-Buffer
            glBindFramebuffer(GL_FRAMEBUFFER, self.gBuffer)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.gBufferShader)
            self.render_scene(self.gBufferShader)

            # Segunda pasada: SSAO
            glBindFramebuffer(GL_FRAMEBUFFER, self.ssaoFBO)
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.ssaoShader)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.gPosition)
            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.gNormal)
            glActiveTexture(GL_TEXTURE2)
            glBindTexture(GL_TEXTURE_2D, self.noiseTexture)
            for i in range(64):
                glUniform3fv(glGetUniformLocation(self.ssaoShader, f"samples[{i}]"), 1, self.ssaoKernel[i])
            glUniformMatrix4fv(glGetUniformLocation(self.ssaoShader, "projection"), 1, GL_FALSE, self.projection)
            self.render_quad()

            # Tercera pasada: Desenfoque horizontal
            glBindFramebuffer(GL_FRAMEBUFFER, self.blurFBO)
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.blurShaderH)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.ssaoColorBuffer)
            self.render_quad()

            # Cuarta pasada: Desenfoque vertical
            glBindFramebuffer(GL_FRAMEBUFFER, self.ssaoFBO)  # Reutilizamos el FBO del SSAO
            glClear(GL_COLOR_BUFFER_BIT)
            glUseProgram(self.blurShaderV)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.blurColorBuffer)
            self.render_quad()

            # Quinta pasada: Renderizar la escena final (con SSAO?)
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glUseProgram(self.shader)
            
            # Pasar la posición de la vista al shader
            glUniform3f(self.viewPosLocation, 0, 2, 5)  # Usa las mismas coordenadas que usaste para crear la matriz de vista
            
            # Activar y vincular la textura SSAO con desenfoque
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.ssaoColorBuffer)
            glUniform1i(self.ssaoTextureLocation, 0)

            glUniform1i(self.ssaoEnabledLocation, int(self.ssao_enabled))
            
            self.render_scene(self.shader)

            pg.display.flip()

            self.clock.tick(60)
        self.quit()

    def generate_ssao_kernel(self, kernel_size=64):
        kernel = []
        for i in range(kernel_size):
            sample = np.array([
                np.random.uniform(-1, 1),
                np.random.uniform(-1, 1),
                np.random.uniform(0, 1)
            ])
            sample = sample / np.linalg.norm(sample)
            scale = float(i) / kernel_size
            scale = 0.1 + (scale * scale) * 0.9  
            sample *= scale
            kernel.append(sample)
        return np.array(kernel, dtype=np.float32)

    def generate_noise_texture(self, size=4):
        noise = np.random.uniform(0, 1, (size, size, 3)).astype(np.float32)
        noise[:,:,2] = 0  # Sólo necesitamos componentes x e y
        
        # Crear y configurar la textura de ruido
        noiseTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, noiseTexture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, size, size, 0, GL_RGB, GL_FLOAT, noise)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        
        return noiseTexture

    def render_scene(self, shader):
        # Renderizar el piso
        floor_model = pyrr.matrix44.create_identity(dtype=np.float32)
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, floor_model)
        if shader == self.shader:  # Solo para el shader original
            glUniform3f(self.colorLocation, 0.5, 0.5, 0.5)
        glBindVertexArray(self.floor['vao'])
        glDrawArrays(GL_TRIANGLE_FAN, 0, self.floor['vertex_count'])

        # Renderizar el auto
        rotation_angle = pg.time.get_ticks() / 10000
        car_model = pyrr.matrix44.create_from_translation([0, 0.5, 0], dtype=np.float32)
        car_model = pyrr.matrix44.multiply(
            car_model,
            pyrr.matrix44.create_from_y_rotation(rotation_angle, dtype=np.float32)
        )
        car_model = pyrr.matrix44.multiply(
            car_model,
            pyrr.matrix44.create_from_scale([0.5, 0.5, 0.5], dtype=np.float32)
        )
        glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, car_model)

        for model in self.models:
            if shader == self.shader:  # Solo para el shader original
                glUniform3f(self.colorLocation, *model['color'])
            glBindVertexArray(model['vao'])
            
            # Cambiamos glDrawArrays por glDrawElements
            glDrawElements(GL_TRIANGLES, model['index_count'], GL_UNSIGNED_INT, None)

    def render_quad(self):
        if not hasattr(self, 'quadVAO'):
            self.quadVAO = glGenVertexArrays(1)
            quadVBO = glGenBuffers(1)
            glBindVertexArray(self.quadVAO)
            glBindBuffer(GL_ARRAY_BUFFER, quadVBO)
            glBufferData(GL_ARRAY_BUFFER, np.array([
                -1.0,  1.0,  0.0, 1.0,
                -1.0, -1.0,  0.0, 0.0,
                1.0, -1.0,  1.0, 0.0,
                -1.0,  1.0,  0.0, 1.0,
                1.0, -1.0,  1.0, 0.0,
                1.0,  1.0,  1.0, 1.0
            ], dtype=np.float32), GL_STATIC_DRAW)
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(0))
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 16, ctypes.c_void_p(8))
        glBindVertexArray(self.quadVAO)
        glDrawArrays(GL_TRIANGLES, 0, 6)
        glBindVertexArray(0)

    def quit(self):
        for model in self.models:
            glDeleteVertexArrays(1, (model['vao'],))
            glDeleteBuffers(1, (model['vbo'],))
        glDeleteVertexArrays(1, (self.floor['vao'],))
        glDeleteBuffers(1, (self.floor['vbo'],))
        glDeleteProgram(self.shader)
        glDeleteProgram(self.gBufferShader)
        glDeleteProgram(self.ssaoShader)
        glDeleteProgram(self.blurShaderH)
        glDeleteProgram(self.blurShaderV)
        glDeleteFramebuffers(1, (self.gBuffer,))
        glDeleteTextures(2, (self.gPosition, self.gNormal))
        glDeleteRenderbuffers(1, (self.rboDepth,))
        glDeleteFramebuffers(1, (self.ssaoFBO,))
        glDeleteTextures(1, (self.ssaoColorBuffer,))
        glDeleteFramebuffers(1, (self.blurFBO,))
        glDeleteTextures(1, (self.blurColorBuffer,))
        glDeleteTextures(1, (self.noiseTexture,))
        if hasattr(self, 'quadVAO'):
            glDeleteVertexArrays(1, (self.quadVAO,))
        pg.quit()


myApp = App()