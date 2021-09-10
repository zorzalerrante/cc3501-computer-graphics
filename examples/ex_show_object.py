import argparse
import open3d as o3d

parser = argparse.ArgumentParser()
parser.add_argument('--model', type=str, default='', help='Model name')
opt = parser.parse_args()

object = o3d.io.read_triangle_mesh(opt.model)
object.compute_vertex_normals()
color = [1.0, 0.78, 0.32]
object.paint_uniform_color(color)
o3d.visualization.draw_geometries([object])