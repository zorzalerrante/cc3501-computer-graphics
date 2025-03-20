import pyglet
from OpenGL import GL
import numpy as np
import os
from pathlib import Path
import click
import time
from grafica.utils import load_pipeline

@click.command("chroma_key", short_help="Efecto de green screen en una imagen")
@click.argument("filename", type=str)
@click.option("--color", default="0,255,0", help="Color a reemplazar en formato R,G,B (0-255)")
@click.option("--threshold", default=0.1, help="Umbral de tolerancia (0.0-1.0)")
def chroma_key(filename, color, threshold):
    # Convertir el color de string a array de floats normalizados
    chroma_color = np.array([float(c) for c in color.split(",")]) / 255.0
    
    # Cargar la imagen
    pic = pyglet.image.load(filename)
    win = pyglet.window.Window(pic.width, pic.height)
    texture = pic.get_texture()
    
    # Definir geometría (un cuadrado simple que cubre toda la pantalla)
    vertices = np.array([-1, -1, 1, -1, 1, 1, -1, 1], dtype=np.float32)
    uv = np.array([0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0], dtype=np.float32)
    indices = np.array([0, 1, 2, 2, 3, 0], dtype=np.uint32)
    
    # Cargar nuestro pipeline para el efecto chroma key
    pipeline = load_pipeline(
        Path(os.path.dirname(__file__)) / "vertex_chroma.glsl",
        Path(os.path.dirname(__file__)) / "fragment_chroma.glsl",
    )
    
    # Enviar datos a la GPU
    gpu_data = pipeline.vertex_list_indexed(4, GL.GL_TRIANGLES, indices)
    gpu_data.position[:] = vertices
    gpu_data.uv[:] = uv
    
    # Variable para rastrear el tiempo
    start_time = time.time()
    
    @win.event
    def on_draw():
        win.clear()
        
        # Calcular tiempo transcurrido para animación del fondo
        elapsed = time.time() - start_time
        
        # Usar nuestro pipeline
        pipeline.use()
        
        # Enviar uniforms al shader
        pipeline['chroma_color'] = chroma_color
        pipeline['threshold'] = threshold
        pipeline['time'] = elapsed
        
        # Vincular textura y dibujar
        GL.glBindTexture(texture.target, texture.id)
        gpu_data.draw(GL.GL_TRIANGLES)
    
    pyglet.app.run()

if __name__ == "__main__":
    chroma_key()