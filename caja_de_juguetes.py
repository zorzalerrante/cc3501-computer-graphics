#!/usr/bin/env python3

import click
import importlib

@click.group()
def grafica_cli():
    pass

from examples.image_pixel import image_pixel_viewer
grafica_cli.add_command(image_pixel_viewer)

from examples.color import color_wheel
grafica_cli.add_command(color_wheel)

from examples.hello_world import hola_mundo
grafica_cli.add_command(hola_mundo)

from examples.chroma_key import chroma_key
grafica_cli.add_command(chroma_key)

from examples.image_texture import image_viewer
grafica_cli.add_command(image_viewer)

from examples.sr_jengibre import sr_jengibre
grafica_cli.add_command(sr_jengibre)

from examples.particles.app import particulas
grafica_cli.add_command(particulas)

# la carpeta tiene un guion :) así que hay que usar otro método
boids = importlib.import_module('examples.boids-particles')
grafica_cli.add_command(boids.boids_particles)

from examples.arcball import arcball_example
grafica_cli.add_command(arcball_example)

from examples.cloth.app_pymunk import cloth_pymunk
grafica_cli.add_command(cloth_pymunk)

from examples.cloth.app_verlet import cloth_verlet
grafica_cli.add_command(cloth_verlet)

boids = importlib.import_module('examples.boids-abm.app')
grafica_cli.add_command(boids.boids_abm)

# TODO: hay que actualizar el código de este ejemplo
#from examples.collision_detection.dino_runner import dino_game
#grafica_cli.add_command(dino_game)

from examples.ray_triangle import ray_triangle_example
grafica_cli.add_command(ray_triangle_example)

from examples.hello_opengl import hola_opengl
grafica_cli.add_command(hola_opengl)

from examples.shadows import shadow_mapping
grafica_cli.add_command(shadow_mapping)

from examples.terrain import terrain_generation
grafica_cli.add_command(terrain_generation)

from examples.projection.app import projection_example
grafica_cli.add_command(projection_example)

from examples.pymunk_boxes.app import falling_boxes
grafica_cli.add_command(falling_boxes)

from examples.raytracing_cpu.app import raytracing_cpu
grafica_cli.add_command(raytracing_cpu)

from examples.scene_graphs.app import solar_system
grafica_cli.add_command(solar_system)

from examples.transformation_composition.app import compositions
grafica_cli.add_command(compositions)

from examples.transformations.app import transformed_bunny
grafica_cli.add_command(transformed_bunny)

from examples.disco_bunny.app import disco_bunny
grafica_cli.add_command(disco_bunny)

from examples.camera_path import camera_path
grafica_cli.add_command(camera_path)

from examples.pyvista_orbital import orbital
grafica_cli.add_command(orbital)

if __name__ == '__main__':
    grafica_cli()