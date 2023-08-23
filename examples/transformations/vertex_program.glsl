#version 330
in vec3 position;
uniform mat4 view_transform;

out vec3 fragColor;

void main()
{
    fragColor = vec3(1.0, 1.0, 1.0);
    gl_Position = view_transform * vec4(position, 1.0f);
}