#version 330
in vec3 position;
in float curvature;
uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

out vec3 fragColor;

void main()
{
    fragColor = vec3(0.9, curvature, 0.9);
    gl_Position = projection * view * transform * vec4(position, 1.0f);
}