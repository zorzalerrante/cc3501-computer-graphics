#version 330
uniform mat4 view;
uniform mat4 projection;
uniform float max_ttl;

in vec3 position;
in float ttl;
out float alpha;

void main()
{
    gl_PointSize = 15.0 * (ttl / max_ttl);
    gl_Position = projection * view * vec4(position, 1.0);
    alpha = ttl / max_ttl;
}