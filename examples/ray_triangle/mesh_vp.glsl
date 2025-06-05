#version 330
in vec3 position;
in vec3 normal;
out vec3 fragNormal;
out vec3 fragPos;
uniform mat4 mvp;
uniform mat4 model;
void main() {
    gl_Position = mvp * vec4(position, 1.0);
    fragPos = vec3(model * vec4(position, 1.0));
    // Calcular la normal transformada directamente
    mat3 normalMatrix = transpose(inverse(mat3(model)));
    fragNormal = normalize(normalMatrix * normal);
}