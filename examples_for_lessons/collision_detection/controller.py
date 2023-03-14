import pyglet
from OpenGL.GL import *

import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# We will need double linked lists because we are going to remove elements at the beginning
# But also add many at the end

import grafica.transformations as tr

from models import ObstacleManager, GameState
from moving_shader import MovingShader2D


class Controller(pyglet.window.Window):
    """Class that handles input events such as key and mouse press.
    Also renders and applies transforms. It contains the Pyglet window.
    """

    def __init__(self, width, height, game_state):
        super().__init__(width, height)
        self.width, self.height = width, height
        self.jump_action_queued = False
        self.game_state: 'GameState' = game_state
        self.current_pipeline: MovingShader2D = None

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.jump_action_queued = True
        if symbol == pyglet.window.key.ENTER:
            self.game_state.paused = not self.game_state.paused 
        elif symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_mouse_press(self, x, y, buttons, modifiers):
        # For debugging purposes
        opengl_x = (x/self.width -0.5) * 2
        opengl_y = (y/self.height - 0.5) * 2
        real_x = opengl_x + self.game_state.camera_position
        print(f"Position of click {real_x}, {opengl_y}")

    def apply_transform(self, pipeline, transform_matrix, shader_param_name="transform"):
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, shader_param_name), 1, GL_TRUE, transform_matrix)

    def render_obstacle(self, pipeline, obstacle):
        GPUShape = obstacle.gpu_obstacle
        translation = tr.translate(obstacle.x, obstacle.y, 0.0)
        self.apply_transform(pipeline, translation)
        pipeline.drawCall(GPUShape)

    def render_player(self, pipeline, player):
        # TODO: Add animation or keyframe
        GPUShape = player.gpu_player
        translation = tr.translate(player.x, player.y, 0.0)
        self.apply_transform(pipeline, translation)
        pipeline.drawCall(GPUShape)

    def apply_player_position_transform(self):
        player = self.game_state.player
        player_inverse_translation = tr.translate(-player.x, 0., 0.)
        self.apply_transform(
            self.current_pipeline, player_inverse_translation, shader_param_name="playerPosition"
        )

    def on_draw(self):
        self.clear()
        glUseProgram(self.current_pipeline.shaderProgram)

        self.apply_player_position_transform()
        for obstacle in ObstacleManager.obstacles:
            self.render_obstacle(self.current_pipeline, obstacle)

        self.render_player(self.current_pipeline, self.game_state.player)
