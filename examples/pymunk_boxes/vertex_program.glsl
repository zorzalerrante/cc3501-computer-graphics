#version 330
in vec3 position;
//in vec3 color;
uniform mat4 projection;
uniform mat4 transform;
uniform mat4 view;

out vec3 fragColor;

void main()
{
    fragColor = vec3(1.0, 1.0, 1.0);
    gl_Position = projection * view * transform * vec4(position, 1.0f);
}