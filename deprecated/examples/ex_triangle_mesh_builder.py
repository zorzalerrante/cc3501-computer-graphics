# coding=utf-8
"""Using the dedicated face based triangle mesh builder"""

import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.triangle_mesh as tm

__author__ = "Daniel Calderon"
__license__ = "MIT"


def createTriangleVertices(triangleIndices, vertices):
    a = vertices[triangleIndices.a]
    b = vertices[triangleIndices.b]
    c = vertices[triangleIndices.c]

    return tm.Triangle(a, b, c)


if __name__ == "__main__":

    # Creating all vertices.
    """
    This is the order for the vertices and triangles
    0-------1-------2
    | \  1  | 2   / |
    |   \   |   /   |
    | 0   \ | /   3 |
    3-------4-------5
    """

    vertices = [
        (0, 200, 0),
        (100, 250, 0),
        (200, 230, 50),
        (0, 100, 0),
        (110, 110, 100),
        (190, 90, 0)
    ]

    # This object helps us to create a mesh, generating all required connections automatically
    meshBuilder = tm.TriangleFaceMeshBuilder()

    # Adding all triangles to the builder
    meshBuilder.addTriangle(tm.Triangle(3, 4, 0))
    meshBuilder.addTriangle(tm.Triangle(0, 4, 1))
    meshBuilder.addTriangle(tm.Triangle(1, 4, 2))
    meshBuilder.addTriangle(tm.Triangle(2, 4, 5))

    # Do note that the order of adding the triangles is not relevant

    # Requesting the meshes
    meshes = meshBuilder.getTriangleFaceMeshes()

    # We can navigate through the mesh
    triangleMesh0 = meshes[0]
    print("triangleMesh0 :", triangleMesh0)
    print("triangleMesh0.bc :", triangleMesh0.bc)
    print("triangleMesh0.bc.ab <=> triangleMesh0 :", triangleMesh0.bc.ab)
    print()