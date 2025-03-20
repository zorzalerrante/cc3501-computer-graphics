#version 330

in vec2 frag_texcoord;
out vec4 out_color;
uniform sampler2D sampler_tex;

void main() {
    out_color = texture(sampler_tex, frag_texcoord);
}