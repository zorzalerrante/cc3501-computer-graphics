import numpy as np
from grafica.math import normalize

# este archivo contiene funciones utilitarias para hacer ray tracing
# está basado en código de Cyrille Rossant
# lo iremos modificando con el tiempo
# para que funcione con mallas arbitrarias y otros elementos del curso


def intersect_plane(O, D, P, N):
    """
    Retorna la distancia desde O a la intersección del rayo (O, D) con el
    plano (P, N), o +inf si no hay intersección.
    O y P son puntos 3D, D y N (normal) son vectores normalizados.
    """
    denom = np.dot(D, N)
    if np.abs(denom) < 1e-6:
        return np.inf, None
    d = np.dot(P - O, N) / denom
    if d < 0:
        return np.inf, None
    return d, None


def intersect_sphere(O, D, S, R):
    """
    Retorna la distancia desde O hasta la intersección del rayo (O, D) con la
    esfera (S, R), o +inf si no hay intersección.
    O y S son puntos en 3D, D (dirección) es un vector normalizado, R es un escalar.
    """
    a = np.dot(D, D)
    OS = O - S
    b = 2 * np.dot(D, OS)
    c = np.dot(OS, OS) - R * R
    disc = b * b - 4 * a * c
    if disc > 0:
        distSqrt = np.sqrt(disc)
        q = (-b - distSqrt) / 2.0 if b < 0 else (-b + distSqrt) / 2.0
        t0 = q / a
        t1 = c / q
        t0, t1 = min(t0, t1), max(t0, t1)
        if t1 >= 0:
            if t0<0:
                return t1, None
            else:
                return t0, None
    return np.inf, None


#NUEVO: Este metodo define las intersecciónes en una malla
def intersect_mesh(O,D,mesh):
    origin = np.array([O])
    direction = np.array([D])
    locations, index_ray, index_tri = mesh.ray.intersects_location(
        ray_origins=origin,ray_directions=direction,multiple_hits=False
    )
    if len(locations) == 0:
        return np.inf, None
    dx,dy,dz = locations[0]-O
    distance = np.sqrt(dx**2+dy**2+dz**2)
    face_idx = index_tri[0]
    return distance, face_idx


def intersect(O, D, obj):
    if obj["type"] == "plane":
        return intersect_plane(O, D, obj["position"], obj["normal"])
    elif obj["type"] == "sphere":
        return intersect_sphere(O, D, obj["position"], obj["radius"])
    #NUEVO: Opción para una malla, se aplica su metodo de intersección.
    elif obj["type"] == "mesh":
        return intersect_mesh(O, D, obj["mesh"])


def get_normal(obj, M, face_idx = None):
    """
    Calcula la normal de la superficie de obj en el punto M.
    Por ahora solo funciona con esferas y planos.
    """
    if obj["type"] == "sphere":
        N = normalize(M - obj["position"])
    elif obj["type"] == "plane":
        N = obj["normal"]
    #NUEVO: Opción para una malla, es similar a como funcióna con una esfera
    elif obj["type"] == "mesh":
        N = obj["mesh"].face_normals[face_idx]
    return N


def get_color(obj, M):
    """
    Calcula el color correspondiente al objeto obj en el punto M.
    Más adelante esto debiese interpolar colores o texturas por vértice.
    """
    color = obj["color"]
    if not hasattr(color, "__len__"):
        color = color(M)
    return color


def trace_ray(
    rayO, rayD, scene, L, O, ambient, diffuse_c, specular_c, specular_k, color_light
):
    """
    Esta función traza un rayo a lo largo de la escena.
    Recibe la escena y las características de iluminación de esta.
    """

    # hay que identificar si el rayo se intersecta con algún elemento de la escena
    t = np.inf
    for i, obj in enumerate(scene):
        t_obj = intersect(rayO, rayD, obj)
        if t_obj[0] < t:
            t, obj_idx = t_obj[0], i

    # si t es infinito, quiere decir que no tocó a nada
    if t == np.inf:
        return

    # ya tenemos identificado el objeto con el que se intersecta el rayo.
    obj = scene[obj_idx]
    # calculamos el punto de intersección
    M = rayO + rayD * t

    distance, face_idx = intersect(rayO, rayD, obj)
    # calculamos las propiedades del objeto: normal y color
    N = get_normal(obj, M, face_idx)
    color = get_color(obj, M)

    # evaluamos la iluminación.
    toL = normalize(L - M)
    toO = normalize(O - M)

    # para saber si el objeto está iluminado, debemos emitir un rayo
    # que sale desde el punto M hacia la luz
    # y verificar que no se intersecta con otros objetos
    l = [
        intersect(M + N * 0.0001, toL, obj_sh)[0]
        for k, obj_sh in enumerate(scene)
        if k != obj_idx
    ]
    # aquí asumiremos que si no le llega luz, entonces no hay color.
    if l and min(l) < np.inf:
        return obj, M, N, ambient
    
    # como si le llega luz, calculamos el color
    # utilizaremos el modelo de iluminación de Phong
    # componente ambiental
    col_ray = ambient
    # componente difusa
    col_ray += obj.get("diffuse_c", diffuse_c) * max(np.dot(N, toL), 0) * color
    # componente especular (noten que esto es la modificación Blinn-Phong).
    col_ray += (
        obj.get("specular_c", specular_c)
        * max(np.dot(N, normalize(toL + toO)), 0) ** specular_k
        * color_light
    )
    return obj, M, N, col_ray


def add_sphere(position, radius, color):
    return dict(
        type="sphere",
        position=np.array(position),
        radius=np.array(radius),
        color=np.array(color),
        reflection=0.5,
    )


def add_plane(position, normal):
    color_plane0 = 1.0 * np.ones(3)
    color_plane1 = 0.0 * np.ones(3)

    return dict(
        type="plane",
        position=np.array(position),
        normal=np.array(normal),
        color=lambda M: (
            color_plane0 if (int(M[0] * 2) % 2) == (int(M[2] * 2) % 2) else color_plane1
        ),
        diffuse_c=0.75,
        specular_c=0.5,
        reflection=0.25,
    )

#NUEVO: Este metodo añade una malla y le asigna sus valores asociados correspondientes.
def add_mesh(position, mesh, color):
    mesh.apply_translation(position)
    return dict(
        type="mesh",
        mesh=mesh,
        color=np.array(color),
        reflection=0.5,
        position=position
        )

