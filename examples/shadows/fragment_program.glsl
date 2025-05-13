#version 330

// Entradas desde el vertex shader
in vec4 frag_color;        // Color del fragmento (RGBA)
in vec3 frag_normal;       // Normal del fragmento
in vec3 frag_pos;          // Posición del fragmento en espacio mundial
in vec4 pos_in_light_space; // Posición del fragmento vista desde la luz

// Salida: color final del fragmento
out vec4 out_color;

// Uniforms (constantes para todos los fragmentos)
uniform vec3 light_position;  // Posición de la luz en espacio mundial
uniform sampler2D shadow_map; // Mapa de sombras

// Calcula la componente difusa de la iluminación
vec3 calc_diffuse(vec3 normal_world, vec3 light_dir, vec3 light_color, vec3 material_diffuse) {
    float diff = max(dot(normal_world, light_dir), 0.0);
    return light_color * (diff * material_diffuse);
}

// Determina si un fragmento está en sombra (1.0) o iluminado (0.0)
float calc_shadow(vec4 frag_position_light_space) {
    // Transformar coordenadas a espacio NDC de la luz
    vec3 projected_coords = frag_position_light_space.xyz / frag_position_light_space.w;
    projected_coords = projected_coords * 0.5 + 0.5; // Transformar a rango [0,1]
    
    // Verificar si está dentro del frustum de la luz
    if(projected_coords.x < 0.0 || projected_coords.x > 1.0 ||
       projected_coords.y < 0.0 || projected_coords.y > 1.0 ||
       projected_coords.z < 0.0 || projected_coords.z > 1.0)
        return 0.0; // Fuera del frustum, no hay sombra
    
    // Obtener profundidad almacenada y actual
    float closest_depth = texture(shadow_map, projected_coords.xy).r;
    float current_depth = projected_coords.z;
    
    // Calcular bias para evitar shadow acne
    vec3 light_dir = normalize(light_position - frag_pos);
    float bias = max(0.05 * (1.0 - dot(normalize(frag_normal), light_dir)), 0.005);
    
    // PCF para suavizar bordes de sombras
    float shadow = 0.0;
    vec2 texel_size = 1.0 / textureSize(shadow_map, 0);
    
    for(int x = -1; x <= 1; ++x) {
        for(int y = -1; y <= 1; ++y) {
            float pcf_depth = texture(shadow_map, projected_coords.xy + vec2(x, y) * texel_size).r;
            shadow += current_depth - bias > pcf_depth ? 1.0 : 0.0;        
        }    
    }
    
    shadow /= 9.0; // Promedio de los 9 muestreos
    
    // Evitar sombras en objetos muy lejanos
    if(projected_coords.z > 0.995)
        shadow = 0.0;
        
    return shadow;
}

void main() {
    // out_color = vec4(normalize(frag_normal) * 0.5 + 0.5, 1.0);
    // return;

    vec3 material_ambient = vec3(0.2, 0.2, 0.2);
    vec3 material_diffuse = vec3(frag_color.rgb);  // Usar color de vértice como base

    // Color de la luz
    vec3 light_color = vec3(1.0, 1.0, 1.0);  // Luz blanca
    // Cálculo de iluminación difusa
    vec3 light_dir = normalize(light_position - frag_pos);
    vec3 diffuse = calc_diffuse(normalize(frag_normal), light_dir, light_color, material_diffuse);
    
    // Componente ambiental para evitar objetos completamente negros
    vec3 ambient = material_ambient * vec3(frag_color.rgb);
    
    // Cálculo de sombras
    float shadow = calc_shadow(pos_in_light_space);
    float in_light = 1 - shadow;
    
    // Combinar todo para el color final
    out_color = vec4(ambient + in_light * diffuse, frag_color.a);
    
    // Limitar valores máximos
    out_color = min(out_color, vec4(1.0));
    
}