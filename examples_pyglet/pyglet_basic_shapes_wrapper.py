import pyglet

from pyglet.shapes import Polygon, get_default_shader, Batch, _ShapeGroup
from pyglet.gl import GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA
from pyglet.gl import GL_TRIANGLES, GL_LINES, GL_BLEND


class CustomShape2D(Polygon):

    def __init__(self, vertices, indices, mode=GL_TRIANGLES, batch=None, group=None):
        """Create a convex polygon. This is a wrapper from previous basic_shapes
        module of Daniel Calderon.

        The polygon's anchor point defaults to the first vertex point.
        The vertices must be a list of 3D points in the format:
        [
            x1, y1, z1, r1, g1, b1,
            x2, y2, z2, r2, g2, b2,
            x3, y3, z3, r3, g3, b3,
        ]
        Where every z point defaults to 0.

        :Parameters:
            `vertices` : List[float]
                The vertex info for each point in the polygon.
            `indices` : List[int]
                Information about how the vertices connect with each other. For example
                [0, 1, 2] makes a triangle between vertices 0, 1 and 2 if GL_TRIANGLES is used.
            `mode` : int
                OpenGL drawing mode enumeration; for example, one of
                ``GL_POINTS``, ``GL_LINES``, ``GL_TRIANGLES``, etc.
            `batch` : `~pyglet.graphics.Batch`
                Optional batch to add the polygon to.
            `group` : `~pyglet.graphics.Group`
                Optional parent group of the polygon.
        """
        self._rotation = 0
        self._scale = 1.0
        self._num_verts = len(vertices) // 5
        _coordinates = [vertices[ix:ix + 2] for ix in range(0, len(vertices), 5)]
        coordinates = []
        for pair_coordinates in _coordinates:
            coordinates += pair_coordinates
        # Adjusting relative position to screen
        coordinates = [int(coord) for coord in coordinates]
        self._coordinates =coordinates

        _colors = [vertices[ix:ix+3] for ix in range(2, len(vertices), 5)]
        colors = []
        for rgb_vertex in _colors:
            colors += rgb_vertex + [1.0] # adding alpha channel
        colors = [int(color * 255) for color in colors]
        
        program = get_default_shader()
        self._batch = batch or Batch()
        self._group = _ShapeGroup(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, program, group)

        self._vertex_list = program.vertex_list_indexed(
                                                count=self._num_verts,
                                                indices=indices, 
                                                mode=mode,
                                                batch=self._batch,
                                                group=self._group,
                                                colors=('Bn', colors),
        )
        self._update_vertices()
        # self._update_translation()

        self._set_color(colors)
        self._update_color()

    def _update_vertices(self):
        if not self._visible:
            self._vertex_list.vertices[:] = tuple([0] * ((len(self._coordinates) - 2) * 6))
        else:
            # Adjust all coordinates by the anchor.
            # Flattening the list before setting vertices to it.
            # self._vertex_list.vertices[:] = tuple(value for coordinate in triangles for value in coordinate)
            self._vertex_list.vertices[:] = tuple(coord * self._scale for coord in self._coordinates)

    def _set_color(self, in_colors):
        self.colors = in_colors

    def _update_color(self):
        """Send the new colors for each vertex to the GPU.

        This method must set the contents of `self._vertex_list.colors`
        using a list or tuple that contains the RGBA color components
        for each vertex in the shape. This is usually done by repeating
        `self._rgba` for each vertex.
        """
        self._vertex_list.colors[:] = self.colors

    @property
    def scale(self):
        """The outer radius of the star."""
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self._update_vertices()