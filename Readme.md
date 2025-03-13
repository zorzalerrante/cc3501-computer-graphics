# Computación Gráfica y Modelamiento para Ingenieros e Ingenieras (CC3501)

Este repositorio contiene el código asociado alcurso. Se pueden descargar, aunque recomiendo clonarlo para después hacer _pull_ de las actualizaciones. Cambiará durante el semestre.

## Instalación

Es necesario [`conda`](https://docs.anaconda.com/free/anaconda/install/windows/). Les más valientes pueden intentarlo con [Miniconda](https://docs.anaconda.com/free/miniconda/)  y les más valientes aún instalar [`mamba`](https://mamba.readthedocs.io/en/latest/installation/micromamba-installation.html).

Una vez instalado es necesario abrir una consola. Si usas Windows, en el botón de inicio de Windows hay que ejecutar "Anaconda Prompt" (no sirve PowerShell, debe ser `cmd.exe` ).

Allí deben ir a la carpeta del curso (recuerden los comandos `cd` y `dir` en Windows, o `cd` y `ls` si están en GNU/Linux o Apple). En la carpeta raíz del repositorio hay un archivo llamado `environment.yml`. En la consola deben ejecutar:
```
conda env create -n grafica -f environment.yml
```
(si instalaron `mamba`, puede ser `mamba env create [...]`).

El siguiente comando activa el entorno:
```
conda activate grafica
```

## Ejemplos

El siguiente comando muestra la lista de ejemplos disponibles:
```
python caja_de_juguetes.py
```

Por ejemplo, el siguiente comando ejecuta `image_pixel` (ejemplo práctico de la clase de Colores). Este comando requiere un parámetro, una imagen:

```
python caja_de_juguetes.py image_pixel assets/torres-del-paine-sq.jpg
```