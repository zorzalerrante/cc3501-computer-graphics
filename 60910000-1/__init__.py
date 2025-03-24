import pyglet
from OpenGL import GL
import click

@click.command("tarea", short_help='¡Hola, mundo!')
@click.option("--width", type=int, default=800)
@click.option("--height", type=int, default=600)
def tarea(width, height):
    win = pyglet.window.Window(width, height)


    label = pyglet.text.Label('¡Hola, CC3501!',
                font_name='Times New Roman',
                font_size=36,
                color=(0,0,0,255),
                x=win.width//2, y=win.height//2,
                anchor_x='center', anchor_y='center')

    
    @win.event
    def on_draw():
        GL.glClearColor(0.5, 0.5, 0.5, 1.0)
        win.clear()
        label.draw()

    pyglet.app.run()
