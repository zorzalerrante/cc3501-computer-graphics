#version 330
in vec3 position;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;
uniform vec3 bulb_color;

out vec3 frag_color;

void main()
{
    // Pasamos directamente el color de la luz al fragment shader
    frag_color = bulb_color;
    
    // Posición transformada
    gl_Position = projection * view * transform * vec4(position, 1.0f);
}