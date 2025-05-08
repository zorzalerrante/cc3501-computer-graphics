#version 330
in vec3 position;
in vec3 normal;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 light_1_position;
uniform vec3 light_2_position;
uniform vec3 view_position;

out vec3 frag_color;

// Función para calcular el componente difuso
vec3 calc_diffuse(vec3 normal_world, vec3 light_dir, vec3 light_color, vec3 material_diffuse) {
    float diff = max(dot(normal_world, light_dir), 0.0);
    return light_color * (diff * material_diffuse);
}

// Función para calcular el componente especular
vec3 calc_specular(vec3 normal_world, vec3 light_dir, vec3 view_dir, 
                  vec3 light_color, vec3 material_specular, float shininess) {
    vec3 reflect_dir = reflect(-light_dir, normal_world);
    float spec = pow(max(dot(view_dir, reflect_dir), 0.0), shininess);
    return light_color * (spec * material_specular);
}

// Función para calcular la iluminación Phong para una luz
vec3 calc_phong_light(vec3 position, vec3 normal_world, vec3 view_dir, 
                     vec3 light_position, vec3 light_color, 
                     vec3 material_diffuse, vec3 material_specular, float shininess) {
    vec3 light_dir = normalize(light_position - position);
    
    vec3 diffuse = calc_diffuse(normal_world, light_dir, light_color, material_diffuse);
    vec3 specular = calc_specular(normal_world, light_dir, view_dir, 
                                 light_color, material_specular, shininess);
    
    return diffuse + specular;
}

void main()
{
    // Propiedades del material (conejo brillante con tono rosado)
    vec3 material_ambient = vec3(0.2, 0.1, 0.15);
    vec3 material_diffuse = vec3(0.9, 0.1, 0.8);
    vec3 material_specular = vec3(1.0, 0.8, 1.0);
    float material_shininess = 32.0;
    
    // Colores de las luces
    vec3 light_1_color = vec3(0.0, 0.8, 1.0);  // Azul claro
    vec3 light_2_color = vec3(1.0, 0.3, 0.0);  // Naranja
    
    // Posición del vértice en coordenadas de mundo
    vec4 world_position = transform * vec4(position, 1.0);
    
    // Normal en espacio de mundo
    mat3 normal_matrix = transpose(inverse(mat3(transform)));
    vec3 normal_world = normalize(normal_matrix * normal);
    
    // Vector hacia la cámara
    vec3 view_dir = normalize(view_position - world_position.xyz);
    
    // Componente ambiental
    vec3 ambient = vec3(0.2) * material_ambient;
    
    // Calcular iluminación para cada luz
    vec3 light_1_contribution = calc_phong_light(
        world_position.xyz, normal_world, view_dir,
        light_1_position, light_1_color,
        material_diffuse, material_specular, material_shininess
    );
    
    vec3 light_2_contribution = calc_phong_light(
        world_position.xyz, normal_world, view_dir,
        light_2_position, light_2_color,
        material_diffuse, material_specular, material_shininess
    );
    
    // Combinar todos los componentes
    frag_color = ambient + light_1_contribution + light_2_contribution;
    
    // Limitar valores
    frag_color = min(frag_color, vec3(1.0));
    
    // Posición final
    gl_Position = projection * view * world_position;
}