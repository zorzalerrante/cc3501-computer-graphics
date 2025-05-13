#version 330

// Atributos de entrada (por vértice)
in vec3 position;  // Posición del vértice en espacio local
in vec3 normal;    // Vector normal del vértice en espacio local
in vec4 color;     // Color del vértice (RGBA, 0-255)

// Matrices de transformación uniformes
uniform mat4 transform;       // Matriz modelo (local a mundo)
uniform mat4 view;            // Matriz de vista (mundo a vista)
uniform mat4 projection;      // Matriz de proyección (vista a clip)
uniform mat4 light_transform; // Matriz combinada para vista desde la luz

// Datos a enviar al fragment shader
out vec4 frag_color;          // Color interpolado
out vec3 frag_normal;         // Normal en espacio mundo
out vec3 frag_pos;            // Posición en espacio mundo
out vec4 pos_in_light_space;  // Posición vista desde la luz (para shadow mapping)

void main()
{
    // Transformar vértice a espacio mundo
    vec4 world_position = transform * vec4(position, 1.0);
    
    // Calcular matriz para transformar las normales correctamente
    // (necesario si hay escalado no uniforme o transformaciones de esquileo)
    mat3 normal_matrix = transpose(inverse(mat3(transform)));
    
    // Preparar datos para el fragment shader
    frag_normal = normalize(normal_matrix * normal);  // Normal transformada y normalizada
    frag_color = color / 255.0;                       // Convertir color de [0-255] a [0-1]
    frag_pos = vec3(world_position);                  // Posición en espacio mundo
    
    // Calcular posición desde el punto de vista de la luz (para sombras)
    pos_in_light_space = light_transform * world_position;
    
    // Posición final del vértice (coordenadas de clip)
    gl_Position = projection * view * world_position;
}