# Computación Gráfica y Modelamiento para ingenieros e ingenieras (CC3501)

**Este repositorio está desactualizado. El nuevo es https://github.com/PLUMAS-research/cc3501-computer-graphics** 

## Instalación

Es necesario el administrador de entornos [`conda`](https://docs.anaconda.com/free/anaconda/install/windows/). Les más valientes pueden intentarlo con [Miniconda](https://docs.anaconda.com/free/miniconda/) (una versión mínima que ocupa menos espacio y que recomiendo) y les más valientes aún instalar [`mamba`](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html) (una versión eficiente en términos de desempeño). Nota que más adelante usaremos `conda` como comando, pero si instalas `mamba` solo basta que reemplaces `conda` por `mamba`.

Una vez instalado el administrador es necesario abrir una consola o terminal. Si usas Windows, en el botón de inicio de Windows hay que ejecutar "Anaconda Prompt" (no sirve PowerShell, debe ser Anaconda Prompt, que se basa en `cmd.exe` ). Allí deben ir a la carpeta del curso (recuerden los comandos `cd` y `dir` en Windows, o `cd` y `ls` si están en GNU/Linux o Apple). En la carpeta raíz del repositorio hay un archivo llamado `environment.yml`. En la consola deben ejecutar:

`conda env create -n grafica -f environment.yml`

Eso instalará todo el _software_ necesario para el curso en un entorno llamado `grafica`. Un entorno es un conjunto de herramientas, _software_ y bibliotecas.

El siguiente comando activa el entorno para la sesión de terminal:

`conda activate grafica`

Tienes que ejecutarlo cada vez que uses una sesión (o ventana).

## Ejemplo en la caja de juguetes

El archivo `caja_de_juguetes.py` sirve como puerta de entrada a los distintos ejemplos del curso. Se ejecuta así:

`python caja_de_juguetes.py nombre_ejemplo parámetros opciones`

Algunos ejemplos no tienen parámetros ni opciones:

`python caja_de_juguetes hello_world`

Otros requieren parámetros:

`python caja_de_juguetes image_texture assets/dice.jpg`

Y las opciones no son requisito, puesto que cada programa tiene valores por omisión, pero, en caso de haberlas, se especifican así (en este caso, las opciones son `x0 = 10` e `y0 = - 1`):

`python caja_de_juguetes sr_jengibre --x0 10 --y0 -1`

Nota: si estás en Windows, es posible que en vez de simplemente escribir `python`, debas escribir la ruta completa al intérprete de Python de tu entorno `grafica`.

Para ver la lista de ejemplos, puedes ejecutar la caja de juguetes sin incluir un nombre de ejemplo:

`python caja_de_juguetes.py`

Esto debería imprimir en tu pantalla una salida similar a esta:

```
(grafica) $ python caja_de_juguetes.py
Usage: caja_de_juguetes.py [OPTIONS] COMMAND [ARGS]...


Options:
 --help  Show this message and exit.


Commands:
 arcball_example     Visor interactivo de modelos 3D
 boids_abm           Simulador de vuelo de pajaritos usando Agent-Based
                     Modeling
 cloth_pymunk        Simulación de tela con pymunk
 cloth_verlet        Simulación de tela usando una implementación ingenua de
                     integración de Verlet
 color_wheel         Ejemplo de espacios de color
 compositions        Ejemplo de composición de transformaciones
 dino_runner         Ejemplo de detección de colisiones en 2D
 falling_boxes       Ejemplo de uso de Pymunk
 hello_opengl        ¡Hola, OpenGL!
 hello_world         ¡Hola, mundo!
 image_pixel         Visor de imágenes
 image_texture       Visor de imágenes (versión textura)
 particles           Partículas simples
 projection_example  Ejemplo de proyección
 raytracing_cpu      Prueba de concepto de RT en la CPU
 solar_system        Sistema solar con grafos de escena
 sr_jengibre         Señor Jengibre
 transformed_bunny   Ejemplo de transformaciones con el conejo de Stanford
```

