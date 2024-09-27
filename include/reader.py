import csv

def leer_csv(directorio_archivo):
    with open(directorio_archivo, 'r') as archivo_csv:
        lector_csv = csv.reader(archivo_csv, delimiter=';')
        matriz = [fila for fila in lector_csv]
    return matriz

def cantidad_filas_matriz(matriz):
    return len(matriz)

def cantidad_columnas_matriz(matriz):
    return len(matriz[0]) if cantidad_filas_matriz(matriz) > 0 else 0

def obtener_datos_matriz(matriz):
    filas = cantidad_filas_matriz(matriz)
    columnas = cantidad_columnas_matriz(matriz)
    lista_transiciones = []
    diccionario_estados = {}
    diccionario_transiciones = {}

    for i in range(1, columnas-1):
        lista_transiciones.append(matriz[0][i])
                
    for i in range(1, filas):
        diccionario_estados[matriz[i][0]] = int(matriz[i][columnas-1])

    for i in range(1, filas):
        transiciones_de_un_estado = []
        for j in range(1, columnas-1):
            transiciones_de_un_estado.append( (lista_transiciones[j-1], matriz[i][j]) )
        diccionario_transiciones[matriz[i][0]] = transiciones_de_un_estado

    return lista_transiciones, diccionario_estados, diccionario_transiciones

def parsear_tabla_transicion(nombreArchivo, lista_transiciones):
    transition_dict = {}
    # Definir la lista de transiciones
    transiciones = lista_transiciones

    with open(nombreArchivo, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            state = row['d']
            # Construir el diccionario de transiciones dinámicamente
            transitions = {trans: row[trans] for trans in transiciones}
            is_accepting = row['F'] == '1'
            transition_dict[state] = {
                'transitions': transitions,
                'is_accepting': is_accepting
            }
    return transition_dict