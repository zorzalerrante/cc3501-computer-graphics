"""Clase Arcball para manipulación 3D de puntos de vista.
Basado en https://github.com/mmatl/pyrender/blob/master/pyrender/trackball.py, de Matthew Matl
"""

import numpy as np

import grafica.transformations as tr


class Arcball(object):
    """Una clase para crear transformaciones de cámara a partir de movimientos del ratón."""

    STATE_ROTATE = 0  # Estado para rotación
    STATE_PAN = 1     # Estado para traslación/paneo
    STATE_ROLL = 2    # Estado para roll (rotación sobre el eje Z)
    STATE_ZOOM = 3    # Estado para zoom

    def __init__(self, pose, size, scale, target=np.array([0.0, 0.0, 0.0])):
        """Inicializa un arcball con una pose inicial cámara-a-mundo
        y los parámetros dados.

        Parámetros
        ----------
        pose : [4,4]
            Una matriz de transformación inicial de cámara-a-mundo para el arcball.
            Es la matriz inversa de la "vista" (world-to-camera).

        size : (float, float)
            El ancho y alto de la imagen de la cámara en píxeles.

        scale : float
            La diagonal de la caja contenedora de la escena --
            usado para asegurar que los movimientos de traslación sean
            suficientemente rápidos para escenas de diferentes tamaños.

        target : (3,) float
            El centro de la escena en coordenadas del mundo.
            El arcball rotará alrededor de este punto.
        """
        self._size = np.array(size)
        self._scale = float(scale)

        self._pose = pose  # Matriz de pose anterior
        self._n_pose = pose  # Matriz de pose actual/nueva

        self._target = target  # Punto objetivo anterior
        self._n_target = target  # Punto objetivo actual/nuevo

        self._state = Arcball.STATE_ROTATE  # Estado inicial: rotación

    @property
    def pose(self):
        """Devuelve la pose actual de cámara-a-mundo."""
        return self._n_pose

    def set_state(self, state):
        """Establece el estado del arcball para cambiar el efecto
        de los movimientos de arrastre.

        Parámetros
        ----------
        state : int
            Uno de Arcball.STATE_ROTATE, Arcball.STATE_PAN,
            Arcball.STATE_ROLL, y Arcball.STATE_ZOOM.
        """
        self._state = state

    def resize(self, size):
        """Redimensiona la ventana.

        Parámetros
        ----------
        size : (float, float)
            El nuevo ancho y alto de la imagen de la cámara en píxeles.
        """
        self._size = np.array(size)

    def down(self, point):
        """Registra una pulsación inicial del ratón en un punto determinado.

        Parámetros
        ----------
        point : (2,) int
            Las coordenadas x e y en píxeles de la pulsación del ratón.
        """
        # Guardamos el punto donde ocurrió el clic
        self._pdown = np.array(point, dtype=np.float32)
        # Guardamos la pose actual como referencia para el movimiento
        self._pose = self._n_pose
        # Guardamos el objetivo actual como referencia
        self._target = self._n_target

    def drag(self, point):
        """Actualiza el arcball durante un arrastre.

        Parámetros
        ----------
        point : (2,) int
            Las coordenadas x e y actuales en píxeles del ratón durante un arrastre.
            Esto calculará un movimiento para el arcball con el movimiento relativo
            entre este punto y el marcado por down().
        """
        # Convertimos el punto a un array numpy
        point = np.array(point, dtype=np.float32)
        # Calculamos el desplazamiento desde el punto inicial
        dx, dy = point - self._pdown
        # Calculamos una dimensión de referencia para normalizar el movimiento
        mindim = 0.3 * np.min(self._size)

        # Extraemos información de la pose actual
        target = self._target  # Centro de rotación
        x_axis = self._pose[:3, 0].flatten()  # Vector del eje X de la cámara
        y_axis = self._pose[:3, 1].flatten()  # Vector del eje Y de la cámara
        z_axis = self._pose[:3, 2].flatten()  # Vector del eje Z de la cámara
        eye = self._pose[:3, 3].flatten()     # Posición de la cámara

        # Interpretamos el arrastre como una rotación
        if self._state == Arcball.STATE_ROTATE:
            # Calculamos ángulo de rotación en X basado en movimiento horizontal
            x_angle = -dx / mindim

            # Creamos matriz de rotación alrededor del eje Y (para movimiento horizontal)
            # Primero trasladamos al centro de rotación, rotamos, y trasladamos de vuelta
            x_rot_mat = (
                tr.translate(*target) @ tr.rotationY(x_angle) @ tr.translate(*-target)
            )
            
            # Calculamos ángulo de rotación en Y basado en movimiento vertical
            y_angle = dy / mindim

            # Creamos matriz de rotación alrededor del eje X (para movimiento vertical)
            y_rot_mat = (
                tr.translate(*target) @ tr.rotationX(y_angle) @ tr.translate(*-target)
            )

            # Aplicamos ambas rotaciones a la pose anterior
            self._n_pose = y_rot_mat @ x_rot_mat @ self._pose

        # Interpretamos el arrastre como un roll sobre el eje de la cámara
        elif self._state == Arcball.STATE_ROLL:
            # Calculamos el centro de la ventana
            center = self._size / 2.0
            # Vector desde el centro hasta el punto inicial
            v_init = self._pdown - center
            # Vector desde el centro hasta el punto actual
            v_curr = point - center
            
            # Normalizamos ambos vectores
            v_init = v_init / np.linalg.norm(v_init)
            v_curr = v_curr / np.linalg.norm(v_curr)

            # Calculamos el ángulo entre los dos vectores
            theta = -np.arctan2(v_curr[1], v_curr[0]) + np.arctan2(v_init[1], v_init[0])

            # Creamos matriz de rotación alrededor del eje Z
            rot_mat = (
                tr.translate(*target) @ tr.rotationZ(theta) @ tr.translate(*-target)
            )

            # Aplicamos la rotación a la pose anterior
            self._n_pose = rot_mat.dot(self._pose)

        # Interpretamos el arrastre como un paneo de cámara en el plano de vista
        elif self._state == Arcball.STATE_PAN:
            # Calculamos la magnitud del desplazamiento, ajustando por escala
            dx = -dx / (3.0 * mindim) * self._scale
            dy = -dy / (3.0 * mindim) * self._scale

            # Calculamos el vector de traslación en el espacio 3D
            # usando los ejes X e Y de la cámara como direcciones
            translation = dx * x_axis + dy * y_axis
            
            # Actualizamos el punto objetivo
            self._n_target = self._target + translation
            
            # Creamos una matriz de traslación
            t_tf = np.eye(4)  # Comenzamos con una matriz identidad
            t_tf[:3, 3] = translation  # Establecemos la parte de traslación
            
            # Aplicamos la traslación a la pose anterior
            self._n_pose = t_tf.dot(self._pose)

        # Interpretamos el arrastre como un movimiento de zoom
        elif self._state == Arcball.STATE_ZOOM:
            # Calculamos la distancia actual entre la cámara y el objetivo
            radius = np.linalg.norm(eye - target)
            ratio = 0.0
            
            # Calculamos el factor de zoom basado en el movimiento vertical
            if dy > 0:
                ratio = np.exp(abs(dy) / (0.5 * self._size[1])) - 1.0
            elif dy < 0:
                ratio = 1.0 - np.exp(dy / (0.5 * (self._size[1])))
                
            # Calculamos el vector de traslación para el zoom
            # Nos movemos a lo largo del eje Z de la cámara
            translation = -np.sign(dy) * ratio * radius * z_axis
            
            # Creamos una matriz de traslación
            t_tf = np.eye(4)
            t_tf[:3, 3] = translation
            
            # Aplicamos la traslación a la pose actual
            self._n_pose = t_tf.dot(self._pose)

        # Después de actualizar self._n_pose, estabilizamos la matriz
        # para prevenir la acumulación de errores numéricos
        self.stabilize_rotation()

    def scroll(self, clicks):
        """Zoom usando el movimiento de la rueda del ratón.

        Parámetros
        ----------
        clicks : int
            El número de clics. Números positivos indican movimiento de
            la rueda hacia adelante.
        """
        target = self._target
        # Factor de escala para cada clic de la rueda
        ratio = 0.90

        # Calculamos el multiplicador basado en la dirección de los clics
        mult = 1.0
        if clicks > 0:
            # Acercamiento: reducimos el radio
            mult = ratio**clicks
        elif clicks < 0:
            # Alejamiento: aumentamos el radio
            mult = (1.0 / ratio) ** abs(clicks)

        # Para la nueva pose
        z_axis = self._n_pose[:3, 2].flatten()  # Dirección de profundidad
        eye = self._n_pose[:3, 3].flatten()     # Posición de la cámara
        radius = np.linalg.norm(eye - target)   # Distancia al objetivo
        
        # Calculamos el vector de traslación para el zoom
        translation = (mult * radius - radius) * z_axis
        
        # Aplicamos la traslación a la nueva pose
        t_tf = np.eye(4)
        t_tf[:3, 3] = translation
        self._n_pose = t_tf.dot(self._n_pose)

        # Para la pose anterior
        z_axis = self._pose[:3, 2].flatten()
        eye = self._pose[:3, 3].flatten()
        radius = np.linalg.norm(eye - target)
        
        # Aplicamos la traslación a la pose anterior
        translation = (mult * radius - radius) * z_axis
        t_tf = np.eye(4)
        t_tf[:3, 3] = translation
        self._pose = t_tf.dot(self._pose)

    def rotate(self, azimuth, axis=None):
        """Rota el arcball alrededor del eje "Up" en azimuth radianes.

        Parámetros
        ----------
        azimuth : float
            El número de radianes a rotar.
        """
        target = self._target

        # Creamos matriz de rotación alrededor del eje Y (eje "Up" por defecto)
        # Primero trasladamos al centro, rotamos, y trasladamos de vuelta
        x_rot_mat = (
            tr.translate(*target) @ tr.rotationY(azimuth) @ tr.translate(*-target)
        )
        
        # Aplicamos la rotación a ambas poses
        self._n_pose = x_rot_mat @ self._n_pose        
        self._pose = x_rot_mat @ self._pose

    def stabilize_rotation(self):
        """Estabiliza la matriz de rotación para prevenir la deriva
        debido a acumulación de errores numéricos."""
        # Extraemos la parte de rotación de la matriz
        rotation = self._n_pose[:3, :3]
        
        # Extraemos los vectores de los ejes actuales
        x = rotation[:, 0]  # Vector X actual
        y = rotation[:, 1]  # Vector Y actual
        
        # Paso 1: Normalizamos el eje X para asegurar longitud unitaria
        x = x / np.linalg.norm(x)
        
        # Paso 2: Hacemos que Y sea ortogonal a X mediante proyección
        # Restamos la componente de Y que está en dirección X
        y = y - np.dot(y, x) * x
        # Normalizamos Y
        y = y / np.linalg.norm(y)
        
        # Paso 3: Calculamos Z como producto cruz de X y Y
        # Esto garantiza que Z es perpendicular a ambos X e Y
        z = np.cross(x, y)
        
        # Paso 4: Actualizamos la matriz con los ejes ortonormales
        self._n_pose[:3, 0] = x
        self._n_pose[:3, 1] = y
        self._n_pose[:3, 2] = z