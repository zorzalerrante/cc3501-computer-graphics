# coding=utf-8
"""
Using Delaunay triangluation from the scipy library

documentation:
https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.Delaunay.html
"""

import numpy as np
from scipy.spatial import Delaunay
import matplotlib.pyplot as mpl

__author__ = "Daniel Calderon"
__license__ = "MIT"

#points = np.array([[0, 0], [0, 1.1], [1, 0], [1, 1]])
points = np.random.rand(20,2)

print("Random 2D points:")
print(points)

# Computing the Delaunay triangulation
tri = Delaunay(points)

# Plotting the triangulation => triplot
fig, axs = mpl.subplots(1,2)

axs[0].plot(points[:,0], points[:,1], 'o')
axs[0].set_xlabel('x')
axs[0].set_ylabel('y')

axs[1].triplot(points[:,0], points[:,1], tri.simplices.copy())
axs[1].plot(points[:,0], points[:,1], 'o')
axs[1].set_xlabel('x')
axs[1].set_ylabel('y')

mpl.show()