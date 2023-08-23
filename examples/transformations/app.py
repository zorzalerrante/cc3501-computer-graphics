import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path

# Nota:
# Queremos usar el código que está en el módulo grafica
# ubicado en la raíz del repositorio. 
# como ejecutamos el código desde esa raíz, tenemos que agregar
# el módulo a las rutas de búsqueda de módulos del intérprete de Python
# lo ideal sería instalar el módulo gráfica como una biblioteca
# pero no es una biblioteca aún :)
import sys
if sys.path[0] != '':
    sys.path.insert(0, '')

# ahora sí podemos importar funcionalidad desde grafica
import grafica.transformations as tr


if __name__ == "__main__":
    try:
        config = pyglet.gl.Config(sample_buffers=1, samples=4)
        window = pyglet.window.Window(960, 960, config=config)
    except pyglet.window.NoSuchConfigException:
        window = pyglet.window.Window(960, 960)

    bunny = tm.load("assets/Stanford_Bunny.stl")

    # esta es la "model" transform
    # convierte el sistema de coordenadas del conejito en el nuestro
    # para nuestro caso basta que la apliquemos una vez al comienzo
    # porque trimesh puede aplicar una matriz al modelo 3D
    # en otras situaciones las matrices subyacentes se aplicarían en un
    # vertex program
    bunny_scale = tr.uniformScale(2.0 / bunny.scale)
    bunny_translate = tr.translate(*-bunny.centroid)
    bunny_rotate = tr.rotationX(-np.pi / 2)
    
    # multiplicamos las matrices con el operador @
    # y aplicamos la matriz resultante
    # OJO: ¡noten el orden de las multiplicaciones!
    bunny.apply_transform(bunny_rotate @ bunny_scale @ bunny_translate)

    # queremos hacer un conejito que gire y gire sin pasar
    # usaremos este diccionario para almacenar el estado del conejito
    window.bunny_state = {
        'angle': 0.0,
        'total_time': 0.0,
        'transform': tr.identity()
    }

    # esta parte es igual al ejemplo hello_opengl.
    # sin embargo, el vertex program es ligeramente diferente
    # porque ahora tiene como parámetro una transformación
    with open(Path(os.path.dirname(__file__)) / "vertex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "fragment_program.glsl") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # dibujaremos cuatro conejos, pero basta que lo copiemos una única vez a la GPU
    bunny_vertex_list = tm.rendering.mesh_to_vertexlist(bunny)
    bunny_gpu = pipeline.vertex_list_indexed(
        len(bunny_vertex_list[4][1]) // 3,
        GL.GL_TRIANGLES,
        bunny_vertex_list[3]
    )
    bunny_gpu.position[:] = bunny_vertex_list[4][1]

    # hemos visto que esta función dibuja el mundo dentro del GAME LOOP
    # pero, de cierto modo, es una función estática, no tiene noción del tiempo
    @window.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glLineWidth(1.0)

        window.clear()

        pipeline.use()
        # aquí le entregamos al pipeline la matriz correspondiente al parámetro view_transform
        # OpenGL espera una matriz de 4x4 expresada como un vector de 16 elementos
        # por eso ejecutamos reshape(16, 1, order='F') 
        # el parámetro order se refiere a si se realiza por filas o por columnas
        # Nota: F no es por filas, es por Columnas. la F viene de Fortran ;)
        pipeline["view_transform"] = window.bunny_state['transform'].reshape(16, 1, order="F")

        # la función de dibujo es esencialmente la misma.
        # lo que ha cambiado es el parámetro que recibe el vertex program
        bunny_gpu.draw(pyglet.gl.GL_TRIANGLES)

    # entonces, ¿cómo actualizar el mundo?
    # lo actualizaremos a 60 cuadros por segundo
    # primero definimos la función que utilizaremos
    def update_world(dt, window):
        # el parámetro dt es delta time
        # cuánto tiempo (en segundos) ha pasado desde la última ejecución
        window.bunny_state['total_time'] += dt
        window.bunny_state['angle'] = window.bunny_state['total_time']
        window.bunny_state['transform'] = tr.rotationY(window.bunny_state['total_time'])

    # aquí le pedimos a pyglet que ejecute nuestra función
    # noten que la ejecución de la actualización del mundo y de su graficación
    # se ejecutan por separado
    pyglet.clock.schedule_interval(update_world, 1 / 60.0, window)

    # let's go justin
    pyglet.app.run(1 / 60.0)
