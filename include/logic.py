from .utils import separar_estados, formatear_transicion, transicion_es_no_determinista
from .reader import cantidad_columnas_matriz

def union_estados_transiciones(estado_compuesto, transiciones, diccionario_transiciones):
    lista_estados = separar_estados(estado_compuesto)
    result = []

    nueva_lista_estados = [item for item in lista_estados if item != ''] # elimina los estados '' (vacios)

    for transicion in transiciones:
        nuevaTransicion = ""

        for estado in nueva_lista_estados:
            lista_tuplas_transiciones = diccionario_transiciones[estado]

            for t, q in lista_tuplas_transiciones: # t = transicion, q = estado
                if t == transicion:
                    nuevaTransicion += q + "," # se le concatena una coma (",") Luego el metodo de formatear transicion elimina la coma del final
                    break

        result.append((transicion, formatear_transicion(nuevaTransicion)))

    return result

def transformar_automata_deterministico(matriz, lista_transiciones, diccionario_estados, diccionario_transiciones):
    columnas = cantidad_columnas_matriz(matriz)
    matriz_output = [fila.copy() for fila in matriz]
    estados_procesados = {fila[0] for fila in matriz_output}

    i = 1
    while i < len(matriz_output):
        for j in range(1, columnas-1):
            estado_actual = matriz_output[i][j]
            if transicion_es_no_determinista(estado_actual):
                result = union_estados_transiciones(estado_actual, lista_transiciones, diccionario_transiciones)
                nuevo_estado_compuesto = ",".join(sorted(separar_estados(estado_actual)))

                if nuevo_estado_compuesto not in estados_procesados:
                    nuevoEstado = [formatear_transicion(nuevo_estado_compuesto)]
                    nuevoEstado.append(result[0][1])
                    nuevoEstado.append(result[1][1])

                    F = any(diccionario_estados[estado] for estado in separar_estados(nuevo_estado_compuesto) if estado != '')
                    nuevoEstado.append(int(F))

                    nuevoEstadoFixed = [item[1:] if isinstance(item, str) and item.startswith(',') else item for item in nuevoEstado] # Corrige error de tener una "," al principio

                    matriz_output.append(nuevoEstadoFixed)
                    estados_procesados.add(nuevo_estado_compuesto)

        i += 1

    return matriz_output

def eliminar_estados_inalcanzables(matriz_output, columnas):
    estado_inicial = matriz_output[1][0]
    alcanzables = set()
    alcanzables.add(estado_inicial)

    # Cola para realizar un recorrido en amplitud (BFS) desde el estado inicial
    cola = [estado_inicial]

    while cola:
        estado_actual = cola.pop(0)
    
        # Busca las transiciones desde este estado
        for i in range(1, len(matriz_output)):
            if matriz_output[i][0] == estado_actual:
                for j in range(1, columnas-1):
                    estado_siguiente = matriz_output[i][j]
                    # Si el estado de destino no ha sido visitado, lo añadimos a la cola
                    if estado_siguiente not in alcanzables and estado_siguiente != '':
                        alcanzables.add(estado_siguiente)
                        cola.append(estado_siguiente)

    # Crear una nueva matriz que solo contenga los estados alcanzables
    nueva_matriz_output = []

    for i in range(1, len(matriz_output)):
        if matriz_output[i][0] in alcanzables:
            nueva_matriz_output.append(matriz_output[i])
        else:
            print("\nEliminando estado inalcanzable: ", matriz_output[i][0])

    # Reemplazamos matriz_output con la nueva matriz
    return nueva_matriz_output

def validar_cadena(transition_dict, lista_transiciones, input_string):
    current_state = 'Q0'  # Suponiendo que Q0 es el estado inicial
    
    if (input_string == 'λ' or input_string == ''): # valida si acepta cadena vacia o no
        if (transition_dict['Q0'].get('is_accepting')): 
            return True
        return False

    for char in input_string:
        if char not in lista_transiciones:
            raise ValueError("Invalid input character")
        
        if current_state not in transition_dict:
            return False  # Estado no definido en la tabla
        
        transitions = transition_dict[current_state]['transitions']
        next_state = transitions.get(char, '-') # busca el siguiente estado, si no tiene siguiente estado devuelve "-", por lo que no acepta
        
        if next_state == '-':
            return False  # Transición inválida
        
        current_state = next_state
    
    return transition_dict.get(current_state, {}).get('is_accepting', False)

def cadena_con_transiciones_validas(lista_transiciones, cadena):
    for char in cadena:
        if char not in lista_transiciones:
            return False
    return True