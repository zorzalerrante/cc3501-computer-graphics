#version 330

in vec2 frag_texcoord;
out vec4 outColor;
uniform sampler2D sampler_tex;

void main()
{
    vec4 texel = texture(sampler_tex, frag_texcoord);
    if (texel.a < 0.5)
        discard;
    outColor = texel;
}