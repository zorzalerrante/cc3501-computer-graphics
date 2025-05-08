#version 330

in vec3 frag_color;
out vec3 out_color;

void main()
{
    // Añadimos un efecto de resplandor para que las luces parezcan emitir luz
    out_color = frag_color * 1.5;  // Más brillante que el color base
}