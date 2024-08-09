#version 330 core
out float FragColor;

in vec2 TexCoords;

uniform sampler2D gPosition;
uniform sampler2D gNormal;
uniform sampler2D texNoise;

uniform vec3 samples[64];
uniform mat4 projection;

// Parámetros
const int kernelSize = 64;
const float radius = 0.5;
const float bias = 0.025;

void main()
{
    // Obtener datos de entrada
    vec3 fragPos = texture(gPosition, TexCoords).xyz;
    vec3 normal = normalize(texture(gNormal, TexCoords).rgb);
    vec3 randomVec = normalize(texture(texNoise, TexCoords * vec2(800.0/4.0, 600.0/4.0)).xyz);
    
    vec3 tangent = normalize(randomVec - normal * dot(randomVec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TBN = mat3(tangent, bitangent, normal);
    
    // Calcular oclusión
    float occlusion = 0.0;
    for(int i = 0; i < kernelSize; ++i)
    {
        // Obtener muestra de posición
        vec3 samplePos = TBN * samples[i]; // De espacio tangente a espacio de vista
        samplePos = fragPos + samplePos * radius; 
        
        // Proyectar muestra de posición
        vec4 offset = vec4(samplePos, 1.0);
        offset = projection * offset; // De espacio de vista a espacio de clip
        offset.xyz /= offset.w; // Perspectiva divide
        offset.xyz = offset.xyz * 0.5 + 0.5; // Transformar a [0,1] range
        
        // Obtener profundidad de muestra
        float sampleDepth = texture(gPosition, offset.xy).z;
        
        // Comprobación de rango y acumulación
        float rangeCheck = smoothstep(0.0, 1.0, radius / abs(fragPos.z - sampleDepth));
        occlusion += (sampleDepth >= samplePos.z + bias ? 1.0 : 0.0) * rangeCheck;
    }
    
    occlusion = 1.0 - (occlusion / kernelSize);
    
    FragColor = occlusion;
}