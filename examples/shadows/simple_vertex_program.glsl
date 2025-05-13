#version 330
in vec3 position;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

out vec4 frag_color;

void main()
{
    frag_color = vec4(1.0);

    gl_Position = projection * view * transform * vec4(position, 1.0f);
}