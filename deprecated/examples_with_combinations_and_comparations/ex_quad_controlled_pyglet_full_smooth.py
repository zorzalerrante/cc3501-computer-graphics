import pyglet

"""
In this example, we are using only pyglet and no low-level OpenGL calls.
By detecting on key press and release and updating position during the update_quad method,
We are achieving a smooth movement. There are other alternatives, shown in the same folder
"""

class Controller(pyglet.window.Window):

    def __init__(self):
        super().__init__()
        self.fillPolygon = True
        self.theta = 0.0
        self.rotate = True
        self.batch = pyglet.graphics.Batch()
        self.square = pyglet.shapes.BorderedRectangle(360, 240, 100, 100, border=5, color=(55, 55, 255),
                                                    border_color=(25, 25, 25), batch=self.batch)
        self.moving_direction = [0., 0.]

    def update_quad(self, dt):
        if self.rotate:
            self.theta += 300.0 * dt
            self.square.rotation = self.theta

        self.square.x += 300.0 * dt * self.moving_direction[0]
        self.square.y += 300.0 * dt * self.moving_direction[1]

window = Controller()
counter = pyglet.window.FPSDisplay(window=window)


@window.event
def on_key_press(symbol, modifiers):
    if symbol == pyglet.window.key.SPACE:
        window.rotate = not window.rotate
    elif symbol == pyglet.window.key.LEFT:
        window.moving_direction[0] = -1.0
    elif symbol == pyglet.window.key.RIGHT:
        window.moving_direction[0] = +1.0
    elif symbol == pyglet.window.key.UP:
        window.moving_direction[1] = +1.0
    elif symbol == pyglet.window.key.DOWN:
        window.moving_direction[1] = -1.0
    elif symbol == pyglet.window.key.ESCAPE:
        window.close()


# Reverse state. Stop motion.
@window.event
def on_key_release(symbol, modifiers):
    if symbol == pyglet.window.key.LEFT:
        window.moving_direction[0] += -1.0
    elif symbol == pyglet.window.key.RIGHT:
        window.moving_direction[0] += -1.0
    elif symbol == pyglet.window.key.UP:
        window.moving_direction[1] += -1.0
    elif symbol == pyglet.window.key.DOWN:
        window.moving_direction[1] += +1.0
    elif symbol == pyglet.window.key.ESCAPE:
        window.close()


@window.event
def on_draw():
    window.clear()
    window.batch.draw()
    counter.draw()

pyglet.clock.schedule(window.update_quad)
pyglet.app.run()
