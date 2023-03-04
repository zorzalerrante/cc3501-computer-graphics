import pyglet
from color_controller import Controller

# You do not need to understand what controller does in this first class.
if __name__ == "__main__":
    NUMBER_OF_ROWS = 8
    NUMBER_OF_COLS = 8
    controller = Controller(rows=NUMBER_OF_ROWS, columns=NUMBER_OF_COLS)

    # These are colors in the RGB format
    WHITE_COLOR = 1.0, 1.0, 1.0
    BLACK_COLOR = 0.0, 0.0, 0.0
    RED_COLOR = 1.0, 0.0, 0.0
    GRAY_COLOR = 0.5, 0.5, 0.5
    BLUE_COLOR = 0.0, 0.0, 1.0

    # Setting colors
    controller[0:3, 0:4] = BLUE_COLOR
    controller[3:, 0:4] = WHITE_COLOR
    controller[:, 4:] = RED_COLOR

    controller.update_colors()
    
    pyglet.app.run()
    