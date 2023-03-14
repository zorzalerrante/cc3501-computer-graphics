import pyglet
from OpenGL.GL import *

import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models import Player
from controller import Controller

from models import GameState, ObstacleManager
from moving_shader import MovingShader2D

"""
The idea of this project is to something way more complex. Since this is an advanced lesson,
students should be able to understand it better.
The code related to rendering, input and view is in the class/file controller.py
The logic is located in the models.py file
"""


if __name__ == '__main__':
    # We add this import here only to make it more explicit
    # note that we are importing a variable instead of a class
    game_state = GameState()
    game_state.player = Player(
        x=-0.8, 
        speed=[0.3, 0.0], 
        game_state=game_state,
        vertical_jump_speed=0.6
    )
    game_state.obstacle_manager = ObstacleManager(game_state)
    game_state.obstacle_manager.generate_obstacles(100)

    # Create Window
    controller: Controller = Controller(width=1280, height=800, game_state=game_state)
    controller.current_pipeline = MovingShader2D()
    
    game_state.player.set_gpu_shape(controller.current_pipeline)
    game_state.set_gpu_shapes_of_obstacles(controller.current_pipeline)

    glClearColor(0.35, 0.35, 0.35, 0.2)
    # Enable Transparencies
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    pyglet.clock.schedule(game_state.update)
    pyglet.clock.schedule(game_state.player.update, controller)
    pyglet.clock.schedule(game_state.obstacle_manager.check_for_destroy)
    pyglet.clock.schedule(game_state.obstacle_manager.create_new_obstacles)

    pyglet.app.run()
