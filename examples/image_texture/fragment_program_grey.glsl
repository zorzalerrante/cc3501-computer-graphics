#version 330

in vec2 frag_texcoord;
out vec3 out_color;
uniform sampler2D sampler_tex;

void main() {
    vec4 rgba_color = texture(sampler_tex, frag_texcoord);
    float avg = (rgba_color.x + rgba_color.y + rgba_color.z) / 3.0f;
    out_color = vec3(avg, avg, avg);
}