# Conversor de AFND a AFD
Este programa transforma un autómata finito no determinístico, que el usuario ingresa a través de una matriz de transición, en un autómata finito determinístico.

Autores:
* Ramiro Parra
* Alan Kalevich
* Matias Casteglione

## Instalación

1. Clonar el repositorio.

`git clone https://github.com/Ramiro1414/conversor-afnd-a-afd.git`

2. Cambiar al directorio del repositorio clonado.

`cd conversor-afnd-a-afd/`

3. Crear un nuevo entorno virtual.

`python3 -m venv fundamentos`

4. Activar el entorno virtual.

    Para **Linux**: `source fundamentos/bin/activate`

    Para **Windows**: `fundamentos\Scripts\activate`

5. Instalar las dependencias necesarias.

`pip install -r requirements.txt`

6. Ejecutar el programa.

`python3 main.py`