#version 330 core
out float FragColor;

in vec2 TexCoords;

uniform sampler2D ssaoInput;

void main() {
    vec2 texelSize = 1.0 / vec2(textureSize(ssaoInput, 0));
    float result = 0.0;
    for (int x = -2; x < 2; ++x) {
        vec2 offset = vec2(float(x) * texelSize.x, 0.0);
        result += texture(ssaoInput, TexCoords + offset).r;
    }
    FragColor = result / 4.0;
}