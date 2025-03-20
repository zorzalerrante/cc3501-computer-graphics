#version 330

in vec2 position;
in vec2 uv;

out vec2 frag_texcoord;

void main() {
    frag_texcoord = uv;
    gl_Position = vec4(position, 0.0f, 1.0f);
}