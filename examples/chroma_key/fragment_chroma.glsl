#version 330

in vec2 frag_texcoord;
out vec4 out_color;

uniform sampler2D sampler_tex;
uniform vec3 chroma_color;
uniform float threshold;
uniform float time;

// Función para calcular un color de fondo que varía con el tiempo
vec3 background_color(float t) {
    float r = 0.5 + 0.5 * sin(t * 0.3);
    float g = 0.5 + 0.5 * sin(t * 0.37 + 2.0);
    float b = 0.5 + 0.5 * sin(t * 0.41 + 4.0);
    
    return vec3(r, g, b);
}

void main() {
    // Obtener el color del pixel de la textura
    vec4 texel = texture(sampler_tex, frag_texcoord);
    
    // Calcular la "distancia" entre el color del pixel y el chroma key
    // Usamos distancia euclidiana en el espacio RGB
    float distance = length(texel.rgb - chroma_color);
    
    // Si la distancia es menor que el umbral, reemplazamos el color
    if (distance < threshold) {
        // Calcular factor de mezcla (para bordes suaves)
        float blend_factor = smoothstep(0.0, threshold, distance);
        
        // Obtener color de fondo animado
        vec3 bg = background_color(time);
        
        // Mezclar el color original con el fondo según la distancia
        texel.rgb = mix(bg, texel.rgb, blend_factor);
    }
    
    out_color = texel;
}