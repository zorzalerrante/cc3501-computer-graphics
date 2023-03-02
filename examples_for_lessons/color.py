import pyglet
from color_controller import Controller

if __name__ == "__main__":
    WHITE_COLOR = 1.0, 1.0, 1.0
    BLACK_COLOR = 0.0, 0.0, 0.0
    GRAY_COLOR = 0.5, 0.5, 0.5
    controller = Controller(rows=8, columns=8, background_color=BLACK_COLOR)

    controller.set_color_for_quad(i=0, j=0, r=1.0, g=0.0, b=0.0)  # red
    controller.set_color_for_quad(i=0, j=1, r=1.0, g=1.0, b=0.0)  # yellow 
    controller.set_color_for_quad(i=0, j=2, r=0.0, g=1.0, b=0.0)  # green
    controller.set_color_for_quad(i=0, j=3, r=0.0, g=0.0, b=1.0)  # blue

    controller.update_colors()
    
    pyglet.app.run()
    