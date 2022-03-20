|
Instalación de python y librerias en OS X
=======

Primero hay que revisar si su sistema tiene python3 instalado, para esto abra su terminal

Ejecute ``python`` o ``python3``. Si la respuesta es algo del tipo:

    Python 3.6.6 (default, Sep 12 2018, 18:26:19)
    [GCC 8.0.1 20180414 (experimental) [trunk revision 259383]] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>>

y la numeración de python es 3.6 o superior, felicidades, usted ya tiene python 3 instalado.

Si la numeración indica python 2.7.x o similar, o el comando python3 no es encontrado, usted necesita instalar python 3.

El símbolo >>> indica el lugar donde usted puede enviar comandos al intérprete de python. Ejecutando quit() usted cierra dicho intérprete.

Instalación de Brew
---------------------

Primero hay que revisar si ``brew`` esta instalado, para esto abra su terminal

Ejecute ``brew``. Si la respuesta es algo de este tipo:

    Example usage:
      brew search TEXT|/REGEX/
      brew info [FORMULA|CASK...]
      brew install FORMULA|CASK...
      brew update
      brew upgrade [FORMULA|CASK...]
      brew uninstall FORMULA|CASK...
      brew list [FORMULA|CASK...]

    Troubleshooting:
      brew config
      brew doctor
      brew install --verbose --debug FORMULA|CASK

    Contributing:
      brew create URL [--no-fetch]
      brew edit [FORMULA|CASK...]

    Further help:
      brew commands
      brew help [COMMAND]
      man brew
      https://docs.brew.sh

Entonces ``brew`` esta instalado.

En caso de no estar instalado Para instalar ``brew`` se pueden seguir las instrucciones en [https://brew.sh](https://brew.sh).

Instalación de python3
----------------------

En la terminal ejecute:

    brew install python3

Se le pedirá su contraseña de sistema, ingrésela y luego ingrese 'y' o 's' para comenzar la instalación.

Creando un environment
----------------------

Existen múltiples librerías para python. Algunas incompatibles entre si debido a distintos requerimientos de versiones. Es posible crear distintos ambientes de trabajo para tener ejecutables de python con distintas librerías específicas según sea el caso. Se recomienda instalar todas las librerías para el curso en un environment dedicado. Así no interfiere con pythons que pueda utilizar para otros fines.

Luego cree un ambiente de python una carpeta de su home con ~/python-cg (puede utilizar otra ruta si lo desea).

    python3 -m venv ~/python-cg

Si no funciona puede crear directamente la carpeta con el environment, ejecutando

    python3 -m venv python-cg

Instalando librerías
--------------------

Primero active su environment python3 con

    source ~/python-cg/bin/activate

Aparecerá (python-cg) al lado izquierdo de su prompt, indicando que dicho environment se encuentra activo.

Puede probar que la versión de python activa es la que se encuentra en su environment con

    which python

La respuesta debiera ser

    /home/[username]/python-cg/bin/python

También verifique pip, con:

    which pip

La respuesta debiera ser

    /home/[username]/python-cg/bin/pip

Instalemos algunas dependencias necesarias:

    brew install glfw

Ahora instalamos todas las librerias python requeridas

    pip install numpy scipy matplotlib ipython jupyter pyopengl glfw pillow

Siempre es posible instalar cada librería por separado.

Arreglar glfw
--------------------

Para que todos los programas corran correctamente debera agregar el siguiente bloque de codigo en la linea 1180

    [ 1174 ] """
    [ 1175 ] Creates a window and its associated context.
    [ 1176 ]
    [ 1177 ] Wrapper for:
    [ 1178 ]     GLFWwindow* glfwCreateWindow(int width, int height, const char* title, GLFWmonitor* monitor, GLFWwindow* share);
    [ 1179 ] """
    # Agregar esto:
    [ 1180 ] window_hint(CONTEXT_VERSION_MAJOR, 3)
    [ 1181 ] window_hint(CONTEXT_VERSION_MINOR, 3)
    [ 1182 ] window_hint(OPENGL_FORWARD_COMPAT, True)
    [ 1183 ] window_hint(OPENGL_PROFILE, OPENGL_CORE_PROFILE)

al archivo ~/pythoncg/lib/python3.9/site-packages/glfw/\_\_init\_\_.py
