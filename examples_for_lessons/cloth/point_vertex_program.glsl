#version 330
uniform mat4 view;
uniform mat4 projection;

in vec3 position;

void main()
{
    gl_PointSize = 15.0;
    gl_Position = projection * view * vec4(position, 1.0);
}