#version 330

in vec2 position;
in vec3 color;
uniform vec2 resolution;

out vec3 frag_color;

void main()
{
    vec2 screen_pos = position.xy / resolution * 2.0 - 1.0;
    gl_PointSize = 5.0;
    gl_Position = vec4(screen_pos, 0.0, 1.0f);
    frag_color = color;
}