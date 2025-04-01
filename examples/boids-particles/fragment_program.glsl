#version 330

in vec3 frag_color;
out vec4 out_color;

void main()
{
    out_color = vec4(frag_color, 0.85);
}