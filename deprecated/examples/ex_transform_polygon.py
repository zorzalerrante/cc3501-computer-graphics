# coding=utf-8
"""Drawing and transforming polygons with matplotlib"""

import numpy as np
from matplotlib.patches import Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
import sys, os.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import grafica.transformations as tr

__author__ = "Daniel Calderon"
__license__ = "MIT"

def applyTransform(transform, vertices):

    # Creating an array to store the transformed vertices
    # Since we will replace its content, the initial data is just garbage memory.
    transformedVertices = np.ndarray((len(vertices), 2), dtype=float)

    for i in range(len(vertices)):
        vertex2d = vertices[i]
        # input vertex only has x,y
        # expresing it in homogeneous coordinates
        homogeneusVertex = np.array([vertex2d[0], vertex2d[1], 0.0, 1.0])
        transformedVertex = np.matmul(transform, homogeneusVertex)

        # we are not prepared to handle 3d in this example
        assert(transformedVertex[2] == 0.0)

        # converting the vertex back to 2d
        transformedVertices[i,0] = transformedVertex[0] / transformedVertex[3]
        transformedVertices[i,1] = transformedVertex[1] / transformedVertex[3]
        
    return transformedVertices


originalVertices = np.array([
    [4,5],
    [0,5],
    [0,0],
    [4,0],
    [4,3],
    [2,3],
    [2,2],
    [3,2],
    [3,1],
    [1,1],
    [1,4],
    [4,4]])

# TODO: Play with this script exploring different transformations
rotatedVertices = applyTransform(tr.rotationZ(np.pi/4), originalVertices)

originalPolygon = Polygon(originalVertices, True)
rotatedPolygon = Polygon(rotatedVertices, True)

originalPathCollection = PatchCollection([originalPolygon], alpha=0.4)
originalPathCollection.set_facecolor((0,0,1))

rotatedPathCollection = PatchCollection([rotatedPolygon], alpha=0.4)
rotatedPathCollection.set_facecolor((0,1,0))

fig, ax = plt.subplots()
ax.add_collection(originalPathCollection)
ax.add_collection(rotatedPathCollection)
ax.set_xlim(-6,6)
ax.set_ylim(-6,6)
plt.show()