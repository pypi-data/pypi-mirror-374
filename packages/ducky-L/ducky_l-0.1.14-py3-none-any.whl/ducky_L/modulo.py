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

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import shutil

def LSL(html_file, static_dir="static", port=8000):
    app = FastAPI()

    # Monta la carpeta de archivos estáticos si existe
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # Ruta principal
    @app.get("/")
    def home():
        html_path = os.path.join(os.path.dirname(__file__), html_file)
        return FileResponse(html_path)


    # Levanta el servidor
    uvicorn.run(app, host="0.0.0.0", port=port)
