# coding=utf-8
"""Drawing 4 shapes with different transformations"""

import pyglet
from math import sin, cos
from pyglet_basic_shapes_wrapper import CustomShape2D


class Controller(pyglet.window.Window):

    def __init__(self, width, height, title="Pyglet window"):
        super().__init__(width, height, title)
        self.total_time = 0.0
        self.fillPolygon = True


# We will use the global controller as communication with the callback function
WIDTH, HEIGHT = 1280, 800
controller = Controller(width=WIDTH, height=HEIGHT)

# Setting up the clear screen color
pyglet.gl.glClearColor(0.15, 0.15, 0.15, 1.0)

# Setting the model (data of our code)
# Each figure will occupy a portion 1/4 of the screen
# Setting the coordinates and color for each vertex
rainbow_triangle_vertices = [
   # x   y    r    g    b
    0,   0,  1.0, 0.0, 0.0,
   WIDTH * 0.25,  HEIGHT * 0.25,  0.0, 1.0, 0.0, 
   WIDTH * 0.25, 0, 0.0, 0.0, 1.0,
]
triangle_vertices = [0, 1, 2]

# Creating shapes on GPU memory
rainbow_quad_vertices = [
   # x   y    r    g    b
    0,   0,  1.0, 0.0, 0.0,
   WIDTH * 0.25,  HEIGHT * 0.25,  0.0, 1.0, 0.0, 
   WIDTH * 0.25, 0, 0.0, 0.0, 1.0,
    0,  HEIGHT * 0.25, 1.0, 1.0, 1.0,
]
quad_vertices = [
    0, 1, 2,
    0, 1, 3,
]

batch = pyglet.graphics.Batch()

# Position each shape in a different quarter of the screen
shape_triangle1 = CustomShape2D(
    vertices=rainbow_triangle_vertices,
    indices=triangle_vertices,
    batch=batch,
)
shape_triangle1.position = (WIDTH * 0.5, 100.0)

shape_triangle2 = CustomShape2D(
    vertices=rainbow_triangle_vertices,
    indices=triangle_vertices,
    batch=batch,
)
shape_triangle2.position = (100.0, 100.0)

shape_quad1 = CustomShape2D(
    vertices=rainbow_quad_vertices,
    indices=quad_vertices,
    batch=batch,
)
shape_quad1.position = (WIDTH * 0.5, HEIGHT * 0.5)

shape_quad2 = CustomShape2D(
    vertices=rainbow_quad_vertices,
    indices=quad_vertices,
    batch=batch,
)
shape_quad2.position = (100.0, HEIGHT * 0.5)

# What happens when the user presses these keys
@controller.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        controller.fillPolygon = not controller.fillPolygon
    elif symbol == pyglet.window.key.ESCAPE:
        controller.close()


@controller.event
def on_draw():
    controller.clear()
    batch.draw()


# This function will be executed approximately 60 times per second
# dt is the time between the last time it was executed and now
def update_figures(dt: float, controller: Controller):
    controller.total_time += dt
    shape_quad1.rotation = 20.0 * controller.total_time
    shape_triangle2.position = 100.0 + 100.0 * cos(controller.total_time), 100.0 + 100.0 * sin(controller.total_time)
    shape_quad2.scale = 1.0 + 0.5 * sin(controller.total_time)

pyglet.clock.schedule(update_figures, controller)
# Set the view
pyglet.app.run()
