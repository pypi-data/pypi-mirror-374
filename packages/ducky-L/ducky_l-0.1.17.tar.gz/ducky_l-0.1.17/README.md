duckyL es una libreria/lenguaje que sirve para codigo en español
´´´
poner("text") <-- entre comillas el texto

variable("pato", "algo") <-- el primer parametro es el nmbre de la variable y el segundo el valor de la variable

poner("*pato*") <-- entre * se pondra cuando se llama una variable

variables["pato"] <--- es llamar una variable

si(variables["pato"] == "algo", lambda: poner("pato"), None, None) <-- el si() tiene 4 parametros: el if elif y else (solo 1 para cada uno) se usan los lambdas: algo, para poner que  se hara, el pimer parametro sera para la condicion, segundo para if, tercero elif y cuarto else

bucle(2, lambda: poner("pao")) <-- habran 3 parametros: accion, conndicion, cantidad, la acciones lo que se va a hacer, la condicion es porque se ejecuta (si no hay se puede poner None) y cantidad que sera las veses que se repita

consola_nor("texto: ") <-- sera para poner texto en la consola como un input

consola_var("texto: ", "2") <-- sera para poder crear una variable que se llame como se ponga en el segundo parametro y su valor sera el que se ponga en la consola 

LSL(index.html, "static", port=8000) <-- esto es para poder levantar un servidor local, en el primer argumento se pone el index.html (en la misma carpeta) en el segundo se pone la carpeta donde estan los archivos css y js y el ultiumo se pone el puerto
´´´
A todos los parametros que no se usan se puede poner None