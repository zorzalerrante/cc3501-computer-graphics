#version 330

out vec4 out_color;
uniform vec2 current_pos;
uniform vec2 resolution;
uniform sampler2D sampler_tex;
in vec2 frag_texcoord;

void main() {
    vec2 pixel_pos = gl_FragCoord.xy / resolution;

    float diff = length(pixel_pos - current_pos);

    if (diff < 0.0005) {
        out_color = vec4(1.0);
    } else {
        out_color = texture(sampler_tex, frag_texcoord) - vec4(0.001f, 0.001f, 0.001f, 0.0f);
    }
}