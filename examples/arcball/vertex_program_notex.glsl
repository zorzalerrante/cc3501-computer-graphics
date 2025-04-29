#version 330
in vec3 position;
in vec4 color;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

out vec4 frag_color;

void main()
{
    vec4 pos = projection * view * transform * vec4(position, 1.0f);
    frag_color = color / 255.f;
    
    gl_Position = pos;
}