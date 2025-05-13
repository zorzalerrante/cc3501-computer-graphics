#version 330

in vec4 frag_color;
out vec4 out_color;

void main()
{
    out_color = vec4(vec3(gl_FragCoord.z), 1.0);
}