import pyglet

def load_pipeline(vertex_path, fragment_path):
    with open(vertex_path) as f:
        vertex_source_code = f.read()

    with open(fragment_path) as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    return pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)