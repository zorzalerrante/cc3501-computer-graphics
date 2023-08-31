#version 330
in vec3 position;
uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

out vec3 fragColor;

void main()
{
    fragColor = vec3(0.0, 0.0, 0.0);
    gl_Position = projection * view * transform * vec4(position, 1.0f);
}