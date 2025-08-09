import numpy as np
import matplotlib.pyplot as plt

from grafica.math import normalize
import grafica.transformations as tr
from .raytracing import trace_ray, add_plane, add_sphere, add_mesh
import trimesh as tm
import click
    
@click.command("raytracing_cpu", short_help='Prueba de concepto de RT en la CPU')
@click.argument("filename", type=str)
@click.option("--width", type=int, default=320)
@click.option("--height", type=int, default=280)
def raytracing_cpu(filename, width, height):
    #NUEVO: Cargamos el modelo 3D
    charmander = tm.load("assets/Charmander.STL", force= "mesh")
    squirtle = tm.load("assets/Squirtle.STL", force= "mesh")
    bulbasaur = tm.load("assets/Bulbasaur.STL", force= "mesh")

    #NUEVO: Es posible que necesite algunos ajustes para tamaño y orientación
    charmander.apply_scale(1.5/charmander.scale)
    squirtle.apply_scale(1.5/squirtle.scale)
    bulbasaur.apply_scale(1.5/bulbasaur.scale)
    mesh_rotateZ = tr.rotationZ(np.pi)
    mesh_rotateX = tr.rotationX(np.pi/2)
    charmander.apply_transform(mesh_rotateZ @ mesh_rotateX)
    squirtle.apply_transform(mesh_rotateZ @ mesh_rotateX)
    bulbasaur.apply_transform(mesh_rotateZ @ mesh_rotateX)

    # una descripción básica de la escena
    scene = [add_mesh([1.35, -0.5, 1.6],charmander, [1, 0.6, 0]),
            add_mesh([0.25, -0.5, 2.25],squirtle, [.2, .8, 1]),
            add_mesh([-1.5, -0.5, 3.5], bulbasaur, [0.3, 1, .2]),
            add_plane([0., -.5, 0.], [0., 1., 0.]),
        ]

    # atributos de la luz
    L = np.array([5., 5., -10.])
    color_light = np.ones(3)
    ambient = .05

    # atributos de material
    diffuse_c = 1.
    specular_c = 1.
    specular_k = 50

    # ¿cuántos rebotes vamos a considerar?
    depth_max = 5
    # color base
    col = np.zeros(3)
    # posición de la cámara (origen de los rayos)
    O = np.array([0., 0.35, -1.])
    # posición focal de la cámara
    Q = np.array([0., 0., 0.])

    # en este buffer guardaremos la imagen
    # noten que está traspuesta dado que no estamos trabajando con OpenGL, sino numpy
    img = np.zeros((height, width, 3))

    # ¿cómo mapear a coordenadas de la pantalla?
    # x0, y0, x1, y1
    # (aquí debiésemos usar una matriz de proyección)
    r = float(width) / height
    S = (-1., -1. / r + .25, 1., 1. / r + .25)

    # iteramos en cada píxel.
    # aquí se hace de manera secuencial
    # pero hay mucho de esto que podría paralelizarse
    for i, x in enumerate(np.linspace(S[0], S[2], width)):
        # esto imprime el progreso
        if i % 10 == 0:
            print(i / float(width) * 100, "%")

        for j, y in enumerate(np.linspace(S[1], S[3], height)):
            # reseteamos el color
            col[:] = 0
            # actualizamos la dirección del rayo
            Q[:2] = (x, y)
            D = normalize(Q - O)
            rayO, rayD = O, D

            # no ha rebotado aún
            depth = 0
            # factor de reflexión para acumular colores
            reflection = 1.
            
            # trazamos el rayo cuantas veces sea necesario
            while depth < depth_max:
                traced = trace_ray(rayO, rayD, scene, L, O, ambient, diffuse_c, specular_c, specular_k, color_light)

                if not traced:
                    break

                obj, M, N, col_ray = traced
                
                # Reflection: create a new ray.
                rayO, rayD = M + N * .0001, normalize(rayD - 2 * np.dot(rayD, N) * N)
                depth += 1
                col += reflection * col_ray
                reflection *= obj.get('reflection', 1.)

            # guardamos el color final en el píxel
            img[height - j - 1, i, :] = np.clip(col, 0, 1)

    # guardamos la imagen.
    # nota: ¡fíjense en el aliasing de la imagen!
    plt.imsave(filename, img)