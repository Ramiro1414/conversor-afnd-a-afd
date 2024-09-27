from graphviz import Digraph
import tkinter as tk
from tkinter import Label, Entry, Button
from PIL import Image, ImageTk
from include.logic import validar_cadena, cadena_con_transiciones_validas
from include.reader import parsear_tabla_transicion, obtener_datos_matriz, leer_csv

labelResultado = None

def renderAutomata(diccionario_estados_resultado, diccionario_transiciones_resultado):
    # Crear un grafo dirigido con Graphviz
    dot = Digraph()

    # Añadir nodos y aristas
    for estado, transiciones in diccionario_transiciones_resultado.items():
        # Verificar si el estado es aceptador
        if diccionario_estados_resultado.get(estado) == 1:
            dot.node(estado, shape='circle', style='filled', fillcolor='lightgreen')  # Estado aceptador en verde clarito
        else:
            dot.node(estado, shape='circle')  # Estado no aceptador

        # Añadir las aristas
        for transicion, destino in transiciones:
            if destino != '-':  # Evitar transiciones hacia el estado de error '-'
                dot.edge(estado, destino, label=transicion)  # Añadir las aristas con etiquetas

    # Renderizar el autómata
    dot.render('automata', format='png', view=False)

def iniciar_interfaz():
    # Crear ventana principal
    ventana = tk.Tk()
    ventana.title("Conversor AFND a AFD")
    ventana.geometry("800x400")  # Tamaño total de la ventana

    # Crear un frame para la parte izquierda (vacía por ahora)
    frame_izquierdo = tk.Frame(ventana, width=400, height=400, bg="white")
    frame_izquierdo.grid(row=0, column=0)

    # Generar el autómata y obtener la imagen
    ruta_imagen = "automata.png"

    # Mostrar la imagen en la parte derecha
    mostrar_imagen(ventana, ruta_imagen)

    # Crear widgets en el frame izquierdo
    # --- Campo para ingresar cadenas ---
    label_ingresar_cadena = Label(frame_izquierdo, text="Ingrese una cadena", fg="black", bg="white", font=("Arial", 20))
    label_ingresar_cadena.grid(row=0, column=0, padx=10, pady=10)
    campo_texto = Entry(frame_izquierdo, font=("Arial", 18))
    campo_texto.grid(row=1, column=0, padx=10, pady=10)

    # --- Boton para validar cadenas ---
    boton_validar = Button(frame_izquierdo, text="Validar", fg="blue", font=("Arial", 18), borderwidth=3, relief="solid", command=lambda: validar_cadena_interfaz(frame_izquierdo, campo_texto.get()))
    boton_validar.grid(row=2, column=0, padx=10, pady=10)

    # Iniciar el bucle principal de la interfaz
    ventana.mainloop()

def mostrar_imagen(ventana, ruta_imagen):
    # Cargar la imagen y redimensionarla para encajar en la mitad derecha de la ventana
    imagen = Image.open(ruta_imagen)
    imagen = imagen.resize((400, 400))  # Ajustar el tamaño según tus necesidades
    imagen_tk = ImageTk.PhotoImage(imagen)

    label_imagen = Label(ventana, image=imagen_tk)
    label_imagen.image = imagen_tk  # Necesario para evitar que se recoja la imagen por el garbage collector
    label_imagen.grid(row=0, column=1)  # Ubicar en la mitad derecha

def validar_cadena_interfaz(frame_izquierdo, cadena):
    global labelResultado
    

    matriz_csv = leer_csv("afd.csv")
    lista_transiciones, NULL, NULL = (
        obtener_datos_matriz(matriz_csv)
    )

    transition_dict = parsear_tabla_transicion("afd.csv", lista_transiciones)

    # Validamos si la cadena contiene caracteres validos (presentes en la lista de transiciones)
    if (not cadena_con_transiciones_validas(lista_transiciones, cadena)):
        resultado_texto = "Transicion no válida"
        resultado_color = "orange"
        
        if labelResultado:
            labelResultado.config(text=resultado_texto, fg=resultado_color)
        else:
            # Si no existe, crea un nuevo Label
            labelResultado = Label(frame_izquierdo, text=resultado_texto, fg=resultado_color, bg="white", font=("Arial", 14))
            labelResultado.grid(row=3, column=0, padx=50, pady=50)

        labelResultado.update()
        return

    if validar_cadena(transition_dict, lista_transiciones, cadena):
        resultado_texto = "Acepta"
        resultado_color = "green"
    else:
        resultado_texto = "No acepta"
        resultado_color = "red"
    
    # Si labelResultado ya existe, actualiza su texto y color
    if labelResultado:
        labelResultado.config(text=resultado_texto, fg=resultado_color)
    else:
        # Si no existe, crea un nuevo Label
        labelResultado = Label(frame_izquierdo, text=resultado_texto, fg=resultado_color, bg="white", font=("Arial", 14))
        labelResultado.grid(row=3, column=0, padx=50, pady=50)

    # Borra el Label anterior si existe (esto puede no ser necesario en todos los casos)
    # Aquí se asegura de que el Label sea visible y tenga el contenido correcto
    labelResultado.update()