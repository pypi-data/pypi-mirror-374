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
