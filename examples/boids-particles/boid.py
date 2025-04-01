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
        border_factor=0.5
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
        self.border_factor = border_factor

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
            + self.avoid_borders() * self.border_factor
        )
        # Normalización segura de la velocidad
        velocity_norm = np.linalg.norm(self.velocity)
            
        if velocity_norm <= 0.00001:
            # Si la velocidad es cero, asignamos una dirección aleatoria
            self.velocity = np.random.random(2) * 2 - 1
            velocity_norm = np.linalg.norm(self.velocity)
            
        self.velocity /= velocity_norm
        self.current_speed = velocity_norm
        
        new_pos = self.pos + self.velocity * self.current_speed

        new_pos[0] = np.clip(new_pos[0], 0, self.model.space.x_max)
        new_pos[1] = np.clip(new_pos[1], 0, self.model.space.y_max)

        self.model.space.move_agent(self, new_pos)

    def avoid_borders(self, margin=30.0, turn_factor=0.2):
        """
        Aplica una fuerza que aleja a los boids de los bordes del espacio
        cuando se aproximan a ellos dentro de cierto margen.
        
        Parameters:
        -----------
        margin : float
            Distancia desde el borde a la que comienza a aplicarse la fuerza
        turn_factor : float
            Intensidad de la fuerza de alejamiento del borde
        """
        v = np.zeros(2)
        
        # Obtenemos las dimensiones del espacio
        width = self.model.space.x_max
        height = self.model.space.y_max
        
        # Revisamos proximidad al borde izquierdo
        if self.pos[0] < margin:
            v[0] += turn_factor
        # Revisamos proximidad al borde derecho
        elif self.pos[0] > width - margin:
            v[0] -= turn_factor
        
        # Revisamos proximidad al borde inferior
        if self.pos[1] < margin:
            v[1] += turn_factor
        # Revisamos proximidad al borde superior
        elif self.pos[1] > height - margin:
            v[1] -= turn_factor
        
        return v

