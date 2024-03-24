# Computación Gráfica y Modelamiento para Ingenieros e Ingenieras

## Instalación

Este repositorio se pueden descargar, aunque recomiendo clonarlo para después hacer _pull_ de las actualizaciones.

Los pasos para hacerlo funcionar son los siguientes:

1. **Instalar `conda`**. Se puede descargar aquí: https://docs.anaconda.com/free/anaconda/install/windows/ (les más valientes pueden intentarlo con Miniconda: https://docs.anaconda.com/free/miniconda/ y les más valientes aun instalar `mamba`).
1. **Crear el entorno**. En el botón de inicio de Windows hay que ejecutar "Anaconda Prompt". Eso abrirá una consola. Allí deben ir a la carpeta del curso (recuerden los comandos `cd` y `dir`, o `ls` si están en GNU/Linux). En la carpeta raíz del repositorio hay un archivo llamado `environment.yml`. En la consola deben ejecutar:
```
conda env create -n grafica -f environment.yml
```
(si instalaron `mamba`, puede ser `mamba env create [...]`).
1. **Ejecutar hello world**. El siguiente comando activa el entorno:
```
conda activate grafica
```
El siguiente comando ejecuta un ejemplo:
```
python examples/hello_world/app.py
```
1. **Configurar tu editor favorito**. En mi caso utilizo VSCODE. Allí puedes descargar el repositorio directamente y también ejecutar los programas. Para ello, deben indicarle cuál es el entorno/intérprete de Python que utilizarán: hay que hacer clic en la esquina inferior derecha (donde dice “Python: gráfica [...]”) y elegir el entorno que acaban de instalar. Si estás en Windows, asegúrense de que el terminal por omisión sea `cmd.exe` y no _PowerShell_. Después pueden presionar el botón de _play_ en la esquina superior derecha. 
