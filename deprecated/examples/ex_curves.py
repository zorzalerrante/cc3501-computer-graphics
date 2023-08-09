# coding=utf-8
"""Hermite and Bezier curves using python, numpy and matplotlib"""

import numpy as np
import matplotlib.pyplot as mpl
from mpl_toolkits.mplot3d import Axes3D

__author__ = "Daniel Calderon"
__license__ = "MIT"


def generateT(t):
    return np.array([[1, t, t**2, t**3]]).T


def hermiteMatrix(P1, P2, T1, T2):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P1, P2, T1, T2), axis=1)
    
    # Hermite base matrix is a constant
    Mh = np.array([[1, 0, -3, 2], [0, 0, 3, -2], [0, 1, -2, 1], [0, 0, -1, 1]])    
    
    return np.matmul(G, Mh)


def bezierMatrix(P0, P1, P2, P3):
    
    # Generate a matrix concatenating the columns
    G = np.concatenate((P0, P1, P2, P3), axis=1)

    # Bezier base matrix is a constant
    Mb = np.array([[1, -3, 3, -1], [0, 3, -6, 3], [0, 0, 3, -3], [0, 0, 0, 1]])
    
    return np.matmul(G, Mb)


def plotCurve(ax, curve, label, color=(0,0,1)):
    
    xs = curve[:, 0]
    ys = curve[:, 1]
    zs = curve[:, 2]
    
    ax.plot(xs, ys, zs, label=label, color=color)
    

# M is the cubic curve matrix, N is the number of samples between 0 and 1
def evalCurve(M, N):
    # The parameter t should move between 0 and 1
    ts = np.linspace(0.0, 1.0, N)
    
    # The computed value in R3 for each sample will be stored here
    curve = np.ndarray(shape=(N, 3), dtype=float)
    
    for i in range(len(ts)):
        T = generateT(ts[i])
        curve[i, 0:3] = np.matmul(M, T).T
        
    return curve

if __name__ == "__main__":
    
    """
    Example for Hermite curve
    """
    
    P1 = np.array([[0, 0, 1]]).T
    P2 = np.array([[1, 0, 0]]).T
    T1 = np.array([[10, 0, 0]]).T
    T2 = np.array([[0, 10, 0]]).T
    
    GMh = hermiteMatrix(P1, P2, T1, T2)
    print(GMh)
    
    # Number of samples to plot
    N = 50
    
    hermiteCurve = evalCurve(GMh, N)
    
    # Setting up the matplotlib display for 3D
    fig = mpl.figure()
    ax = fig.gca(projection='3d')
        
    plotCurve(ax, hermiteCurve, "Hermite curve", (1,0,0))
    
    """
    Example for Bezier curve
    """
    
    R0 = np.array([[0, 0, 1]]).T
    R1 = np.array([[0, 1, 0]]).T
    R2 = np.array([[1, 0, 1]]).T
    R3 = np.array([[1, 1, 0]]).T
    
    GMb = bezierMatrix(R0, R1, R2, R3)
    bezierCurve = evalCurve(GMb, N)
        
    plotCurve(ax, bezierCurve, "Bezier curve")
    
    # Adding a visualization of the control points
    controlPoints = np.concatenate((R0, R1, R2, R3), axis=1)
    ax.scatter(controlPoints[0,:], controlPoints[1,:], controlPoints[2,:], color=(1,0,0))
    
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_zlabel('z')
    ax.legend()
    mpl.show()