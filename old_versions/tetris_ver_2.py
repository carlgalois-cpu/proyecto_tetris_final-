import tkinter as tk
from tkinter import messagebox
import random
import json
import time

# =============================================
# CONFIGURACIÓN INICIAL Y CONSTANTES
# =============================================

def configurar_constantes():
    """Define todas las constantes del juego"""
    constantes = {
        'TABLERO_ANCHO': 10,
        'TABLERO_ALTO': 20,
        'TAMANO_BLOQUE': 30,
        
        'VELOCIDAD_BASE': 500,
        'VELOCIDAD_MINIMA': 100,
        'REDUCCION_VELOCIDAD': 40,
        
        'PUNTUACION_LINEAS': {
            1: 100,
            2: 300, 
            3: 500,
            4: 800
        },
        
        'COLORES_PIEZAS': [
            "#1a1a1a",  # Vacío
            "#00f0f0",  # I
            "#f0f000",  # O  
            "#a000f0",  # T
            "#00f000",  # S
            "#f00000",  # Z
            "#0000f0",  # J
            "#f0a000"   # L
        ],
        
        'FORMAS_PIEZAS': [
            [], # 0. Vacío
            # I
            [[[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]], 
             [[0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,0,0]]],
            # O
            [[[2,2], [2,2]]],
            # T
            [[[0,3,0], [3,3,3], [0,0,0]], 
             [[0,3,0], [0,3,3], [0,3,0]], 
             [[0,0,0], [3,3,3], [0,3,0]], 
             [[0,3,0], [3,3,0], [0,3,0]]],
            # S
            [[[0,4,4], [4,4,0], [0,0,0]], 
             [[0,4,0], [0,4,4], [0,0,4]]],
            # Z
            [[[5,5,0], [0,5,5], [0,0,0]], 
             [[0,0,5], [0,5,5], [0,5,0]]],
            # J
            [[[6,0,0], [6,6,6], [0,0,0]], 
             [[0,6,6], [0,6,0], [0,6,0]], 
             [[0,0,0], [6,6,6], [0,0,6]], 
             [[0,6,0], [0,6,0], [6,6,0]]],
            # L
            [[[0,0,7], [7,7,7], [0,0,0]], 
             [[0,7,0], [0,7,0], [0,7,7]], 
             [[0,0,0], [7,7,7], [7,0,0]], 
             [[7,7,0], [0,7,0], [0,7,0]]]
        ],
        
        'ARCHIVO_RECORD': "tetris_record.json"
    }
    return constantes

# =============================================
# PERSISTENCIA DE DATOS
# =============================================

def cargar_datos(archivo):
    """Carga el récord desde archivo JSON"""
    try:
        with open(archivo, 'r') as f:
            datos = json.load(f)
            return datos.get('record', 0)
    except FileNotFoundError:
        # Si el archivo no existe, crear uno con record 0
        guardar_datos(archivo, 0)
        return 0
    except json.JSONDecodeError:
        messagebox.showerror("Error", "El archivo de récord está corrupto")
        return 0

def guardar_datos(archivo, record):
    """Guarda el récord en archivo JSON"""
    try:
        datos = {'record': record}
        with open(archivo, 'w') as f:
            json.dump(datos, f)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo guardar el récord: {e}")
        return False

# =============================================
# LÓGICA DEL JUEGO
# =============================================

def crear_tablero_vacio(ancho, alto):
    """Crea un tablero vacío lleno de ceros"""
    tablero = []
    for fila in range(alto):
        fila_vacia = []
        for columna in range(ancho):
            fila_vacia.append(0)
        tablero.append(fila_vacia)
    return tablero

def generar_pieza_aleatoria():
    """Genera una nueva pieza aleatoria"""
    tipo_pieza = random.randint(1, 7)  # Del 1 al 7 (0 es vacío)
    return {
        'tipo': tipo_pieza,
        'rotacion': 0,
        'x': 4,  # Posición inicial centrada
        'y': 0
    }

def obtener_forma_pieza(pieza, formas):
    """Obtiene la forma actual de la pieza basada en su rotación"""
    if not pieza:
        return []
    tipo = pieza['tipo']
    rotacion = pieza['rotacion']
    return formas[tipo][rotacion]

def verificar_colision(tablero, forma, pos_x, pos_y, ancho_tablero, alto_tablero):
    """Verifica si la pieza colisiona con paredes, suelo u otras piezas"""
    for fila in range(len(forma)):
        for columna in range(len(forma[fila])):
            if forma[fila][columna] != 0:
                # Calcular posición en el tablero
                tablero_x = pos_x + columna
                tablero_y = pos_y + fila
                
                # Verificar límites
                if tablero_x < 0 or tablero_x >= ancho_tablero:
                    return True
                if tablero_y >= alto_tablero:
                    return True
                # Verificar otras piezas (solo si está dentro del tablero)
                if tablero_y >= 0 and tablero[tablero_y][tablero_x] != 0:
                    return True
    return False

def fijar_pieza_en_tablero(tablero, pieza, formas):
    """Fija la pieza actual en el tablero"""
    forma = obtener_forma_pieza(pieza, formas)
    tipo_pieza = pieza['tipo']
    
    for fila in range(len(forma)):
        for columna in range(len(forma[fila])):
            if forma[fila][columna] != 0:
                pos_y = pieza['y'] + fila
                pos_x = pieca['x'] + columna
                if pos_y >= 0:  # Solo fijar si está dentro del tablero visible
                    tablero[pos_y][pos_x] = tipo_pieza

def limpiar_lineas_completas(tablero, ancho):
    """Elimina líneas completas y devuelve cuántas se limpiaron"""
    lineas_limpias = 0
    fila = len(tablero) - 1
    
    while fila >= 0:
        # Verificar si la línea está completa
        linea_completa = True
        for columna in range(ancho):
            if tablero[fila][columna] == 0:
                linea_completa = False
                break
        
        if linea_completa:
            # Eliminar la línea completa
            del tablero[fila]
            # Añadir nueva línea vacía al principio
            tablero.insert(0, [0 for _ in range(ancho)])
            lineas_limpias += 1
        else:
            fila -= 1
    
    return lineas_limpias

def calcular_puntuacion(lineas_limpias, nivel, sistema_puntuacion):
    """Calcula la puntuación basada en líneas limpiadas y nivel"""
    if lineas_limpias == 0:
        return 0
    
    puntos_base = sistema_puntuacion.get(lineas_limpias, 0)
    return puntos_base * nivel

def actualizar_nivel(lineas_totales):
    """Calcula el nivel basado en líneas totales limpiadas"""
    return (lineas_totales // 10) + 1

def calcular_velocidad(nivel, velocidad_base, velocidad_minima, reduccion):
    """Calcula la velocidad de caída basada en el nivel"""
    velocidad = velocidad_base - ((nivel - 1) * reduccion)
    if velocidad < velocidad_minima:
        return velocidad_minima
    return velocidad

# =============================================
# INTERFAZ GRÁFICA
# =============================================

def crear_ventana_principal(constantes):
    """Crea y configura la ventana principal del juego"""
    ancho_juego = constantes['TABLERO_ANCHO'] * constantes['TAMANO_BLOQUE']
    alto_juego = constantes['TABLERO_ALTO'] * constantes['TAMANO_BLOQUE']
    ancho_ventana = ancho_juego + 200  # Espacio para panel lateral
    
    ventana = tk.Tk()
    ventana.title("Tetris - Versión 2")
    ventana.resizable(False, False)
    ventana.geometry(f"{ancho_ventana}x{alto_juego}")
    
    return ventana

def crear_lienzo_juego(ventana, constantes):
    """Crea el lienzo donde se dibuja el juego"""
    ancho = constantes['TABLERO_ANCHO'] * constantes['TAMANO_BLOQUE']
    alto = constantes['TABLERO_ALTO'] * constantes['TAMANO_BLOQUE']
    
    lienzo = tk.Canvas(
        ventana, 
        width=ancho, 
        height=alto, 
        bg="#1a1a1a",
        highlightthickness=0
    )
    return lienzo

def crear_panel_informacion(ventana):
    """Crea el panel lateral con información del juego"""
    panel = tk.Frame(ventana, width=200, bg="#2c2c2c")
    panel.pack(side=tk.RIGHT, fill=tk.Y)
    panel.pack_propagate(False)
    return panel

def crear_etiquetas_informacion(panel):
    """Crea las etiquetas para mostrar información del juego"""
    # Título
    titulo = tk.Label(
        panel, 
        text="TETRIS", 
        font=("Arial", 20, "bold"), 
        fg="white", 
        bg="#2c2c2c"
    )
    titulo.pack(pady=10)
    
    # Récord
    etiqueta_record = tk.Label(
        panel,
        text="Récord:\n0",
        font=("Arial", 14),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_record.pack(pady=10)
    
    # Puntuación
    etiqueta_puntuacion = tk.Label(
        panel,
        text="Puntuación:\n0",
        font=("Arial", 14),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_puntuacion.pack(pady=10)
    
    # Nivel
    etiqueta_nivel = tk.Label(
        panel,
        text="Nivel:\n1",
        font=("Arial", 14),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_nivel.pack(pady=10)
    
    # Líneas
    etiqueta_lineas = tk.Label(
        panel,
        text="Líneas:\n0",
        font=("Arial", 14),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_lineas.pack(pady=10)
    
    # Controles
    controles_texto = """
Controles:
← → : Mover
↑ : Rotar
↓ : Bajar rápido
Espacio: Caída rápida
P : Pausa
R : Reiniciar
    """
    etiqueta_controles = tk.Label(
        panel,
        text=controles_texto,
        font=("Arial", 10),
        fg="lightgray",
        bg="#2c2c2c",
        justify=tk.LEFT
    )
    etiqueta_controles.pack(pady=20)
    
    return {
        'record': etiqueta_record,
        'puntuacion': etiqueta_puntuacion,
        'nivel': etiqueta_nivel,
        'lineas': etiqueta_lineas
    }

def dibujar_tablero(lienzo, tablero, constantes):
    """Dibuja el tablero en el lienzo"""
    tamano_bloque = constantes['TAMANO_BLOQUE']
    colores = constantes['COLORES_PIEZAS']
    
    for fila in range(len(tablero)):
        for columna in range(len(tablero[fila])):
            tipo_pieza = tablero[fila][columna]
            color = colores[tipo_pieza]
            
            x1 = columna * tamano_bloque
            y1 = fila * tamano_bloque
            x2 = x1 + tamano_bloque
            y2 = y1 + tamano_bloque
            
            lienzo.create_rectangle(x1, y1, x2, y2, fill=color, outline="#404040")

def dibujar_pieza_actual(lienzo, pieza, constantes):
    """Dibuja la pieza actual en el lienzo"""
    if not pieza:
        return
    
    formas = constantes['FORMAS_PIEZAS']
    colores = constantes['COLORES_PIEZAS']
    tamano_bloque = constantes['TAMANO_BLOQUE']
    
    forma = obtener_forma_pieza(pieza, formas)
    color = colores[pieza['tipo']]
    
    for fila in range(len(forma)):
        for columna in range(len(forma[fila])):
            if forma[fila][columna] != 0:
                x = (pieza['x'] + columna) * tamano_bloque
                y = (pieza['y'] + fila) * tamano_bloque
                
                if y >= 0:  # Solo dibujar si está en el área visible
                    lienzo.create_rectangle(
                        x, y,
                        x + tamano_bloque, y + tamano_bloque,
                        fill=color, outline="white"
                    )

def dibujar_cuadricula(lienzo, constantes):
    """Dibuja la cuadrícula del tablero"""
    ancho = constantes['TABLERO_ANCHO'] * constantes['TAMANO_BLOQUE']
    alto = constantes['TABLERO_ALTO'] * constantes['TAMANO_BLOQUE']
    tamano_bloque = constantes['TAMANO_BLOQUE']
    
    # Líneas verticales
    for x in range(0, ancho + 1, tamano_bloque):
        lienzo.create_line(x, 0, x, alto, fill="#404040")
    
    # Líneas horizontales
    for y in range(0, alto + 1, tamano_bloque):
        lienzo.create_line(0, y, ancho, y, fill="#404040")

def actualizar_interfaz(lienzo, tablero, pieza_actual, constantes, etiquetas, estado):
    """Actualiza toda la interfaz gráfica"""
    lienzo.delete("all")
    
    dibujar_tablero(lienzo, tablero, constantes)
    dibujar_pieza_actual(lienzo, pieza_actual, constantes)
    dibujar_cuadricula(lienzo, constantes)
    
    # Actualizar etiquetas de información
    etiquetas['puntuacion'].config(text=f"Puntuación:\n{estado['puntuacion']}")
    etiquetas['nivel'].config(text=f"Nivel:\n{estado['nivel']}")
    etiquetas['lineas'].config(text=f"Líneas:\n{estado['lineas_totales']}")
    etiquetas['record'].config(text=f"Récord:\n{estado['record']}")

def mostrar_mensaje_juego_terminado(lienzo, constantes):
    """Muestra mensaje de juego terminado"""
    ancho = constantes['TABLERO_ANCHO'] * constantes['TAMANO_BLOQUE']
    alto = constantes['TABLERO_ALTO'] * constantes['TAMANO_BLOQUE']
    
    lienzo.create_rectangle(
        ancho/4, alto/3,
        3*ancho/4, 2*alto/3,
        fill="black", outline="white"
    )
    lienzo.create_text(
        ancho/2, alto/2,
        text="JUEGO TERMINADO",
        font=("Arial", 20, "bold"),
        fill="red"
    )

def mostrar_mensaje_pausa(lienzo, constantes):
    """Muestra mensaje de pausa"""
    ancho = constantes['TABLERO_ANCHO'] * constantes['TAMANO_BLOQUE']
    alto = constantes['TABLERO_ALTO'] * constantes['TAMANO_BLOQUE']
    
    lienzo.create_text(
        ancho/2, alto/2,
        text="PAUSADO",
        font=("Arial", 30, "bold"),
        fill="white"
    )

# =============================================
# CONTROLADORES DE EVENTOS
# =============================================

def manejar_movimiento_izquierda(estado, constantes):
    """Maneja el movimiento hacia la izquierda"""
    if estado['juego_terminado'] or estado['pausado']:
        return
    
    pieza = estado['pieza_actual']
    if not pieza:
        return
    
    formas = constantes['FORMAS_PIEZAS']
    forma_actual = obtener_forma_pieza(pieza, formas)
    
    nueva_x = pieza['x'] - 1
    if not verificar_colision(
        estado['tablero'], forma_actual, nueva_x, pieza['y'],
        constantes['TABLERO_ANCHO'], constantes['TABLERO_ALTO']
    ):
        pieza['x'] = nueva_x

def manejar_movimiento_derecha(estado, constantes):
    """Maneja el movimiento hacia la derecha"""
    if estado['juego_terminado'] or estado['pausado']:
        return
    
    pieza = estado['pieza_actual']
    if not pieza:
        return
    
    formas = constantes['FORMAS_PIEZAS']
    forma_actual = obtener_forma_pieza(pieza, formas)
    
    nueva_x = pieza['x'] + 1
    if not verificar_colision(
        estado['tablero'], forma_actual, nueva_x, pieza['y'],
        constantes['TABLERO_ANCHO'], constantes['TABLERO_ALTO']
    ):
        pieza['x'] = nueva_x

def manejar_rotacion(estado, constantes):
    """Maneja la rotación de la pieza"""
    if estado['juego_terminado'] or estado['pausado']:
        return
    
    pieza = estado['pieza_actual']
    if not pieza:
        return
    
    formas = constantes['FORMAS_PIEZAS']
    tipo_pieza = pieza['tipo']
    rotaciones_disponibles = len(formas[tipo_pieza])
    
    nueva_rotacion = (pieza['rotacion'] + 1) % rotaciones_disponibles
    nueva_forma = formas[tipo_pieza][nueva_rotacion]
    
    # Verificar si la nueva rotación es válida
    if not verificar_colision(
        estado['tablero'], nueva_forma, pieza['x'], pieza['y'],
        constantes['TABLERO_ANCHO'], constantes['TABLERO_ALTO']
    ):
        pieza['rotacion'] = nueva_rotacion

def manejar_caida_rapida(estado, constantes):
    """Maneja la caída rápida de la pieza"""
    if estado['juego_terminado'] or estado['pausado']:
        return
    
    pieza = estado['pieza_actual']
    if not pieza:
        return
    
    formas = constantes['FORMAS_PIEZAS']
    forma_actual = obtener_forma_pieza(pieza, formas)
    
    nueva_y = pieza['y'] + 1
    if not verificar_colision(
        estado['tablero'], forma_actual, pieza['x'], nueva_y,
        constantes['TABLERO_ANCHO'], constantes['TABLERO_ALTO']
    ):
        pieza['y'] = nueva_y
        # Bonus por caída rápida
        estado['puntuacion'] += 1

def manejar_caida_instantanea(estado, constantes):
    """Maneja la caída instantánea de la pieza"""
    if estado['juego_terminado'] or estado['pausado']:
        return
    
    pieza = estado['pieza_actual']
    if not pieza:
        return
    
    formas = constantes['FORMAS_PIEZAS']
    forma_actual = obtener_forma_pieza(pieza, formas)
    
    # Encontrar la posición más baja posible
    y_actual = pieza['y']
    while not verificar_colision(
        estado['tablero'], forma_actual, pieza['x'], y_actual + 1,
        constantes['TABLERO_ANCHO'], constantes['TABLERO_ALTO']
    ):
        y_actual += 1
    
    pieza['y'] = y_actual
    # Forzar la fijación de la pieza
    fijar_pieza_y_continuar(estado, constantes)

def manejar_pausa(estado, lienzo, constantes):
    """Maneja la pausa del juego"""
    if estado['juego_terminado']:
        return
    
    estado['pausado'] = not estado['pausado']
    
    if estado['pausado']:
        mostrar_mensaje_pausa(lienzo, constantes)

def manejar_reinicio(estado, constantes):
    """Reinicia el juego"""
    estado['tablero'] = crear_tablero_vacio(
        constantes['TABLERO_ANCHO'], 
        constantes['TABLERO_ALTO']
    )
    estado['pieza_actual'] = generar_pieza_aleatoria()
    estado['puntuacion'] = 0
    estado['nivel'] = 1
    estado['lineas_totales'] = 0
    estado['juego_terminado'] = False
    estado['pausado'] = False

def configurar_controles(ventana, estado, constantes, lienzo):
    """Configura los controles del teclado"""
    def evento_tecla(event):
        if event.keysym == 'Left':
            manejar_movimiento_izquierda(estado, constantes)
        elif event.keysym == 'Right':
            manejar_movimiento_derecha(estado, constantes)
        elif event.keysym == 'Up':
            manejar_rotacion(estado, constantes)
        elif event.keysym == 'Down':
            manejar_caida_rapida(estado, constantes)
        elif event.keysym == 'space':
            manejar_caida_instantanea(estado, constantes)
        elif event.keysym == 'p':
            manejar_pausa(estado, lienzo, constantes)
        elif event.keysym == 'r':
            manejar_reinicio(estado, constantes)
    
    ventana.bind('<KeyPress>', evento_tecla)
    ventana.focus_set()

# =============================================
# LÓGICA PRINCIPAL DEL JUEGO
# =============================================

def fijar_pieza_y_continuar(estado, constantes):
    """Fija la pieza actual y prepara la siguiente"""
    # Fijar pieza en el tablero
    fijar_pieza_en_tablero(
        estado['tablero'], 
        estado['pieza_actual'], 
        constantes['FORMAS_PIEZAS']
    )
    
    # Limpiar líneas completas
    lineas_limpias = limpiar_lineas_completas(
        estado['tablero'], 
        constantes['TABLERO_ANCHO']
    )
    
    # Actualizar puntuación y nivel
    if lineas_limpias > 0:
        estado['puntuacion'] += calcular_puntuacion(
            lineas_limpias, 
            estado['nivel'], 
            constantes['PUNTUACION_LINEAS']
        )
        estado['lineas_totales'] += lineas_limpias
        estado['nivel'] = actualizar_nivel(estado['lineas_totales'])
    
    # Actualizar récord si es necesario
    if estado['puntuacion'] > estado['record']:
        estado['record'] = estado['puntuacion']
        guardar_datos(constantes['ARCHIVO_RECORD'], estado['record'])
    
    # Generar nueva pieza
    estado['pieza_actual'] = generar_pieza_aleatoria()
    
    # Verificar si el juego ha terminado
    forma_nueva = obtener_forma_pieza(
        estado['pieza_actual'], 
        constantes['FORMAS_PIEZAS']
    )
    if verificar_colision(
        estado['tablero'], forma_nueva, 
        estado['pieza_actual']['x'], estado['pieza_actual']['y'],
        constantes['TABLERO_ANCHO'], constantes['TABLERO_ALTO']
    ):
        estado['juego_terminado'] = True

def bucle_principal(ventana, lienzo, estado, constantes, etiquetas):
    """Bucle principal del juego"""
    if estado['juego_terminado']:
        mostrar_mensaje_juego_terminado(lienzo, constantes)
        return
    
    if estado['pausado']:
        # Si está pausado, reprogramar el bucle sin hacer nada
        ventana.after(100, bucle_principal, ventana, lienzo, estado, constantes, etiquetas)
        return
    
    # Mover pieza actual hacia abajo
    pieza = estado['pieza_actual']
    if pieza:
        formas = constantes['FORMAS_PIEZAS']
        forma_actual = obtener_forma_pieza(pieza, formas)
        
        nueva_y = pieza['y'] + 1
        if verificar_colision(
            estado['tablero'], forma_actual, pieza['x'], nueva_y,
            constantes['TABLERO_ANCHO'], constantes['TABLERO_ALTO']
        ):
            # Colisión detectada, fijar pieza
            fijar_pieza_y_continuar(estado, constantes)
        else:
            # No hay colisión, continuar moviendo
            pieza['y'] = nueva_y
    
    # Actualizar interfaz
    actualizar_interfaz(lienzo, estado['tablero'], estado['pieza_actual'], constantes, etiquetas, estado)
    
    # Calcular velocidad actual
    velocidad = calcular_velocidad(
        estado['nivel'],
        constantes['VELOCIDAD_BASE'],
        constantes['VELOCIDAD_MINIMA'],
        constantes['REDUCCION_VELOCIDAD']
    )
    
    # Programar siguiente iteración
    ventana.after(velocidad, bucle_principal, ventana, lienzo, estado, constantes, etiquetas)

# =============================================
# FUNCIÓN PRINCIPAL
# =============================================

def main():
    """Función principal que inicia el juego"""
    # Configurar constantes
    constantes = configurar_constantes()
    
    # Cargar récord
    record = cargar_datos(constantes['ARCHIVO_RECORD'])
    
    # Estado inicial del juego
    estado_juego = {
        'tablero': crear_tablero_vacio(
            constantes['TABLERO_ANCHO'], 
            constantes['TABLERO_ALTO']
        ),
        'pieza_actual': generar_pieza_aleatoria(),
        'puntuacion': 0,
        'record': record,
        'nivel': 1,
        'lineas_totales': 0,
        'juego_terminado': False,
        'pausado': False
    }
    
    # Crear interfaz
    ventana = crear_ventana_principal(constantes)
    lienzo = crear_lienzo_juego(ventana, constantes)
    panel = crear_panel_informacion(ventana)
    etiquetas = crear_etiquetas_informacion(panel)
    
    # Empaquetar elementos
    lienzo.pack(side=tk.LEFT)
    
    # Configurar controles
    configurar_controles(ventana, estado_juego, constantes, lienzo)
    
    # Iniciar bucle del juego
    bucle_principal(ventana, lienzo, estado_juego, constantes, etiquetas)
    
    # Iniciar aplicación
    ventana.mainloop()

if __name__ == "__main__":
    main()