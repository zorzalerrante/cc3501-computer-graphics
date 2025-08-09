import click

import pyvista as pv
from pyvista import examples


@click.command(
    "pyvista_orbital", short_help="Ejemplo básico de pyvista con orbitales atómicos"
)
@click.option("--width", type=int, default=800)
@click.option("--height", type=int, default=600)
def orbital(width, height):
    """
    Fuente: https://docs.pyvista.org/examples/99-advanced/atomic_orbitals#sphx-glr-examples-99-advanced-atomic-orbitals-py
    """
    grid = examples.load_hydrogen_orbital(3, 2, -2)

    pl = pv.Plotter(window_size=(width, height))
    vol = pl.add_volume(grid, cmap="magma", opacity=[1, 0, 1])
    vol.prop.interpolation_type = "linear"
    pl.camera.zoom(2)
    pl.show_axes()
    pl.show()


if __name__ == "__main__":
    orbital.callback(800, 600)
