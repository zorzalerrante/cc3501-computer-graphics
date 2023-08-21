#version 330
in vec3 position;
//in vec3 color;

out vec3 fragColor;

void main()
{
    fragColor = vec3(1.0, 1.0, 1.0);
    gl_Position = vec4(position, 1.0f);
}