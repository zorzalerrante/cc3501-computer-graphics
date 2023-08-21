# IMPORTANTE: ESTOS EJEMPLOS SON DE VERSIONES PREVIAS DEL CURSO. 

Están aquí solo por motivos históricos.

---


# The Hall of Fame 2022
In [this](./HoF2022/hall.md) page, you can find the several renderings from the student's homeworks.


# The Hall of Fame 2021
In [this](./HoF/hall.md) page, you can find the several renderings from the student's homeworks.

# Computer Graphics with OpenGL and Python

This set of examples illustrate different computer graphics concepts in 2D and 3D while using: Python, OpenGL core profile, GLFW and Numpy.
    
## Raster

    
### ex_color_palette.py
Simulating an indirect color scheme with matplotlib
    
[![ex_color_palette.py](./screenshots/ex_color_palette.png)](./examples/ex_color_palette.py)
    
### ex_color_palette_anim.py
Animation changing the color palette  while simulating an indirect color scheme with matplotlib
    
[![ex_color_palette_anim.py](./screenshots/ex_color_palette_anim.gif)](./examples/ex_color_palette_anim.py)
    
### ex_sira_direct.py
Using a direct color scheme with sira
    
[![ex_sira_direct.py](./screenshots/ex_sira_direct.png)](./examples/ex_sira_direct.py)
    
### ex_sira_indirect.py
Using an indirect color scheme with sira
    
[![ex_sira_indirect.py](./screenshots/ex_sira_indirect.png)](./examples/ex_sira_indirect.py)
    
## OpenGL Basics

    
### opengl_version.py
Sample code to determine OpenGL version available on the current machine.
It attempts to set OpenGL core profile 3.3.
    
### ex_triangle.py
Hello OpenGL!
    
[![ex_triangle.py](./screenshots/ex_triangle.png)](./examples/ex_triangle.py)
    
### ex_quad.py
Drawing a Quad via a EBO
    
[![ex_quad.py](./screenshots/ex_quad.png)](./examples/ex_quad.py)
    
### ex_cube.py
Drawing a simple cube with OpenGL
    
[![ex_cube.py](./screenshots/ex_cube.png)](./examples/ex_cube.py)
    
### ex_stream_draw.py
Drawing a deformable shape using GL_STREAM_DRAW
    
[![ex_stream_draw.py](./screenshots/ex_stream_draw.gif)](./examples/ex_stream_draw.py)
    
## Transformations

    
### ex_transform_polygon.py
Drawing and transforming polygons with matplotlib
    
[![ex_transform_polygon.py](./screenshots/ex_transform_polygon.png)](./examples/ex_transform_polygon.py)
    
### ex_cpu_transforms.py
Transforming vertices in the CPU to create shapes.
    
[![ex_cpu_transforms.py](./screenshots/ex_cpu_transforms.png)](./examples/ex_cpu_transforms.py)
    
### ex_4shapes.py
Drawing 4 shapes with different transformations
    
[![ex_4shapes.py](./screenshots/ex_4shapes.png)](./examples/ex_4shapes.py)
    
### ex_transformations_showcase.py
Ilustrating different transformations
    
[![ex_transformations_showcase.py](./screenshots/ex_transformations_showcase.gif)](./examples/ex_transformations_showcase.py)
    
### ex_quad_controlled.py
Controlling the movement of a quad
    
[![ex_quad_controlled.py](./screenshots/ex_quad_controlled.gif)](./examples/ex_quad_controlled.py)
    
### ex_transform_imgui.py
Simple example using ImGui with GLFW and OpenGL

More info at:
https://pypi.org/project/imgui/

Installation:
pip install imgui[glfw]

Another example:
https://github.com/swistakm/pyimgui/blob/master/doc/examples/integrations_glfw3.py#L2
    
[![ex_transform_imgui.py](./screenshots/ex_transform_imgui.png)](./examples/ex_transform_imgui.py)
    
### ex_mouse.py
Interactions with keyboard and mouse via GLFW/python

More information at:
https://www.glfw.org/docs/latest/input_guide.html

How to convert GLFW/C calls to GLFW/python
https://pypi.org/project/glfw/
    
[![ex_mouse.py](./screenshots/ex_mouse.gif)](./examples/ex_mouse.py)
    
## Textures

    
### ex_texture_boo.py
Textures and transformations in 2D
    
[![ex_texture_boo.py](./screenshots/ex_texture_boo.png)](./examples/ex_texture_boo.py)
    
### ex_texture_quad.py
Texture Quad in 2D
    
[![ex_texture_quad.py](./screenshots/ex_texture_quad.png)](./examples/ex_texture_quad.py)
    
### ex_mipmap.py
Using mipmaps
    
[![ex_mipmap.py](./screenshots/ex_mipmap.png)](./examples/ex_mipmap.py)
    
### ex_binding_textures.py
Using 2 different textures in the same Fragment Shader
    
[![ex_binding_textures.py](./screenshots/ex_binding_textures.gif)](./examples/ex_binding_textures.py)
    
### ex_text_renderer.py
Example drawing text with OpenGL textures
    
[![ex_text_renderer.py](./screenshots/ex_text_renderer.gif)](./examples/ex_text_renderer.py)
    
## Scene Graphs

    
### ex_scene_graph_2dcars.py
Drawing many cars in 2D using scene_graph2
    
[![ex_scene_graph_2dcars.py](./screenshots/ex_scene_graph_2dcars.png)](./examples/ex_scene_graph_2dcars.py)
    
### ex_scene_graph_snowman.py
Drawing a Snowman using scene_graph
    
[![ex_scene_graph_snowman.py](./screenshots/ex_scene_graph_snowman.png)](./examples/ex_scene_graph_snowman.py)
    
## Curves

    
### ex_curves.py
Hermite and Bezier curves using python, numpy and matplotlib
    
[![ex_curves.py](./screenshots/ex_curves.png)](./examples/ex_curves.py)
    
## 3D World

    
### ex_projections.py
Projections example
    
[![ex_projections.py](./screenshots/ex_projections.gif)](./examples/ex_projections.py)
    
### ex_texture_dice.py
Textures and transformations in 3D
    
[![ex_texture_dice.py](./screenshots/ex_texture_dice.png)](./examples/ex_texture_dice.py)
    
### ex_height_plotter.py
plotting a 2d function as a surface
    
[![ex_height_plotter.py](./screenshots/ex_height_plotter.png)](./examples/ex_height_plotter.py)
    
### ex_scene_graph_3dcars.py
Drawing 3D cars via scene graph
    
[![ex_scene_graph_3dcars.py](./screenshots/ex_scene_graph_3dcars.png)](./examples/ex_scene_graph_3dcars.py)
    
### ex_mix2d3d.py
Example drawing 2D over a 3D world.
The trick is to not clear the color buffer after drawing 3D, and then draw 2D with the shader.

If it is required to draw 3D over 2D, you may need to clear the depth buffer with
glClear(GL_DEPTH_BUFFER_BIT)
    
[![ex_mix2d3d.py](./screenshots/ex_mix2d3d.png)](./examples/ex_mix2d3d.py)
    
### ex_surface.py
Bezier Surface using python, numpy and matplotlib
    
[![ex_surface.py](./screenshots/ex_surface.png)](./examples/ex_surface.py)
    
## Shading and Lighting

    
### ex_lighting.py
Showing lighting effects: Flat, Gauraud and Phong
    
[![ex_lighting.py](./screenshots/ex_lighting.gif)](./examples/ex_lighting.py)
    
### ex_lighting_texture2.py
Showing lighting effects over two textured objects: Flat, Gauraud and Phong
    
[![ex_lighting_texture2.py](./screenshots/ex_lighting_texture2.png)](./examples/ex_lighting_texture2.py)
    
### ex_obj_reader.py
Rendering a OBJ file simplified
    
[![ex_obj_reader.py](./screenshots/ex_obj_reader.png)](./examples/ex_obj_reader.py)
    
## Meshes

    
### ex_delaunay.py
Using Delaunay triangluation from the scipy library

documentation:
https://docs.scipy.org/doc/scipy-0.14.0/reference/generated/scipy.spatial.Delaunay.html
    
[![ex_delaunay.py](./screenshots/ex_delaunay.png)](./examples/ex_delaunay.py)
    
### ex_triangle_mesh.py
Face based data structure for a triangle mesh
    
### ex_triangle_mesh_builder.py
Using the dedicated face based triangle mesh builder
    
### ex_openmesh_pyramid.py
Using OpenMesh to compute normals for lighting effects
    
[![ex_openmesh_pyramid.py](./screenshots/ex_openmesh_pyramid.png)](./examples/ex_openmesh_pyramid.py)
    
## Physics and Collisions

    
### ex_collisions.py
Circles, collisions and gravity
    
[![ex_collisions.py](./screenshots/ex_collisions.gif)](./examples/ex_collisions.py)
    
## Advanced OpenGL

    
### ex_geometry_shader.py
Geometry Shader Basic Example

Adapted from: https://learnopengl.com/code_viewer_gh.php?code=src/4.advanced_opengl/9.1.geometry_shader_houses/geometry_shader_houses.cpp
    
[![ex_geometry_shader.py](./screenshots/ex_geometry_shader.png)](./examples/ex_geometry_shader.py)
    
### ex_render_to_texture.py
Render to Texture Example
    
[![ex_render_to_texture.py](./screenshots/ex_render_to_texture.gif)](./examples/ex_render_to_texture.py)
    