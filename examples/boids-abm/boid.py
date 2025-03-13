import mesa
import numpy as np

# un Boid es uno de los elementos/agentes de la simulación.
# esta clase define su comportamiento.
class Boid(mesa.Agent):
    def __init__(
        self,
        model,
        pos,
        speed,
        velocity,
        vision,
        distance,
        cohere_factor=0.025,
        separation_factor=0.25,
        match_factor=0.04,
    ):
        super().__init__(model)
        self.pos = np.array(pos)
        self.speed = speed
        self.velocity = velocity
        self.vision = vision
        self.distance = distance
        self.cohere_factor = cohere_factor
        self.separation_factor = separation_factor
        self.match_factor = match_factor

    def cohere(self, neighbors):
        cohere = np.zeros(2)
        if neighbors:
            for neighbor in neighbors:
                #cohere += self.model.space.get_heading(self.pos, neighbor.pos)
                cohere += neighbor.pos
            cohere /= len(neighbors)
        return self.model.space.get_heading(self.pos, cohere)

    def separate(self, neighbors):
        me = self.pos
        them = (n.pos for n in neighbors)
        separation_vector = np.zeros(2)
        for other in them:
            if self.model.space.get_distance(me, other) < self.distance:
                separation_vector -= self.model.space.get_heading(me, other)
        return separation_vector

    def match_heading(self, neighbors):
        match_vector = np.zeros(2)
        if neighbors:
            for neighbor in neighbors:
                match_vector += neighbor.velocity
            match_vector /= len(neighbors)
        return match_vector

    def step(self):
        neighbors = self.model.query_area(self.pos, self.vision)
        neighbors = list(filter(lambda x: x != self, neighbors))

        self.velocity += (
            self.cohere(neighbors) * self.cohere_factor
            + self.separate(neighbors) * self.separation_factor
            + self.match_heading(neighbors) * self.match_factor
        )
        self.velocity /= np.linalg.norm(self.velocity)
        new_pos = self.pos + self.velocity * self.speed
        self.model.space.move_agent(self, new_pos)

