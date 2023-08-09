# coding=utf-8
"""Face based data structure for a triangle mesh"""

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

def printFramed(text):
    N = len(text) + 6
    print("="*N)
    print("== " + str(text) + " ==")
    print("="*N)


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

    # Triangles are created from left to right
    triangles = [
        tm.Triangle(3, 4, 0),
        tm.Triangle(0, 4, 1),
        tm.Triangle(1, 4, 2),
        tm.Triangle(2, 4, 5)
    ]

    # We use just indices to the triangle list
    # Yes, we could use the triangle themselves as node objects.
    meshes = [
        tm.TriangleFaceMesh(0),
        tm.TriangleFaceMesh(1),
        tm.TriangleFaceMesh(2),
        tm.TriangleFaceMesh(3)
    ]

    # Making connections
    meshes[0].bc = meshes[1]
    meshes[1].ab = meshes[0]
    meshes[1].bc = meshes[2]
    meshes[2].ab = meshes[1]
    meshes[2].bc = meshes[3]
    meshes[3].ab = meshes[2]
    
    printFramed("All triangles")
    for i in range(len(meshes)):
        triangleMesh = meshes[i]
        triangleIndex = triangleMesh.data
        triangleIndices = triangles[triangleIndex]
        triangleVertices = createTriangleVertices(triangleIndices, vertices)

        print("Triangle (indices)", i, ":", triangleIndices)
        print("Triangle (vertices)", i, ":", triangleVertices)
        print("Connections:", triangleMesh)
        print()

    # We can verify the connections using the debugger or
    # printing a given triangle mesh

    printFramed("Navigating through the mesh")
    triangleMesh0 = meshes[0]
    print("triangleMesh0 :", triangleMesh0)
    print("triangleMesh0.bc :", triangleMesh0.bc)
    print("triangleMesh0.bc.ab <=> triangleMesh0 :", triangleMesh0.bc.ab)
    print()

    printFramed("Walking the mesh from left to right")
    mesh = meshes[0]
    while mesh != None:
        triangleIndex = mesh.data
        triangleIndices = triangles[triangleIndex]
        triangleVertices = createTriangleVertices(triangleIndices, vertices)
        print(triangleIndices)
        print(triangleVertices)
        print()

        # Yes, this only works because we know the next triangle is at the bc side of the triangle
        # For a more complex mesh, we will have connections at all triangle sides
        mesh = mesh.bc

    print()

    printFramed("Walking the mesh from right to left")
    mesh = meshes[3]
    while mesh != None:
        triangleIndex = mesh.data
        triangleIndices = triangles[triangleIndex]
        triangleVertices = createTriangleVertices(triangleIndices, vertices)
        print(triangleIndices)
        print(triangleVertices)
        print()

        # Yes, this only works because we know the previous triangle is at the ab side of the triangle
        # For a more complex mesh, we will have connections at all triangle sides
        mesh = mesh.ab
