#version 330
// es posible definir una constante
#define TWO_PI 6.28318530718

// las variables uniform también son variables de entrada.
// a diferencia de las variables "in", una variable de este tipo
// tiene el mismo valor para cada vértice. 
// podríamos decir que es un parámetro para el programa
// y no para el píxel específico (o vértice específicoen VP)
// que se esté procesando. 
// estas dos variables las configuramos desde Python
// time la actualizamos cuadro a cuadro
// la resolución es fija
uniform float time;
uniform vec2 resolution;

// cada FP debe entregar un color
// (también puede descartar un píxel)
out vec3 outColor;

// podemos definir funciones dentro de un FP
// en este caso, escribimos la fórmula de conversión de HSV a RGB
// en la fórmula del apunte, el color contiene grados
vec3 hsv_to_rgb(vec3 hsv_color) {
    float h = mod(hsv_color.x, 360.0);
    float s = hsv_color.y;
    float v = hsv_color.z;

    float c = v * s;
    float h_prima = h / 60.0;
    float x = c * (1.0 - abs(mod(h_prima, 2.0) - 1));
    float m = v - c;

    vec3 rgb;

    if(h_prima < 1.0) {
        rgb = vec3(c, x, 0.0);
    } else if(h_prima <= 2.0) {
        rgb = vec3(x, c, 0.0);
    } else if(h_prima <= 3.0) {
        rgb = vec3(0.0, c, x);
    } else if(h_prima < 4.0) {
        rgb = vec3(0.0, x, c);
    } else if(h_prima < 5.0) {
        rgb = vec3(x, 0.0, c);
    } else {
        rgb = vec3(c, 0.0, x);
    }

    return clamp(rgb + m, 0.0, 1.0);
}

// como suele suceder, la función principal se llama main
// ¡esta función grafica una rueda de color HSV!
void main() {
    // la variable gl_Fragcoord contiene las coordenadas del píxel dentro de la ventana
    // al ser una variable de OpenGL, no se declara, pero está disponible
    // la normalizamos al rango (0,1) al dividirla por la resolución
    vec2 st = gl_FragCoord.xy / resolution;

    // desplazamos el origen al centro de la pantalla
    vec2 to_center = vec2(0.5) - st;

    // calculamos el ángulo respecto al eje X (esto sería el tono o HUE)
    // lo transformamos desde radianes a grados
    float angle = atan(to_center.y, to_center.x) / TWO_PI * 360.0;
    // calculamos la distancia desde el centro (esto sería la Saturación)
    // lo multiplicamos por dos para forzar que lleguemos hasta la saturación máxima
    // Propuesto: ¿por qué?
    float radius = length(to_center) * 2.0;

    // Propuesto: ¿qué hace esto? 
    float value = abs(sin(time));

    outColor = hsv_to_rgb(vec3(angle, radius, value));
}