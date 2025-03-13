import pyglet
from OpenGL import GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path
import click


@click.command("image_pixel", short_help="Visor de imágenes")
@click.argument("filename", type=str)
def image_pixel_viewer(filename):
    # cargamos una imagen
    pic = pyglet.image.load(filename)
    # para poder acceder a los datos de la imagen (los píxeles),
    # debemos hacer esto en pyglet:
    raw_image = pic.get_image_data()
    # y luego obtenemos los bytes de la imagen. nos interesa el formato RGB
    pixels = raw_image.get_bytes(fmt="RGB", pitch=pic.width * len("RGB"))

    # ya tenemos la imagen. ahora debemos crear una ventana
    # la hacemos un poco más ancha para poner un...
    win = pyglet.window.Window(pic.width + 40, pic.height)

    # ... gran píxel en el que mostraremos un color
    # por ahora es de color negro (esa tupla (0,0,0) que se observa)
    big_pixel = pyglet.shapes.Rectangle(
        pic.width + 10, pic.height - 30, 20, 20, (0, 0, 0)
    )
    
    @win.event
    def on_draw():
        win.clear()
        big_pixel.draw()
        # blit significa poner en la pantalla (en rigor, en un buffer)
        pic.blit(0, 0)

    @win.event
    def on_mouse_motion(x, y, dx, dy):
        if 0 <= x < pic.width and 0 <= y < pic.height:
            index = int(y * pic.width + x) * 3

            if index + 2 < len(pixels):
                r = int(pixels[index])
                g = int(pixels[index + 1])
                b = int(pixels[index + 2])

                big_pixel.color = (r, g, b)

    pyglet.app.run()
