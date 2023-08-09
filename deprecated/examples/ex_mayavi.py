"""
Example extracted from:
https://docs.enthought.com/mayavi/mayavi/auto/mlab_helper_functions.html#mayavi.mlab.contour3d

"""
from mayavi import mlab
import numpy as np

x, y, z = np.ogrid[-5:5:64j, -5:5:64j, -5:5:64j]

scalars = x * x * 0.5 + y * y + z * z * 2.0

mlab.contour3d(scalars, contours=4, transparent=True)
mlab.show()