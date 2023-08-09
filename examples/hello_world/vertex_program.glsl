#version 330
in vec3 position;
in vec3 color;

out vec3 fragColor;

void main()
{
    fragColor = color;
    gl_Position = vec4(position, 1.0f);
}