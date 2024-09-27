import re

def transicion_es_no_determinista(transicion):
    return "," in transicion

def separar_estados(transicion):
    return str(transicion).split(sep=',')

def formatear_transicion(transicion):
    if all(char == '-' for char in transicion):
        return '-'
    
    if '-' in transicion:
        cadena_sin_guiones = transicion.replace('-', ',')
        estados = sorted(set(cadena_sin_guiones.split(',')))  # Eliminar duplicados y ordenar
        result = ','.join([s for s in estados if s])
        return result

    estados = sorted(set(re.sub(r'(\d)(Q)', r'\1,\2', transicion).split(',')))  # Eliminar duplicados y ordenar
    return ','.join(estados)