#version 330 core
layout (location = 0) out vec3 gPosition;
layout (location = 1) out vec3 gNormal;

in vec3 FragPos;
in vec3 Normal;

void main()
{    
    // Almacenar la posición del fragmento en el espacio de vista
    gPosition = FragPos;
    
    // Almacenar la normal del fragmento
    gNormal = normalize(Normal);
}