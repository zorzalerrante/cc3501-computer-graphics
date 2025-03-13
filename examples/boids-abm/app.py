import numpy as np
import pyglet
import OpenGL.GL as GL

import grafica.transformations as tr
from .world import World
from .pajarito import Pajarito
from .grid import Grid

from pathlib import Path

import click

# variables del estado del programa
program_state = {
    "paused": False,
    "bird_camera": False,
    "view_matrix": None,
    "projection_matrix": None,
}

# variables del mundo que simularemos
world_parameters = {
    "vision": {"min": 60, "max": 200, "default": 100},
    "cohere_factor": {"min": 0.0001, "max": 0.001, "default": 0.0005},
    "separation_factor": {"min": 0.0001, "max": 0.01, "default": 0.005},
    "match_factor": {"min": 0.0001, "max": 0.01, "default": 0.005},
    "distance": {"min": 20, "max": 60, "default": 25},
    "speed": {"min": 0.01, "max": 1.0, "default": 0.75},
}

@click.command("boids_abm", short_help='Simulador de vuelo de pajaritos usando Agent-Based Modeling')
@click.option("--n_pajaritos", type=int, default=50)
@click.option("--width", type=int, default=1024)
@click.option("--height", type=int, default=768)
@click.option("--world_width", type=int, default=960)
@click.option("--world_height", type=int, default=540)
def boids_abm(n_pajaritos, width, height, world_width, world_height):
    # noten que el tamaño de la ventana es independiente del tamaño del mundo.
    window = pyglet.window.Window(width=width, height=height)

    # este es el mundo a simular.
    flock = World(
        n_pajaritos,
        # y muchos parámetros
        width=world_width,
        height=world_height,
        speed=world_parameters["speed"]["default"],
        vision=world_parameters["vision"]["default"],
        distance=world_parameters["distance"]["default"],
        cohere_factor=world_parameters["cohere_factor"]["default"],
        separation_factor=world_parameters["separation_factor"]["default"],
        match_factor=world_parameters["match_factor"]["default"],
    )

    # dibujaremos cada boid como un pajarito (zorzal)
    pajarito_3d = Pajarito()
    # también dibujaremos una grilla para saber el tamaño del mundo
    grid = Grid()

    # esta vez dibujaremos elementos de control que nos permitirán
    # modificar los parámetros del mundo y de sus habitantes.
    # en pyglet estos elementos se dibujan a través de un "Batch" (lote)
    # así que lo creamos aquí.
    # GUI: Graphical User Interface
    gui_batch = pyglet.graphics.Batch()

    # los elementos GUI utilizan imágenes. hay que cargarlas con un...
    # cargador de pyglet especial para ello.
    # recibe como parámetro la ruta completa a la carpeta con imágenes.
    loader = pyglet.resource.Loader(str(Path("assets/UI").resolve()))

    # cargamos las imágenes
    slider_img = loader.image("bar.png")
    knob_img = loader.image("knob.png")

    # ahora crearemos un elemento GUI para cada parámetro del mundo
    sliders = {}
    labels = {}

    # antes de ver esta función leer lo que viene en el ciclo después
    def update_func(current_attr):
        max_value = world_parameters[current_attr]["max"]
        min_value = world_parameters[current_attr]["min"]

        # los valores de la slider van entre 1 y 100. así que debemos
        # normalizar el valor para que coincida con los de nuestras variables.
        def slider_update(widget, value):
            current_value = (value / 100) * (max_value - min_value) + min_value
            print(current_attr, current_value)
            for boid in flock.iter_agents():
                setattr(boid, current_attr, current_value)

        return slider_update

    for i, attr in enumerate(world_parameters.keys()):
        # ¿dónde estará en la pantalla?
        # se usan coordenadas de la ventana.
        pos_x = 50 + (slider_img.width + 20) * i
        pos_y = 50

        # crearemos un "slider", una barra donde se mueve un botón
        sliders[attr] = pyglet.gui.Slider(
            pos_x,
            pos_y,
            slider_img,
            knob_img,
            5,
            batch=gui_batch,
        )

        # se supone que esto le asigna un valor, pero no resulta :p
        sliders[attr].value = (
            world_parameters[attr]["default"] - world_parameters[attr]["min"]
        ) / (world_parameters[attr]["max"] - world_parameters[attr]["min"])
        sliders[attr].on_change(sliders[attr], sliders[attr].value)

        # con esto incorporamos el elemento GUI o "widget" en la ventana
        # eso permite interactuar con él.
        # nota: eso no lo dibuja. de eso se encarga el batch
        window.push_handlers(sliders[attr])

        # pondremos una etiqueta de texto sobre cada elemento
        labels[attr] = pyglet.text.Label(
            attr,
            font_name="Verdana",
            x=pos_x,
            y=pos_y + 10,
            font_size=12,
            color=(0, 0, 0, 255),
        )

        # ¡ahora debemos conectar nuestro mundo con la slider!
        # conectaremos una función de update con el evento "on_change"
        # que se activa cada vez que se cambia el valor correspondiente
        # en la UI
        # en Python las funciones son ciudadanas de primer nivel así que
        # podemos definirlas y retornarlas :D
        # en este caso, esta función es única para el atributo sobre el 
        # que estamos iterando
        # por eso con update_func entregamos la función que actualiza los
        # valores de esta variable/slider en particular
        sliders[attr].set_handler("on_change", update_func(attr))

    # esta función ejecutará un paso de la simulación
    def tick(time):
        if not program_state["paused"]:
            flock.step()

    @window.event
    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.V:
            program_state["bird_camera"] = not program_state["bird_camera"]

        if symbol == pyglet.window.key.P:
            program_state["paused"] = not program_state["paused"]

    @window.event
    def on_draw():
        GL.glClearColor(0.85, 0.85, 0.85, 1.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

        window.clear()
        program_state["view_matrix"] = view_transform(program_state["bird_camera"])

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        grid.pipeline["view"] = program_state["view_matrix"].reshape(16, 1, order="F")
        grid.pipeline["projection"] = program_state["projection_matrix"].reshape(
            16, 1, order="F"
        )
        grid.draw(
            tr.scale(world_width / 2, world_height / 2, 1) @ tr.translate(1, 1, 0)
        )

        pajarito_3d.setup_transforms(
            program_state["view_matrix"], program_state["projection_matrix"]
        )

        for boid in flock.iter_agents():
            angle = np.arctan2(boid.velocity[1], boid.velocity[0])

            transform = tr.matmul(
                [
                    tr.translate(boid.pos[0], boid.pos[1], 0.0),
                    tr.rotationZ(angle),
                    # alinear el pajarito
                    tr.uniformScale(15),
                    tr.rotationZ(np.deg2rad(-90)),
                    tr.rotationX(np.deg2rad(90)),
                    tr.rotationY(np.deg2rad(180)),
                ]
            )
            pajarito_3d.draw(transform)
            # break

        # dibujamos la GUI
        # ¡tenemos que desactivar el test de profundidad!
        # propuesto: ¿por qué?
        GL.glDisable(GL.GL_DEPTH_TEST)

        for l in labels.values():
            l.draw()

        gui_batch.draw()

    def view_transform(bird_camera):
        if not bird_camera:
            viewPos = np.array([world_width / 2, world_height / 2, 600])
            view = tr.lookAt(
                viewPos,
                np.array([world_width / 2, world_height / 2, 0]),
                np.array([0, 1, 0]),
            )
        else:
            boid = next(iter(flock.iter_agents()))
            bird_position = np.array([boid.pos[0], boid.pos[1], 0, 1])
            angle = np.arctan2(boid.velocity[1], boid.velocity[0])

            camera_transform = tr.matmul(
                [
                    tr.rotationZ(angle),
                    tr.translate(-25, 0, 25),
                    tr.rotationZ(-angle),
                ]
            )

            look_at_transform = tr.matmul(
                [
                    tr.rotationZ(angle),
                    tr.translate(20, 0, 0),
                    tr.rotationZ(-angle),
                ]
            )

            camera_position = np.matmul(camera_transform, bird_position)
            look_at_position = np.matmul(look_at_transform, bird_position)

            view = tr.lookAt(
                camera_position[0:3],
                look_at_position[0:3],
                np.array([0, 0, 1]),
            )

        return view

    program_state["view_matrix"] = view_transform(program_state["bird_camera"])
    program_state["projection_matrix"] = tr.perspective(
        65, float(window.width) / float(window.height), 0.01, 1000
    )

    pyglet.clock.schedule_interval(tick, 1 / 60)
    pyglet.app.run()


if __name__ == "__main__":
    main()
