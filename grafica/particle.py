import numpy as np

# Clase Particle genérica que solo maneja las propiedades físicas básicas
class Particle(object):
    def __init__(self, position, velocity=None, acceleration=None, mass=1.0, ttl=1.0):
        """
        Inicializa una partícula con sus propiedades físicas básicas.
        
        Args:
            position (array-like): Posición inicial [x, y]
            velocity (array-like, optional): Velocidad inicial [vx, vy]
            acceleration (array-like, optional): Aceleración inicial [ax, ay]
            mass (float, optional): Masa de la partícula
            ttl (float, optional): Tiempo de vida inicial ("time to live")
        """
        self.position = np.array(position, dtype=np.float32)
        self.velocity = np.array(velocity if velocity is not None else [0, 0], dtype=np.float32)
        self.acceleration = np.array(acceleration if acceleration is not None else [0, 0], dtype=np.float32)
        self.mass = mass
        self.ttl = ttl
        # Propiedades adicionales que pueden ser útiles
        self.age = 0.0  # Edad de la partícula
        self.alive = True  # Estado de la partícula

    def apply_force(self, force):
        """Aplica una fuerza a la partícula, afectando su aceleración."""
        self.acceleration += force / self.mass

    def reset_acceleration(self):
        """Reinicia la aceleración de la partícula a cero."""
        self.acceleration[:] = 0

    def update(self, dt, force_func=None):
        """
        Actualiza el estado de la partícula.
        
        Args:
            dt (float): Delta de tiempo
            force_func (callable, optional): Función que aplica fuerzas a la partícula
        """
        # Actualizar tiempo de vida y edad
        self.ttl -= dt
        self.age += dt
        
        # Verificar si sigue viva
        if self.ttl <= 0:
            self.alive = False
            return
        
        # Aplicar fuerzas externas si se proporciona una función
        if force_func:
            self.reset_acceleration()
            force_func(self)
        
        # Método de integración: Velocity Verlet
        # 1. Actualizar posición con velocidad actual y media aceleración
        self.position += dt * self.velocity + 0.5 * dt * dt * self.acceleration
        
        # 2. Guardar aceleración actual
        old_acceleration = self.acceleration.copy()
        
        # 3. Calcular nueva aceleración (solo si hay una función de fuerzas)
        if force_func:
            self.reset_acceleration()
            force_func(self)
        
        # 4. Actualizar velocidad con aceleración promedio
        self.velocity += 0.5 * dt * (old_acceleration + self.acceleration)

