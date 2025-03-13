# mesa es la biblioteca de simulación basada en agentes que utilizaremos
import mesa
import numpy as np

from .boid import Boid
from scipy import spatial
import time

# la clase World contiene el mundo simulado.
class World(mesa.Model):

    def __init__(
        self,
        population=100,
        width=100,
        height=100,
        speed=1,
        vision=10,
        distance=2,
        cohere_factor=0.025,
        separation_factor=0.25,
        match_factor=0.04,
    ):
        super().__init__(seed=666)
        self.population = population
        self.vision = vision
        self.speed = speed
        self.distance = distance
        #self.schedule = mesa.time.RandomActivation(self)
        self.space = mesa.space.ContinuousSpace(width, height, True)
        self.factors = dict(cohere_factor=cohere_factor, separation_factor=separation_factor, match_factor=match_factor)
        self.make_agents()
        self.running = True

    def make_agents(self):
        self.id_to_agent = {}
        for i in range(self.population):
            x = self.random.random() * self.space.x_max
            y = self.random.random() * self.space.y_max
            pos = np.array((x, y))
            velocity = np.random.random(2) * 2 - 1
            boid = Boid(
                self,
                pos,
                self.speed,
                velocity,
                self.vision,
                self.distance,
                **self.factors
            )
            self.space.place_agent(boid, pos)
            self.id_to_agent[i] = boid

    def step(self):
        self.tree = spatial.KDTree([boid.pos for boid in self.id_to_agent.values()])
        #print(self.tree)
        #self.schedule.step()
        self.agents.shuffle_do('step')

    def iter_agents(self):
        yield from self.space._agent_to_index.keys()

    def query_area(self, pos, radius):
        result_ids = self.tree.query_ball_point(pos, radius)
        return [self.id_to_agent[idx] for idx in result_ids]