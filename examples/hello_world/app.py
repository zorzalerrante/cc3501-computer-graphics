import pyglet
from OpenGL import GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path

if __name__ == "__main__":
    # esta es una ventana de pyglet. 
    # le damos la resolución como parámetro
    win = pyglet.window.Window(800, 600)

    # Inicialización
    # dibujaremos un cuadrilátero. tiene cuatro vértices
    # cada vértice tiene su propio color
    vertices = np.array(
        [-1, -1, 0.0,  # inf izq
          1, -1, 0.0,  # if der
          1,  1, 0.0,  # sup der
         -1,  1, 0.0,  # sup izq
        ],
        dtype=np.float32,
    )

    vertex_colors = np.array(
        [1.0, 204 / 255.0, 1.0,  # inf izq
         1.0, 204 / 255.0, 1.0,  # if der
         204 / 255.0, 1.0, 1.0,  # sup der
         204 / 255.0, 1.0, 1.0,  # sup izq
        ],
        dtype=np.float32,
    )

    # en OpenGL se dibujan triángulos.
    # por tanto, nuestro cuadrilátero tiene dos triángulos.
    # los índices nos dicen cuáles vértices conforman cada triángulo.
    # primero los vértices 0, 1 y 2; 
    # luego los vértices 2, 3 y 0.
    # noten que, al igual que los vértices, aquí todos los índices
    # van en un único arreglo
    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)

    # cargamos nuestros shaders
    # son shaders básicos.
    # el shader de vértices solo lee la posición y el color de cada vértice
    with open(Path(os.path.dirname(__file__)) / "vertex_program.glsl") as f:
        vertex_source_code = f.read()

    # y el shader de píxeles solo lee el color correspondiente al píxel
    with open(Path(os.path.dirname(__file__)) / "fragment_program.glsl") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # ahora le entregaremos los datos de nuestro objeto a la GPU
    # para así graficarlo con el pipeline que hemos creado.
    # primero, inicializamos los datos en la GPU.
    # le decimos que tendremos 4 vértices
    gpu_data = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, indices)

    # ahora le entregamos los valores de nuestro modelo 3D al pipeline
    # las llaves que utilizamos son los nombres de cada parámetro
    # en nuestro pipeline (ver fuente del vertex program)
    gpu_data.position[:] = vertices
    gpu_data.color[:] = vertex_colors

    # adicionalmente, createmos un mensaje para desplegar
    label = pyglet.text.Label('¡Hola, CC3501!',
                font_name='Times New Roman',
                font_size=36,
                color=(0,0,0,255),
                x=win.width//2, y=win.height//2,
                anchor_x='center', anchor_y='center')

    # con esto ya hemos inicializado nuestro programa:
    # - definimos un modelo 3D
    # - creamos un pipeline para dibujarlo
    # - le pasamos todo a la GPU
    # ahora corresponde graficarlo!

    # GAME LOOP
    # ¿qué es esto de @win.event?
    # es lo que se llama un **decorador**
    # la ventana win ejecuta el _game loop_ y allí ejecuta múltiples funciones
    # con un decorador le estamos diciendo que en la parte que grafica
    # ejecute la función que tenemos definida aquí.
    @win.event
    def on_draw():
        # esta función define el color con el que queda una ventana vacía
        # noten que esto es algo de OpenGL, no de pyglet
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)

        # esto vacía la ventana
        win.clear()

        # ahora que la ventana está limpia, comenzamos a dibujar
        # debemos activar el pipeline
        # esto es necesario, de hecho, es bueno: significa que podemos
        # usar múltiples pipelines en una aplicación.
        pipeline.use()
        # le decimos a la GPU que dibuje los datos que subimos
        # de manera implícita usará el pipeline que esté activo
        gpu_data.draw(GL.GL_TRIANGLES)

        # desplegamos el texto.
        # pyglet utiliza su propio pipeline para desplegarlo.
        label.draw()


    # aquí comienza pyglet a ejecutar su loop.
    pyglet.app.run()

    # cuando ejecutemos el programa veremos que la ventana está recubierta
    # con un cuadrilátero que tiene un degradado aesthetic.
