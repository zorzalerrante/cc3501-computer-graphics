import pyglet
from OpenGL.GL import *

import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import grafica.easy_shaders as es

from models import GameState, Player
from controller import Controller


"""
The idea of this project is to something way more complex. Since this is an advanced lesson,
students should be able to understand it better
"""



if __name__ == '__main__':
    game_state: GameState = GameState()
    player: Player = Player(x=0.0, y=0.0)
    game_state.player = player

    # Create Window
    controller: Controller = Controller(width=1280, height=800, game_state=game_state)
    controller.current_pipeline = es.SimpleTextureTransformShaderProgram()
    
    player.set_gpu_shape(controller.current_pipeline)
    
    pyglet.clock.schedule(game_state.update)
    pyglet.clock.schedule(player.update, controller)
    pyglet.app.run()
