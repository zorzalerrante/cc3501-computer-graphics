#version 330
in vec3 position;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

uniform float near_plane;
uniform float far_plane;

out float frag_depth;

void main()
{
    vec4 pos = projection * view * transform * vec4(position, 1.0f);
    gl_Position = pos;
    frag_depth = gl_Position.z / (far_plane - near_plane);
}