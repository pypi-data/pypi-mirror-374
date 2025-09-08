import string, random
variables = {}

def poner(texto):
    if texto.startswith("*") and texto.endswith("*"):
        nombre_var = texto[1:-1]
        print(variables.get(nombre_var, f"$variable {nombre_var} no definida$"))
    else:
        print(texto)

def variable(nombre, valor):
    variables[nombre] = valor

def bucle(accion=None, condicion=None, n=None):
    if n is not None:
        for _ in range(n):
            accion()
    elif condicion is not None:
        while condicion():
            accion()
def si(condicion, hacer=None, condicion2=None, hacer2=None, sino=None):
    if condicion():
        hacer()
    elif condicion2():
        hacer2()
    else:
        sino()

def consola_nor(texto=None):
    input(f"$ {texto}")

def consola_var(texto=None, nombre_var=None):
    valor = input(f"$ {texto} ")
    if nombre_var:
        variables[nombre_var] = valor
    else:
        pass
    return valor

import os
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn


def LSL(html_file, static_dir="static", port=8000):
    app = FastAPI()

    # Monta la carpeta de archivos estáticos si existe
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Ruta principal
    @app.get("/")
    def home():
        # Usa os.path.abspath para obtener la ruta absoluta del archivo HTML
        # Esto asegura que el archivo se encuentre en la carpeta de ejecución
        html_path = os.path.abspath(html_file)
        return FileResponse(html_path)

    # Levanta el servidor
    uvicorn.run(app, host="0.0.0.0", port=port)

def password(length=10):
    elementos = string.ascii_letters + string.digits + string.ascii_uppercase + string.ascii_lowercase
    password = ""

    for _ in range(length):
        password += random.choice(elementos)
    print(password)

import datetime
def hora():
    hora = datetime.datetime.now()
    return hora

from pathlib import Path

def CC(carpeta):
    ruta = Path(carpeta)
    ruta.mkdir(parents=True, exist_ok=True)

def CA(archivo):
    with open(archivo, 'w') as archivo:
        print(f"El archivo '{archivo}' ha sido creado")