import pyglet
from OpenGL.GL import *

import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# We will need double linked lists because we are going to remove elements at the beginning
# But also add many at the end

import grafica.easy_shaders as es
import grafica.transformations as tr

from models import ObstacleManager

class Controller(pyglet.window.Window):

    def __init__(self, width, height, game_state):
        super().__init__(width, height)
        self.jump_action_queued = False
        self.game_state = game_state
        self.current_pipeline: es.SimpleTextureTransformShaderProgram = None

    def apply_transform(self, pipeline, transform_matrix, shader_param_name="transform"):
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, shader_param_name), 1, GL_TRUE, transform_matrix)

    def render_obstacle(self, pipeline, obstacle):
        GPUShape = obstacle.GPUShape
        translation = tr.translate(obstacle.x, obstacle.y, 0.0)
        self.apply_transform(pipeline, translation)
        pipeline.drawCall(GPUShape)

    def render_player(self, pipeline, player):
        # TODO: Add animation or keyframe
        GPUShape = player.gpu_player
        translation = tr.translate(player.x, player.y, 0.0)
        self.apply_transform(pipeline, translation)
        pipeline.drawCall(GPUShape)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.SPACE:
            self.jump_action_queued = True

        elif symbol == pyglet.window.key.ESCAPE:
            self.close()

    def on_draw(self):
        self.clear()
        glUseProgram(self.current_pipeline.shaderProgram)

        for obstacle in ObstacleManager.obstacles:
            self.render_obstacle(self.current_pipeline, obstacle)

        self.render_player(self.current_pipeline, self.game_state.player)
