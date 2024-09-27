import tkinter as tk
import csv
import os
from tkinter import Label, Entry, Button, Frame, messagebox
from PIL import Image, ImageTk
from include.logic import validar_cadena, cadena_con_transiciones_validas, transformar_automata_deterministico, eliminar_estados_inalcanzables
from include.reader import parsear_tabla_transicion, obtener_datos_matriz, leer_csv, cantidad_columnas_matriz
from include.utils import transicion_es_no_determinista, separar_estados
from graphviz import Digraph

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

class TablaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tabla Editable")
        self.table = []
        self.num_rows = 0
        self.num_cols = 0
        self.ventana_grafico = None  # Atributo para almacenar la ventana del gráfico

        # Crear el frame para la tabla
        self.table_frame = Frame(root)
        self.table_frame.grid(row=0, column=1, padx=10, pady=10)

        # Crear la tabla inicial
        self.create_table()

        # Crear el frame de validación
        self.validation_frame = Frame(root)
        self.validation_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        # Sección de validación de cadenas
        self.create_validation_section()

        # Botones para agregar filas, columnas, guardar y graficar
        self.add_row_button = Button(self.table_frame, text="Agregar Fila", command=self.add_row)
        self.add_col_button = Button(self.table_frame, text="Agregar Columna", command=self.add_col)
        self.save_button = Button(self.table_frame, text="Guardar como CSV", command=self.save_as_csv)
        self.eliminar_determinismo_button = Button(self.table_frame, text="Eliminar no determinismo", command=self.eliminar_determinismo)
        self.graficar_automata_button = Button(self.table_frame, text="Graficar Automata", command=self.graficar_automata)

        # Posicionar botones
        self.update_button_positions()

    def graficar_automata(self):
        """ Abre una nueva ventana para graficar el autómata """

        if (os.path.getsize('afd.csv') == 0):
            messagebox.showerror("Error", "Debe eliminar el no determinismo (si lo hay) para graficar el automata.")
            with open('afd.csv', 'w', newline='', encoding='utf-8') as file:
                pass

            return

        # Cerrar la ventana existente si está abierta
        if self.ventana_grafico is not None and self.ventana_grafico.winfo_exists():
            self.ventana_grafico.destroy()

        # Obtener los datos del autómata para graficar
        matriz_csv = leer_csv("afd.csv")
        lista_transiciones, diccionario_estados, diccionario_transiciones = obtener_datos_matriz(matriz_csv)

        # Renderizar el autómata
        renderAutomata(diccionario_estados, diccionario_transiciones)

        # Crear la nueva ventana
        self.ventana_grafico = tk.Toplevel(self.root)  # Asignar la ventana a un atributo
        self.ventana_grafico.title("Gráfico del Autómata")
        self.ventana_grafico.geometry("800x800")

        # Mostrar la imagen en la nueva ventana
        self.mostrar_imagen(self.ventana_grafico, "automata.png")
    
    def eliminar_determinismo(self):
        """ Elimina el determinismo del autómata y guarda el CSV """

        if (os.path.getsize('afnd.csv') == 0):
            messagebox.showerror("Error", "Debe crear la tabla de transicion antes de eliminar el no determinismo.")
            with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                pass

            return

        # Lógica para eliminar determinismo
        matriz_csv = leer_csv("afnd.csv")
        lista_transiciones, diccionario_estados, diccionario_transiciones = obtener_datos_matriz(matriz_csv)

        matriz_determinista = transformar_automata_deterministico(matriz_csv, lista_transiciones, diccionario_estados, diccionario_transiciones)

        nueva_matriz_determinista = eliminar_estados_inalcanzables(matriz_determinista, cantidad_columnas_matriz(matriz_determinista))

        # Guardar el nuevo CSV
        with open("afd.csv", mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_NONE, escapechar='\\')

            # Leer la primera línea del archivo afnd.csv
            with open("afnd.csv", mode="r", newline='', encoding="utf-8") as afnd_file:
                reader = csv.reader(afnd_file, delimiter=';')
                primera_linea = next(reader)  # Leer solo la primera línea

            # Escribir la primera línea en el archivo afd.csv
            writer.writerow(primera_linea)

            # Recorrer cada fila en la matriz
            for i in range(len(nueva_matriz_determinista)):
                # Recorrer cada elemento en la fila
                for j in range(len(nueva_matriz_determinista[i])):
                    # Si el elemento es una cadena vacía, reemplazarlo por '-'
                    if nueva_matriz_determinista[i][j] == '':
                        nueva_matriz_determinista[i][j] = '-'

            # Escribir las filas de la matriz
            for row in nueva_matriz_determinista:
                writer.writerow(row)
        
        print(nueva_matriz_determinista)

        messagebox.showinfo("OK", "No determinismo eliminado.")

    def create_table(self):
        """ Crea una tabla básica con 'δ' en la primera celda y 'F' en la última celda de la primera fila """
        for r in range(2):
            row = []
            for c in range(2):
                entry = Entry(self.table_frame)
                entry.grid(row=r, column=c, padx=5, pady=5)
                row.append(entry)
            self.table.append(row)

        # Poner el símbolo δ en la primera celda y F en la última de la primera fila
        self.table[0][0].insert(0, "d")
        self.table[0][-1].insert(0, "F")

        self.num_rows = 2
        self.num_cols = 2

    def update_button_positions(self):
        """ Actualiza la posición de los botones de agregar fila, columna y guardar CSV """
        self.add_row_button.grid(row=self.num_rows + 1, column=0, pady=10)
        self.add_col_button.grid(row=self.num_rows + 1, column=1, pady=10)
        self.save_button.grid(row=self.num_rows + 1, column=2, pady=10)
        self.eliminar_determinismo_button.grid(row=self.num_rows + 2, column=0, columnspan=3, pady=10)
        self.graficar_automata_button.grid(row=self.num_rows + 3, column=0, columnspan=3, pady=10)

    def add_col(self):
        """ Agrega una columna antes de la columna 'F' """
        self.num_cols += 1

        # Guardar los valores actuales de la columna "F" en todas las filas
        f_values = [self.table[r][-1].get() for r in range(self.num_rows)]

        # Insertar la nueva columna en todas las filas, antes de la columna 'F' (penúltima posición)
        for r in range(self.num_rows):
            entry = tk.Entry(self.table_frame)
            entry.grid(row=r, column=self.num_cols - 2, padx=5, pady=5)
            self.table[r].insert(self.num_cols - 2, entry)

        # Reinsertar la columna "F" con sus valores originales
        for r in range(self.num_rows):
            f_entry = tk.Entry(self.table_frame)
            f_entry.grid(row=r, column=self.num_cols - 1, padx=5, pady=5)
            f_entry.insert(0, f_values[r])  # Reinsertar el valor guardado de la columna "F"
            self.table[r][-1] = f_entry  # Reemplazar la celda con "F"

        # Actualizar la posición de los botones
        self.update_button_positions()

    def add_row(self):
        """ Agrega una fila a la tabla """
        self.num_rows += 1
        row = []
        for c in range(self.num_cols):
            entry = Entry(self.table_frame)
            entry.grid(row=self.num_rows - 1, column=c, padx=5, pady=5)
            row.append(entry)
        self.table.append(row)
        self.update_button_positions()  # Mueve los botones hacia abajo

    def save_as_csv(self):
        """ Guarda la tabla en un archivo CSV llamado 'afnd.csv' """

        with open("afnd.csv", mode="w", newline='', encoding="utf-8") as file:

            writer = csv.writer(file, delimiter=';')
            for row in self.table:
                writer.writerow([entry.get() for entry in row])

        self.clean_csv("afnd.csv", "afnd.csv")

    def clean_csv(self, input_file, output_file):
        """ Limpia el archivo CSV reemplazando múltiples ';' consecutivos por uno solo """
        with open(input_file, mode='r', encoding='utf-8') as file:
            lines = file.readlines()

        cleaned_lines = []
        for line in lines:
            cleaned_line = ';'.join([part for part in line.split(';') if part])  # Elimina elementos vacíos
            cleaned_lines.append(cleaned_line)

        with open(output_file, mode='w', encoding='utf-8') as file:
            file.writelines(cleaned_lines)

        lista_sin_nueva_linea = [elemento.strip() for elemento in cleaned_lines]
        
        # Convertir la lista a matriz
        matriz = [fila.split(';') for fila in lista_sin_nueva_linea]

        lista_transiciones_afnd = matriz[0]

        # Verifico cantidad de columnas de la tabla
        if len(lista_transiciones_afnd) <= 2:
            messagebox.showerror("Error", "Debe agregar al menos una columna de transicion.")
            with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                pass

            return
        else:
            # Verifico que las columnas de transiciones no contengan transiciones repetidas (ejemplo: dos transiciones son 'a' es un error)
            nueva_lista_transiciones_afnd = lista_transiciones_afnd[1:-1]
            elementos_vistos = set()  # Conjunto para almacenar elementos únicos
            repetidos = set()  # Conjunto para almacenar los elementos que se repiten

            for elemento in nueva_lista_transiciones_afnd:
                if elemento in elementos_vistos:
                    repetidos.add(elemento)  # Si ya está en el conjunto, es un repetido
                else:
                    elementos_vistos.add(elemento)  # Si no, agregarlo al conjunto
            
            if repetidos:
                messagebox.showerror("Error", "Transiciones repetidas.")
                with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                    pass

                return

        # Validar valores de la columna "F"
        for fila in matriz[1:]:  # No validamos la primera fila, ya que contiene encabezados
            valor = fila[-1]  # Última columna de cada fila
            if valor not in ['0', '1']:
                if valor == '':  # Verificar si está vacío
                    messagebox.showerror("Error", "Falta el valor en la última columna de una fila.")
                    with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                        pass

                    return
                else:
                    messagebox.showerror("Error", f"Valor no válido en la última columna: {valor}")
                    with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                        pass

                    return

        for i, fila in enumerate(matriz):
            if len(fila) < self.num_cols:
                messagebox.showerror("Error", "Faltan valores en las transiciones")
                with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                    pass

                return

        # Obtener los estados de la columna "d"
        estados = [fila[0] for fila in matriz[1:]]  # Ignorar la primera fila

        # Recorrer las demás columnas (menos la última que contiene "F")
        for fila in matriz[1:]:  # Ignorar la primera fila
            for estado in fila[1:-1]:  # Ignorar la última columna
                if estado not in estados:

                    if transicion_es_no_determinista(estado): # si la transicion es no determinista, es decir, formada por 2 o mas estados, todos los estados deben estar en la lista de estados
                        
                        lista_estados = separar_estados(estado)

                        for estado_separado in lista_estados:
                            
                            if estado_separado not in estados:
                                messagebox.showerror("Error", "Transicion con estado compuesto invalida.")
                                with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                                    pass  # No se escribe nada, el archivo se vacía

                                return  # Salir de la función si se encuentra un error
                    else:

                        if estado == '-':
                            continue
                        else:
                            # Si se encuentra un estado no válido, mostrar un mensaje de error
                            messagebox.showerror("Error", "Estado no valido en transicion.")
                            with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                                pass  # No se escribe nada, el archivo se vacía

                            return  # Salir de la función si se encuentra un error
        
        messagebox.showinfo("OK", "Tabla de transiciones creada.")

    def create_validation_section(self):
        """ Agrega la sección de validación de cadenas en la parte inferior del frame de validación """
        # --- Campo para ingresar cadenas ---
        self.label_ingresar_cadena = Label(self.validation_frame, text="Ingrese una cadena", fg="black", font=("Arial", 14))
        self.label_ingresar_cadena.grid(row=0, column=0, padx=10, pady=10)
        self.campo_texto = Entry(self.validation_frame, font=("Arial", 14))
        self.campo_texto.grid(row=0, column=1, padx=10, pady=10)

        # --- Boton para validar cadenas ---
        self.boton_validar = Button(self.validation_frame, text="Validar", fg="blue", font=("Arial", 14), command=self.validar_cadena_interfaz)
        self.boton_validar.grid(row=0, column=2, padx=10, pady=10)

    def mostrar_imagen(self, ventana, ruta_imagen):
        """ Muestra una imagen en la ventana dada """
        imagen = Image.open(ruta_imagen)
        imagen = imagen.resize((800, 800))  # Ajustar el tamaño según tus necesidades
        imagen_tk = ImageTk.PhotoImage(imagen)

        label_imagen = Label(ventana, image=imagen_tk)
        label_imagen.image = imagen_tk  # Necesario para evitar que se recoja la imagen por el garbage collector
        label_imagen.pack()

    def validar_cadena_interfaz(self):
        global labelResultado

        matriz_csv = leer_csv("afd.csv")
        lista_transiciones, NULL, NULL = (
            obtener_datos_matriz(matriz_csv)
        )

        transition_dict = parsear_tabla_transicion("afd.csv", lista_transiciones)

        # Validamos si la cadena contiene caracteres validos (presentes en la lista de transiciones)
        if (not cadena_con_transiciones_validas(lista_transiciones, self.campo_texto.get())):
            resultado_texto = "Transicion no válida"
            resultado_color = "orange"

            if labelResultado:
                labelResultado.config(text=resultado_texto, fg=resultado_color)
            else:
                # Si no existe, crea un nuevo Label
                labelResultado = Label(self.validation_frame, text=resultado_texto, fg=resultado_color, font=("Arial", 14))
                labelResultado.grid(row=1, column=0, columnspan=3)

            labelResultado.update()
            return

        if validar_cadena(transition_dict, lista_transiciones, self.campo_texto.get()):
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
            labelResultado = Label(self.validation_frame, text=resultado_texto, fg=resultado_color, font=("Arial", 14))
            labelResultado.grid(row=1, column=0, columnspan=3)

        labelResultado.update()

def iniciar_interfaz():

    def on_closing():
    # Mostrar un mensaje de confirmación antes de cerrar y borra el contenido de los archivos "afnd.csv" y "afd.csv"
        if (messagebox.askokcancel("Salir", "¿Seguro que quieres cerrar la aplicación?")):
            with open('afnd.csv', 'w', newline='', encoding='utf-8') as file:
                pass  # No se escribe nada, el archivo se vacía
            with open('afd.csv', 'w', newline='', encoding='utf-8') as file:
                pass  # No se escribe nada, el archivo se vacía
            root.destroy()  # Cierra la ventana principal

    # Crear ventana principal
    root = tk.Tk()
    TablaApp(root)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    iniciar_interfaz()