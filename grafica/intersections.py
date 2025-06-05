import numpy as np

def ray_triangle_intersection(origin, direction, v0, v1, v2):
    """
    Algoritmo de Möller-Trumbore para intersección rayo-triángulo.
    Mejorado para manejar casos especiales y evitar problemas numéricos.
    """
    EPSILON = 1e-6
    
    # Vectores de los lados del triángulo
    edge1 = v1 - v0
    edge2 = v2 - v0
    
    # Calcular determinante
    h = np.cross(direction, edge2)
    a = np.dot(edge1, h)
    
    # Rayo paralelo al triángulo - usar tolerancia más grande
    if abs(a) < EPSILON:
        return False, 0, 0, 0
    
    # Considerar ambos lados del triángulo (no hacer backface culling)
    f = 1.0 / a
    s = origin - v0
    u = f * np.dot(s, h)
    
    # Verificar coordenada baricéntrica u con pequeña tolerancia
    if u < -EPSILON or u > 1.0 + EPSILON:
        return False, 0, 0, 0
    
    q = np.cross(s, edge1)
    v = f * np.dot(direction, q)
    
    # Verificar coordenada baricéntrica v con pequeña tolerancia
    if v < -EPSILON or u + v > 1.0 + EPSILON:
        return False, 0, 0, 0
    
    # Calcular t
    t = f * np.dot(edge2, q)
    
    # Intersección válida si t > 0 (con tolerancia pequeña)
    if t > EPSILON:
        return True, t, u, v
    
    return False, 0, 0, 0


def intersect_mesh(origin, direction, vertices, faces):
    """
    Encuentra la intersección más cercana del rayo con la malla.
    Mejorado con debugging y manejo de casos especiales.
    """
    min_t = float('inf')
    hit_point = None
    hit_face = -1
    hits_count = 0
    
    # Normalizar dirección para asegurar consistencia
    direction = direction / np.linalg.norm(direction)
    
    for i, face in enumerate(faces):
        v0 = vertices[face[0]]
        v1 = vertices[face[1]]
        v2 = vertices[face[2]]
        
        hit, t, u, v = ray_triangle_intersection(origin, direction, v0, v1, v2)
        
        if hit:
            hits_count += 1
            if t < min_t:
                min_t = t
                # Calcular punto usando coordenadas baricéntricas para mayor precisión
                w = 1.0 - u - v
                hit_point = w * v0 + u * v1 + v * v2
                hit_face = i
    
    if hits_count > 0:
        print(f"  Total hits: {hits_count}, closest at t={min_t:.6f}")
    
    return hit_face >= 0, hit_point, hit_face, min_t