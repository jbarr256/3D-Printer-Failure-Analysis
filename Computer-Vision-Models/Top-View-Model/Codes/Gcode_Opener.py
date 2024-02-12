## Gcode Opener and Viewer
import numpy as np
from stl import mesh
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

my_mesh = mesh.Mesh.from_file('/Users/Joseph/Documents/GitHub/3D-Printer-Failure-Analysis/Computer-Vision-Models/Top-View-Model/Test-STL/70mm_low_poly_fox_MatterControl.stl')
#Test to Plot

figure = plt.figure()
axes = mplot3d.Axes3D(figure)

axes.add_collection3d(mplot3d.art3d.Poly3DCollection(my_mesh.vectors))
scale = my_mesh.points.flatten()
axes.auto_scale_xyz(scale, scale, scale)

plt.show()

