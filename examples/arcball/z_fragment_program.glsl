#version 330

in float frag_depth;
out vec4 out_color;

void main() {
    out_color = vec4(1.0 - frag_depth, 0.0, 0.5, 1.0);
}