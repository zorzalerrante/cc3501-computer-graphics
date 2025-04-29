#version 330
in vec3 position;
in vec2 uv;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

out vec2 frag_texcoord;

void main()
{
    vec4 pos = projection * view * transform * vec4(position, 1.0f);
    frag_texcoord = uv;
    
    gl_Position = pos;
}