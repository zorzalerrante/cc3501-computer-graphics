#version 330
uniform float max_ttl;
uniform vec2 resolution;

in vec2 position;
in float ttl;
out float alpha;

void main()
{
    vec2 screen_pos = position.xy / resolution * 2.0 - 1.0;

    gl_PointSize = 15.0 * (ttl / max_ttl);
    gl_Position = vec4(screen_pos, 0.0, 1.0);
    alpha = ttl / max_ttl;
}