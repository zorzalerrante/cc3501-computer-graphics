# coding=utf-8
"""Bezier Surface using python, numpy and matplotlib"""

import numpy as np
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D

__author__ = "Daniel Calderon"
__license__ = "MIT"


def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T


def evalBernstein3(k, t):
    # Full Bezier Matrix
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
    
    T = generateT(t)
    
    return np.dot(Mb[k,:], T)[0]


def evalBezierSurfaceSample(ps, t, s):
    
    Q = np.zeros(3)
    for k in range(4):
        for l in range(4):
            Bk = evalBernstein3(k, s)
            Bl = evalBernstein3(l, t)
            
            Q += Bk * Bl * ps[k, l]
            
    return Q

def evalBezierSurface(ps, ts, ss):
    
    Q = np.ndarray(shape=(N, N, 3), dtype=float)
    for i in range(len(ts)):
        for j in range(len(ss)):
            Q[i,j] = evalBezierSurfaceSample(ps, ts[i], ss[j])

    return Q

if __name__ == "__main__":
    
    """
    Defining control points
    """
    
    # A 4x4 array with a control point in each of those positions
    P = np.ndarray(shape=(4, 4, 3), dtype=float)
    P[0, 0, :] = np.array([[0, 0, 0]])
    P[0, 1, :] = np.array([[0, 1, 0]])
    P[0, 2, :] = np.array([[0, 2, 0]])
    P[0, 3, :] = np.array([[0, 3, 0]])
    
    P[1, 0, :] = np.array([[1, 0, 0]])
    P[1, 1, :] = np.array([[1, 1, 10]])
    P[1, 2, :] = np.array([[1, 2, 10]])
    P[1, 3, :] = np.array([[1, 3, 0]])
    
    P[2, 0, :] = np.array([[2, 0, 0]])
    P[2, 1, :] = np.array([[2, 1, 10]])
    P[2, 2, :] = np.array([[2, 2, 10]])
    P[2, 3, :] = np.array([[2, 3, 0]])
    
    P[3, 0, :] = np.array([[3, 0, 0]])
    P[3, 1, :] = np.array([[3, 1, -5]])
    P[3, 2, :] = np.array([[3, 2, -5]])
    P[3, 3, :] = np.array([[3, 3, 0]])
    
    # Setting up the matplotlib display for 3D
    fig = mpl.figure()
    ax = fig.gca(projection='3d')
    
    """
    Visualizing the control points
    """
    # They are sorted into a list of points
    Pl = P.reshape(16, 3)
    
    # Each component is queried from the previous array
    ax.scatter(Pl[:,0], Pl[:,1], Pl[:,2], color=(1,0,0), label="Control Points")
    
    """
    Discretizing the surface
    """
    # We use the same amount of samples for both, t and s parameters
    N = 10
    
    # The parameters t and s should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    ss = np.linspace(0.0, 1.0, N)
    
    # This function evaluates the bezier surface at each t and s samples in the arrays
    # The solution is stored in the 2D-array Q, where each sample is a 3D vector
    Q = evalBezierSurface(P, ts, ss)
    
    """
    Visualizing the Bezier surface
    """
    # For convenience, we re-organize the data into a list of points
    QlinearShape = (Q.shape[0] * Q.shape[1], 3)
    Ql = Q.reshape(QlinearShape)
    
    # An option is to plot just each dot computed
    #ax.scatter(Ql[:,0], Ql[:,1], Ql[:,2], color=(0,0,1))
    
    # The more elegant option is to make a triangulation and visualize it as a surface
    surf = ax.plot_trisurf(Ql[:,0], Ql[:,1], Ql[:,2], linewidth=0, antialiased=False)

    # Showing the result
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.title("Bezier Surface")
    mpl.show()