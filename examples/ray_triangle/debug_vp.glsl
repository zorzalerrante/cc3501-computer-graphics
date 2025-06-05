#version 330
in vec3 position;
in vec3 color;
out vec3 frag_color;
uniform mat4 mvp;
void main() {
    gl_Position = mvp * vec4(position, 1.0);
    frag_color = color;
}