#version 330 core
         
in vec3 position;
in vec3 color;
in vec3 normal;

out vec3 fragPosition;
out vec3 fragOriginalColor;
out vec3 fragNormal;

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

void main(){

    fragPosition = vec3(model * vec4(position, 1.0));
    fragOriginalColor = color;
    fragNormal = mat3(transpose(inverse(model))) * normal;  
    gl_Position = projection * view * vec4(fragPosition, 1.0);

}

