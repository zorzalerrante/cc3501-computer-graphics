#version 330
in vec3 fragNormal;
in vec3 fragPos;
out vec4 outColor;
uniform vec3 color;
uniform vec3 lightPos;
uniform vec3 viewPos;
void main() {
    // Iluminación básica Phong
    vec3 ambient = 0.15 * color;
    
    // Difusa
    vec3 lightDir = normalize(lightPos - fragPos);
    float diff = max(dot(fragNormal, lightDir), 0.0);
    vec3 diffuse = diff * color;
    
    // Especular
    vec3 viewDir = normalize(viewPos - fragPos);
    vec3 reflectDir = reflect(-lightDir, fragNormal);
    float spec = pow(max(dot(viewDir, reflectDir), 0.0), 32);
    vec3 specular = 0.5 * spec * vec3(1.0);
    
    vec3 result = ambient + diffuse + specular;
    outColor = vec4(result, 1.0);
}