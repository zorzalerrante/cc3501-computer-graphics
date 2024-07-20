#version 330

in vec3 position;
in vec2 uv;

uniform mat4 view;
uniform mat4 projection;
uniform mat4 transform;

out vec2 frag_texcoord;

void main()
{
    frag_texcoord = uv;
    gl_Position = projection * view * transform * vec4(position, 1.0f);
}