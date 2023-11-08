import numpy as np
import pyglet
import OpenGL.GL as GL
import sys

if sys.path[0] != "":
    sys.path.insert(0, "")

import grafica.transformations as tr
from world import World
from pajarito import Pajarito
from grid import Grid

program_state = {
    "paused": False,
    "bird_camera": False,
    "view_matrix": None,
    "projection_matrix": None,
}


def main():
    window = pyglet.window.Window(width=1024, height=768)

    flock = World(
        60,
        width=640,
        height=480,
        speed=0.75,
        vision=100,
        separation=20,
        cohere=0.001,
        separate=0.1,
        match=0.001,
    )

    pajarito_3d = Pajarito()
    grid = Grid()

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
        grid.draw(tr.scale(320, 240, 1) @ tr.translate(1, 1, 0))

        pajarito_3d.setup_transforms(
            program_state["view_matrix"], program_state["projection_matrix"]
        )

        for i, boid in enumerate(flock.iter_agents()):
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

    def view_transform(bird_camera):
        if not bird_camera:
            viewPos = np.array([320, 240, 600])
            view = tr.lookAt(viewPos, np.array([320, 240, 0]), np.array([0, 1, 0]))
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
        60, float(window.width) / float(window.height), 0.01, 1000
    )

    pyglet.clock.schedule_interval(tick, 1 / 60)
    pyglet.app.run()


if __name__ == "__main__":
    main()
