#version 330
in vec3 position;
in float curvature;
uniform mat4 transform;

out vec3 fragColor;

void main()
{
    fragColor = vec3(0.9, curvature, 0.9);
    gl_Position = transform * vec4(position, 1.0f);
}