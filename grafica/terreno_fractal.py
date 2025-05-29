import numpy as np
import pyglet.gl as GL
from itertools import chain


def diamond_square_algorithm(size, roughness=0.5, height_range=1.0, seed=None):
    """
    Genera un mapa de alturas usando el algoritmo diamond-square.
    
    Parámetros:
    size -- Tamaño de la grilla (debe ser 2^n + 1)
    roughness -- Factor de rugosidad (0-1), controla qué tan abrupto es el terreno
    height_range -- Rango inicial de alturas
    seed -- Semilla para reproducibilidad
    """
    if seed is not None:
        np.random.seed(seed)
    
    # Verificar que size sea 2^n + 1
    n = np.log2(size - 1)
    if not n.is_integer():
        raise ValueError("El tamaño debe ser 2^n + 1")
    
    # Inicializar el mapa de alturas
    heights = np.zeros((size, size))
    
    # Inicializar las esquinas con valores aleatorios
    heights[0, 0] = np.random.uniform(-height_range, height_range)
    heights[0, size-1] = np.random.uniform(-height_range, height_range)
    heights[size-1, 0] = np.random.uniform(-height_range, height_range)
    heights[size-1, size-1] = np.random.uniform(-height_range, height_range)
    
    step_size = size - 1
    scale = height_range
    
    while step_size > 1:
        half_step = step_size // 2
        
        # Paso diamond
        for y in range(half_step, size - half_step, step_size):
            for x in range(half_step, size - half_step, step_size):
                # Promedio de las cuatro esquinas
                avg = (heights[y - half_step, x - half_step] +
                       heights[y - half_step, x + half_step] +
                       heights[y + half_step, x - half_step] +
                       heights[y + half_step, x + half_step]) / 4.0
                
                # Agregar desplazamiento aleatorio
                heights[y, x] = avg + np.random.uniform(-scale, scale)
        
        # Paso square
        for y in range(0, size, half_step):
            for x in range((y + half_step) % step_size, size, step_size):
                # Calcular el promedio de los vecinos diamond
                count = 0
                total = 0
                
                # Vecino superior
                if y - half_step >= 0:
                    total += heights[y - half_step, x]
                    count += 1
                
                # Vecino inferior
                if y + half_step < size:
                    total += heights[y + half_step, x]
                    count += 1
                
                # Vecino izquierdo
                if x - half_step >= 0:
                    total += heights[y, x - half_step]
                    count += 1
                
                # Vecino derecho
                if x + half_step < size:
                    total += heights[y, x + half_step]
                    count += 1
                
                avg = total / count
                heights[y, x] = avg + np.random.uniform(-scale, scale)
        
        # Reducir el paso y la escala
        step_size //= 2
        scale *= roughness
    
    return heights


def fractal_terrain(resolution=65, roughness=0.5, height_scale=0.3, seed=None, id=None, parent=None):
    """
    Genera un terreno fractal usando el algoritmo diamond-square.
    
    Parámetros:
    resolution -- Resolución de la grilla (debe ser 2^n + 1, ej: 17, 33, 65, 129)
    roughness -- Factor de rugosidad (0-1)
    height_scale -- Escala de las alturas
    seed -- Semilla para reproducibilidad
    """
    # Generar mapa de alturas
    heights = diamond_square_algorithm(resolution, roughness, height_scale, seed)
    
    # Crear malla de vértices
    xv, yv = np.meshgrid(
        np.linspace(0, 1, resolution),
        np.linspace(0, 1, resolution),
        indexing="xy"
    )
    
    # Combinar posiciones X, Y y alturas Z
    vertices = np.vstack((
        xv.reshape(1, -1),
        yv.reshape(1, -1),
        heights.reshape(1, -1)
    )).T
    
    # Generar índices para triángulos
    indices = []
    for row in range(resolution - 1):
        for col in range(resolution - 1):
            # Primer triángulo del cuadrado
            i0 = row * resolution + col
            i1 = i0 + 1
            i2 = i0 + resolution
            indices.extend([i0, i1, i2])
            
            # Segundo triángulo del cuadrado
            i3 = i1 + resolution
            indices.extend([i1, i3, i2])
    
    # Calcular normales
    normals = calculate_normals(vertices, indices, resolution)
    
    # Generar colores basados en la altura
    colors = generate_terrain_colors(heights.flatten(), resolution)
    
    return {
        'mesh': {
            'n_vertices': resolution**2,
            'texture': None,
            'textures': {}
        },
        'attributes': {
            'position': vertices.reshape(-1, 1, order="C"),
            'normal': normals.reshape(-1, 1, order="C"),
            'color': colors.reshape(-1, 1, order="C")
        },
        'indices': indices,
        'GL_TYPE': GL.GL_TRIANGLES,
        'transform': np.identity(4, dtype=np.float32),
        'id': id,
        'children': [],
        'parent': parent,
        'object': None,
    }


def calculate_normals(vertices, indices, resolution):
    """
    Calcula las normales para cada vértice del terreno.
    """
    normals = np.zeros_like(vertices)
    
    # Calcular normales por triángulo y acumular en vértices
    for i in range(0, len(indices), 3):
        i0, i1, i2 = indices[i], indices[i+1], indices[i+2]
        
        v0 = vertices[i0]
        v1 = vertices[i1]
        v2 = vertices[i2]
        
        # Calcular vectores de los lados
        edge1 = v1 - v0
        edge2 = v2 - v0
        
        # Producto cruz para obtener la normal
        face_normal = np.cross(edge1, edge2)
        
        # Acumular en cada vértice
        normals[i0] += face_normal
        normals[i1] += face_normal
        normals[i2] += face_normal
    
    # Normalizar todas las normales
    for i in range(len(normals)):
        length = np.linalg.norm(normals[i])
        if length > 0:
            normals[i] /= length
    
    return normals


def generate_terrain_colors(heights, resolution):
    """
    Genera colores para el terreno basados en la altura.
    """
    colors = np.zeros((resolution**2, 4), dtype=np.uint8)
    
    # Normalizar alturas a rango [0, 1]
    min_h = heights.min()
    max_h = heights.max()
    if max_h - min_h > 0:
        normalized_heights = (heights - min_h) / (max_h - min_h)
    else:
        normalized_heights = np.ones_like(heights) * 0.5
    
    for i, h in enumerate(normalized_heights):
        if h < 0.3:  # Zonas bajas: verde oscuro
            colors[i] = [34, 139, 34, 255]
        elif h < 0.5:  # Zonas medias: verde claro
            colors[i] = [124, 252, 0, 255]
        elif h < 0.7:  # Colinas: marrón
            colors[i] = [139, 90, 43, 255]
        elif h < 0.85:  # Montañas: gris
            colors[i] = [128, 128, 128, 255]
        else:  # Picos: blanco (nieve)
            colors[i] = [255, 255, 255, 255]
    
    return colors
