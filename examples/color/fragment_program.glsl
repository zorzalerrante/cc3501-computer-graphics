#version 330
#define TWO_PI 6.28318530718

uniform float time;
uniform vec2 resolution;
in vec3 fragColor;
out vec4 outColor;

// créditos: https://www.shadertoy.com/view/MsS3Wc
vec3 hsv2rgb(in vec3 c) {
    vec3 rgb = clamp(abs(mod(c.x * 6.0 + vec3(0.0, 4.0, 2.0), 6.0) - 3.0) - 1.0, 0.0, 1.0);
    rgb = rgb * rgb * (3.0 - 2.0 * rgb);
    return c.z * mix(vec3(1.0), rgb, c.y);
}

void main() {
    vec2 st = gl_FragCoord.xy / resolution;
    
    vec2 to_center = vec2(0.5) - st;
    float angle = atan(to_center.y, to_center.x);
    float radius = length(to_center) * 2.0;

    vec3 hsv_color = hsv2rgb(vec3((angle/TWO_PI) + 0.5, radius, 1.0));

    outColor = vec4(hsv_color, abs(sin(time)));
}