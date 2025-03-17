#version 330
/*
un vertex program se ejecuta por cada vértice de cada elemento graficado
los parámetros "in" son los datos que se copiaron a la GPU
en este caso, hay un parámetro position por cada vértice
*/
in vec2 position;

void main() {
    /*
    en rigor, lo mínimo que se requiere de un vertex program es
    que indique la posición del vértice que está procesando
    eso se hace con la variable gl_Position
    esta variable está en 4D :o
    como en el ejemplo teníamos una posición 2D,
    la tercera dimensión la dejamos como 0
    y la cuarta es 1.0 por motivos que veremos más adelante.
    usualmente, la cuarta dimensión siempre es 1.0.
    */
    gl_Position = vec4(position, 0.0f, 1.0f);
}