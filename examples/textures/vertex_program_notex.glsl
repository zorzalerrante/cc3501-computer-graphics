#version 330
in vec3 position;
in vec3 normal;
in vec4 color;

uniform mat4 transform;
uniform mat4 view;
uniform mat4 projection;

out vec4 frag_color;
out vec3 frag_normal;
out vec3 frag_position;

void main()
{
    frag_position = vec3(projection * view *transform * vec4(position, 1.0f));
    frag_normal = mat3(transpose(inverse(transform))) * normal;
    frag_color = color / 255.f;
    
    gl_Position = vec4(frag_position, 1.0f);
}


