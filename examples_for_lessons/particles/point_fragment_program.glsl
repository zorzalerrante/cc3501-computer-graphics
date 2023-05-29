#version 330

in float alpha;
out vec4 outColor;

void main()
{
    outColor = vec4(1.0, 1.0, 1.0, alpha);
}