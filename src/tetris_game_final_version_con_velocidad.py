#!/usr/bin/env python3
"""
Tetris - Juego completo implementado de manera procedural

Este módulo implementa el clásico juego Tetris con todas las características:
- Sistema de piezas y rotaciones
- Sistema de puntuación con niveles
- Funcionalidad de "Hold" y "Next"
- Pantallas de "Game Over" y pausa
- Persistencia de récords en JSON
- Pieza fantasma (ghost piece) para referencia visual

Autor: [Tu Nombre]
Fecha: [Fecha]
Versión: 1.0
"""

import tkinter as tk
import random
import json

# ============================================================================
# CONFIGURACIÓN Y CONSTANTES DEL JUEGO
# ============================================================================

# ----------------------------------------------------------------------------
# Dimensiones del tablero
# ----------------------------------------------------------------------------
BOARD_WIDTH = 10          # Ancho del tablero en celdas
BOARD_HEIGHT = 20         # Alto del tablero en celdas
SQUARE_SIZE = 30          # Tamaño de cada celda en píxeles

# ----------------------------------------------------------------------------
# Dimensiones de la ventana
# ----------------------------------------------------------------------------
GAME_WIDTH = BOARD_WIDTH * SQUARE_SIZE    # Ancho del área de juego
GAME_HEIGHT = BOARD_HEIGHT * SQUARE_SIZE  # Alto del área de juego
SIDE_PANEL_WIDTH = 200                    # Ancho del panel lateral
WINDOW_WIDTH = GAME_WIDTH + SIDE_PANEL_WIDTH  # Ancho total de la ventana
WINDOW_HEIGHT = GAME_HEIGHT               # Alto total de la ventana

# ----------------------------------------------------------------------------
# Lienzos pequeños (Next y Hold)
# ----------------------------------------------------------------------------
SQUARE_SIZE_SMALL = 20                    # Tamaño de celda para paneles pequeños
MINI_CANVAS_WIDTH = 4 * SQUARE_SIZE_SMALL  # Ancho del lienzo pequeño
MINI_CANVAS_HEIGHT = 4 * SQUARE_SIZE_SMALL # Alto del lienzo pequeño

# ----------------------------------------------------------------------------
# Sistema de niveles y velocidad
# ----------------------------------------------------------------------------
BASE_SPEED = 500          # Velocidad inicial en milisegundos
SPEED_DECREMENT = 40      # Reducción de velocidad por nivel
MIN_SPEED = 100           # Velocidad mínima (máxima dificultad)
LEVEL_UP_LINES = 10       # Líneas necesarias para subir de nivel

# ----------------------------------------------------------------------------
# Sistema de puntuación
# ----------------------------------------------------------------------------
# Puntos por número de líneas eliminadas simultáneamente
SCORE_VALUES = {
    1: 40,    # 1 línea = 40 puntos × nivel
    2: 100,   # 2 líneas = 100 puntos × nivel
    3: 300,   # 3 líneas = 300 puntos × nivel
    4: 1200   # 4 líneas = 1200 puntos × nivel (Tetris)
}

# ----------------------------------------------------------------------------
# Archivo para guardar récords
# ----------------------------------------------------------------------------
HIGH_SCORE_FILE = "tetris_highscore.json"

# ----------------------------------------------------------------------------
# Paleta de colores
# ----------------------------------------------------------------------------
PIECE_COLORS = [
    "#1a1a1a",  # 0: Vacío (negro oscuro)
    "#00f0f0",  # 1: Pieza I (cian)
    "#f0f000",  # 2: Pieza O (amarillo)
    "#a000f0",  # 3: Pieza T (morado)
    "#00f000",  # 4: Pieza S (verde)
    "#f00000",  # 5: Pieza Z (rojo)
    "#0000f0",  # 6: Pieza J (azul)
    "#f0a000"   # 7: Pieza L (naranja)
]

# ----------------------------------------------------------------------------
# Colores de la interfaz
# ----------------------------------------------------------------------------
GRID_COLOR = "#404040"        # Color de la cuadrícula
EMPTY_CELL_COLOR = "#1a1a1a"  # Color de celda vacía
GHOST_COLOR = "#606060"       # Color de la pieza fantasma
SIDE_PANEL_BG = "#2c2c2c"     # Fondo del panel lateral

# ----------------------------------------------------------------------------
# Definición de formas de las piezas
# ----------------------------------------------------------------------------
PIECE_SHAPES = [
    [],  # Índice 0: vacío (no se usa)
    
    # Pieza I (índice 1)
    [
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
    ],
    
    # Pieza O (índice 2)
    [[[2, 2], [2, 2]]],
    
    # Pieza T (índice 3)
    [
        [[0, 3, 0], [3, 3, 3], [0, 0, 0]],
        [[0, 3, 0], [0, 3, 3], [0, 3, 0]],
        [[0, 0, 0], [3, 3, 3], [0, 3, 0]],
        [[0, 3, 0], [3, 3, 0], [0, 3, 0]]
    ],
    
    # Pieza S (índice 4)
    [
        [[0, 4, 4], [4, 4, 0], [0, 0, 0]],
        [[0, 4, 0], [0, 4, 4], [0, 0, 4]]
    ],
    
    # Pieza Z (índice 5)
    [
        [[5, 5, 0], [0, 5, 5], [0, 0, 0]],
        [[0, 0, 5], [0, 5, 5], [0, 5, 0]]
    ],
    
    # Pieza J (índice 6)
    [
        [[6, 0, 0], [6, 6, 6], [0, 0, 0]],
        [[0, 6, 6], [0, 6, 0], [0, 6, 0]],
        [[0, 0, 0], [6, 6, 6], [0, 0, 6]],
        [[0, 6, 0], [0, 6, 0], [6, 6, 0]]
    ],
    
    # Pieza L (índice 7)
    [
        [[0, 0, 7], [7, 7, 7], [0, 0, 0]],
        [[0, 7, 0], [0, 7, 0], [0, 7, 7]],
        [[0, 0, 0], [7, 7, 7], [7, 0, 0]],
        [[7, 7, 0], [0, 7, 0], [0, 7, 0]]
    ]
]

# ============================================================================
# VARIABLES GLOBALES DE ESTADO
# ============================================================================

# Estado del tablero
board_state = []          # Matriz que representa el estado del tablero

# Estado del juego
current_piece = None      # Pieza actual en movimiento
next_piece = None         # Siguiente pieza que aparecerá
held_piece = None         # Pieza guardada (puede ser None)
can_hold = True           # Bandera para controlar el uso de hold

# Puntuación y nivel
score = 0                 # Puntuación actual
high_score = 0            # Récord máximo
level = 1                 # Nivel actual
lines_cleared_count = 0   # Líneas eliminadas en el nivel actual

# Estado del juego
game_over_flag = False    # True si el juego ha terminado
is_paused = False         # True si el juego está en pausa

# Referencias a widgets de Tkinter
window = None             # Ventana principal
canvas = None             # Lienzo principal del juego
next_canvas = None        # Lienzo para mostrar siguiente pieza
hold_canvas = None        # Lienzo para mostrar pieza guardada
score_label = None        # Etiqueta para mostrar puntuación
high_score_label = None   # Etiqueta para mostrar récord
level_label = None        # Etiqueta para mostrar nivel

# ============================================================================
# FUNCIONES DE UTILIDAD GENERAL
# ============================================================================

def crear_tablero_vacio():
    """
    Crea y retorna un tablero vacío.
    
    Returns:
        list: Matriz de BOARD_HEIGHT x BOARD_WIDTH llena de ceros
    """
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]


def crear_pieza_aleatoria():
    """
    Crea una nueva pieza aleatoria.
    
    Returns:
        dict: Diccionario con la información de la pieza
    """
    shape_index = random.randint(1, 7)  # Índice entre 1 y 7 (excluye vacío)
    
    return {
        'shape_index': shape_index,
        'rotation': 0,
        'x': (BOARD_WIDTH // 2) - 2,  # Posición centrada horizontalmente
        'y': 0                         # Posición en la parte superior
    }


def obtener_forma_actual():
    """
    Obtiene la forma matricial de la pieza actual.
    
    Returns:
        list: Matriz que representa la forma actual de la pieza
    """
    if not current_piece:
        return []
    
    shape_index = current_piece['shape_index']
    rotation = current_piece['rotation']
    
    return PIECE_SHAPES[shape_index][rotation]


def leer_puntuacion_maxima():
    """
    Lee la puntuación máxima desde el archivo JSON.
    
    Returns:
        int: Puntuación máxima guardada, o 0 si hay error
    """
    try:
        with open(HIGH_SCORE_FILE, 'r') as archivo:
            datos = json.load(archivo)
            return datos.get('high_score', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def guardar_puntuacion_maxima(nuevo_record):
    """
    Guarda una nueva puntuación máxima en el archivo JSON.
    
    Args:
        nuevo_record (int): Nueva puntuación máxima a guardar
    """
    datos = {'high_score': nuevo_record}
    
    try:
        with open(HIGH_SCORE_FILE, 'w') as archivo:
            json.dump(datos, archivo, indent=2)
    except IOError as error:
        print(f"Error al guardar el récord: {error}")


# ============================================================================
# FUNCIONES DE LÓGICA DEL JUEGO
# ============================================================================

def verificar_colision(forma, x, y):
    """
    Verifica si una forma en posición (x, y) colisiona con algo.
    
    Args:
        forma (list): Matriz que representa la forma
        x (int): Posición horizontal
        y (int): Posición vertical
        
    Returns:
        bool: True si hay colisión, False si la posición es válida
    """
    for y_offset, fila in enumerate(forma):
        for x_offset, valor_celda in enumerate(fila):
            if valor_celda != 0:
                tablero_x = x + x_offset
                tablero_y = y + y_offset
                
                # Verificar límites izquierdo/derecho
                if tablero_x < 0 or tablero_x >= BOARD_WIDTH:
                    return True
                
                # Verificar límite inferior
                if tablero_y >= BOARD_HEIGHT:
                    return True
                
                # Verificar colisión con otras piezas (solo dentro del tablero)
                if tablero_y >= 0 and board_state[tablero_y][tablero_x] != 0:
                    return True
    
    return False


def fijar_pieza_actual():
    """
    Fija la pieza actual en el tablero (la hace permanente).
    """
    global board_state
    
    forma = obtener_forma_actual()
    pieza_x = current_piece['x']
    pieza_y = current_piece['y']
    color_index = current_piece['shape_index']
    
    for y, fila in enumerate(forma):
        for x, valor_celda in enumerate(fila):
            if valor_celda != 0:
                if pieza_y + y >= 0:  # Solo fijar si está dentro del tablero
                    board_state[pieza_y + y][pieza_x + x] = color_index


def limpiar_lineas_completas():
    """
    Elimina las líneas completas del tablero.
    
    Returns:
        int: Número de líneas eliminadas
    """
    global board_state
    
    # Filtrar solo las filas que NO están completas (tienen al menos un 0)
    nuevo_tablero = [fila for fila in board_state if 0 in fila]
    
    # Calcular cuántas líneas se eliminaron
    lineas_eliminadas = BOARD_HEIGHT - len(nuevo_tablero)
    
    if lineas_eliminadas > 0:
        # Crear nuevas filas vacías para la parte superior
        filas_vacias = [[0 for _ in range(BOARD_WIDTH)] 
                       for _ in range(lineas_eliminadas)]
        
        # Combinar filas vacías con el nuevo tablero
        board_state = filas_vacias + nuevo_tablero
    
    return lineas_eliminadas


def crear_nueva_pieza():
    """
    Mueve la siguiente pieza a la posición actual y genera una nueva siguiente.
    También verifica si el juego debe terminar.
    """
    global current_piece, next_piece, can_hold, game_over_flag
    
    # Mover siguiente pieza a actual
    current_piece = next_piece
    
    # Generar nueva siguiente pieza
    next_piece = crear_pieza_aleatoria()
    
    # Actualizar visualización de siguiente pieza
    dibujar_pieza_mini(next_canvas, next_piece)
    
    # Permitir usar hold nuevamente
    can_hold = True
    
    # Verificar si la nueva posición causa game over
    if verificar_colision(obtener_forma_actual(), 
                          current_piece['x'], 
                          current_piece['y']):
        game_over_flag = True
        mostrar_mensaje_game_over()


def actualizar_puntuacion_y_nivel(lineas_eliminadas):
    """
    Actualiza la puntuación y el nivel basándose en líneas eliminadas.
    
    Args:
        lineas_eliminadas (int): Número de líneas eliminadas en este movimiento
    """
    global score, level, lines_cleared_count, high_score
    
    if lineas_eliminadas == 0:
        return
    
    # 1. Actualizar puntuación
    puntos_base = SCORE_VALUES.get(lineas_eliminadas, 0)
    score += puntos_base * level
    score_label.config(text=f"Puntuación:\n{score}")
    
    # 2. Actualizar nivel
    lines_cleared_count += lineas_eliminadas
    
    if lines_cleared_count >= LEVEL_UP_LINES:
        level += 1
        lines_cleared_count -= LEVEL_UP_LINES
        level_label.config(text=f"Nivel:\n{level}")
    
    # 3. Verificar y actualizar récord
    if score > high_score:
        high_score = score
        high_score_label.config(text=f"Récord:\n{score}")


def obtener_velocidad_juego():
    """
    Calcula la velocidad actual del juego basándose en el nivel.
    
    Returns:
        int: Velocidad en milisegundos
    """
    velocidad = BASE_SPEED - ((level - 1) * SPEED_DECREMENT)
    return max(MIN_SPEED, velocidad)


def obtener_posicion_fantasma():
    """
    Calcula la posición más baja posible para la pieza actual (posición fantasma).
    
    Returns:
        int: Coordenada Y de la posición fantasma
    """
    if not current_piece:
        return 0
    
    forma = obtener_forma_actual()
    pieza_x = current_piece['x']
    
    # Encontrar la posición Y más baja posible
    y_fantasma = current_piece['y']
    
    while not verificar_colision(forma, pieza_x, y_fantasma + 1):
        y_fantasma += 1
    
    return y_fantasma


# ============================================================================
# FUNCIONES DE CONTROL DEL JUGADOR
# ============================================================================

def mover_pieza(dx):
    """
    Mueve la pieza actual horizontalmente.
    
    Args:
        dx (int): Desplazamiento horizontal (-1 para izquierda, 1 para derecha)
    """
    if not current_piece or game_over_flag or is_paused:
        return
    
    nueva_x = current_piece['x'] + dx
    
    if not verificar_colision(obtener_forma_actual(), nueva_x, current_piece['y']):
        current_piece['x'] = nueva_x
    
    dibujar_juego()


def rotar_pieza():
    """
    Rota la pieza actual si es posible (con wall kick).
    """
    if not current_piece or game_over_flag or is_paused:
        return
    
    shape_index = current_piece['shape_index']
    rotaciones = PIECE_SHAPES[shape_index]
    num_rotaciones = len(rotaciones)
    nueva_rotacion = (current_piece['rotation'] + 1) % num_rotaciones
    nueva_forma = rotaciones[nueva_rotacion]
    
    # Intentar diferentes desplazamientos (wall kick)
    for desplazamiento_x in [0, -1, 1, -2, 2]:
        if not verificar_colision(nueva_forma, 
                                  current_piece['x'] + desplazamiento_x, 
                                  current_piece['y']):
            current_piece['rotation'] = nueva_rotacion
            current_piece['x'] += desplazamiento_x
            dibujar_juego()
            return


def caida_dura():
    """
    Realiza una caída dura (hard drop) de la pieza actual.
    """
    if not current_piece or game_over_flag or is_paused:
        return
    
    # Encontrar la posición más baja posible
    y_prueba = current_piece['y']
    
    while not verificar_colision(obtener_forma_actual(), 
                                 current_piece['x'], 
                                 y_prueba + 1):
        y_prueba += 1
    
    current_piece['y'] = y_prueba
    
    # Fijar la pieza y pasar al siguiente turno
    fijar_pieza_y_siguiente_turno()


def guardar_pieza():
    """
    Guarda la pieza actual o la intercambia con la pieza guardada.
    """
    global current_piece, held_piece, can_hold, game_over_flag
    
    if game_over_flag or is_paused or not can_hold:
        return
    
    can_hold = False  # Solo se puede usar hold una vez por pieza
    
    if not held_piece:  # Si no hay pieza guardada
        held_piece = current_piece
        crear_nueva_pieza()
    else:  # Intercambiar piezas
        current_piece, held_piece = held_piece, current_piece
        
        # Restablecer posición de la pieza que entra al tablero
        current_piece['x'] = (BOARD_WIDTH // 2) - 2
        current_piece['y'] = 0
        
        # Verificar si el intercambio causa game over
        if verificar_colision(obtener_forma_actual(), 
                              current_piece['x'], 
                              current_piece['y']):
            game_over_flag = True
            mostrar_mensaje_game_over()
    
    # Actualizar visualización
    dibujar_pieza_mini(hold_canvas, held_piece)
    dibujar_juego()


def alternar_pausa():
    """
    Alterna el estado de pausa del juego.
    """
    global is_paused
    
    if game_over_flag:
        return
    
    is_paused = not is_paused
    
    if is_paused:
        # Mostrar mensaje de pausa
        canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2,
            text="PAUSADO",
            font=("Arial", 30, "bold"),
            fill="white",
            tags="mensaje_pausa"
        )
    else:
        # Eliminar mensaje de pausa y reanudar juego
        canvas.delete("mensaje_pausa")
        bucle_juego()  # Reanudar el bucle


# ============================================================================
# FUNCIONES DE DIBUJO
# ============================================================================

def dibujar_estado_tablero():
    """
    Dibuja el estado actual del tablero (piezas fijas).
    """
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            x1 = x * SQUARE_SIZE
            y1 = y * SQUARE_SIZE
            x2 = x1 + SQUARE_SIZE
            y2 = y1 + SQUARE_SIZE
            
            valor_celda = board_state[y][x]
            color = PIECE_COLORS[valor_celda]
            
            canvas.create_rectangle(x1, y1, x2, y2, 
                                    fill=color, outline=GRID_COLOR)


def dibujar_pieza_fantasma():
    """
    Dibuja la pieza fantasma (sombra de la pieza actual).
    """
    if not current_piece:
        return
    
    forma = obtener_forma_actual()
    pieza_x = current_piece['x']
    y_fantasma = obtener_posicion_fantasma()
    
    for y, fila in enumerate(forma):
        for x, valor_celda in enumerate(fila):
            if valor_celda != 0:
                canvas_x = (pieza_x + x) * SQUARE_SIZE
                canvas_y = (y_fantasma + y) * SQUARE_SIZE
                
                if canvas_y >= 0:
                    canvas.create_rectangle(
                        canvas_x, canvas_y,
                        canvas_x + SQUARE_SIZE, canvas_y + SQUARE_SIZE,
                        fill="", outline=GHOST_COLOR, width=2
                    )


def dibujar_pieza_actual():
    """
    Dibuja la pieza actual en movimiento.
    """
    if not current_piece:
        return
    
    forma = obtener_forma_actual()
    color_pieza = PIECE_COLORS[current_piece['shape_index']]
    pieza_x = current_piece['x']
    pieza_y = current_piece['y']
    
    for y, fila in enumerate(forma):
        for x, valor_celda in enumerate(fila):
            if valor_celda != 0:
                canvas_x = (pieza_x + x) * SQUARE_SIZE
                canvas_y = (pieza_y + y) * SQUARE_SIZE
                
                if canvas_y >= 0:
                    canvas.create_rectangle(
                        canvas_x, canvas_y,
                        canvas_x + SQUARE_SIZE, canvas_y + SQUARE_SIZE,
                        fill=color_pieza, outline="white"
                    )


def dibujar_pieza_mini(lienzo_mini, pieza):
    """
    Dibuja una pieza en un lienzo pequeño (Next o Hold).
    
    Args:
        lienzo_mini (tk.Canvas): Lienzo donde dibujar
        pieza (dict): Pieza a dibujar (o None)
    """
    lienzo_mini.delete("all")
    
    if not pieza:
        return
    
    # Usar siempre la primera rotación para visualización
    shape_index = pieza['shape_index']
    forma = PIECE_SHAPES[shape_index][0]
    color = PIECE_COLORS[shape_index]
    
    # Calcular desplazamiento para centrar la pieza
    desplazamiento_x = (MINI_CANVAS_WIDTH - (len(forma[0]) * SQUARE_SIZE_SMALL)) / 2
    desplazamiento_y = (MINI_CANVAS_HEIGHT - (len(forma) * SQUARE_SIZE_SMALL)) / 2
    
    for y, fila in enumerate(forma):
        for x, valor_celda in enumerate(fila):
            if valor_celda != 0:
                x1 = desplazamiento_x + x * SQUARE_SIZE_SMALL
                y1 = desplazamiento_y + y * SQUARE_SIZE_SMALL
                x2 = x1 + SQUARE_SIZE_SMALL
                y2 = y1 + SQUARE_SIZE_SMALL
                
                lienzo_mini.create_rectangle(x1, y1, x2, y2, 
                                             fill=color, outline="white")


def dibujar_juego():
    """
    Función principal de dibujo: limpia y redibuja todo el juego.
    """
    if game_over_flag:
        return
    
    # Limpiar el lienzo
    canvas.delete("all")
    
    # Dibujar todos los componentes
    dibujar_estado_tablero()
    dibujar_pieza_fantasma()
    dibujar_pieza_actual()


def mostrar_mensaje_game_over():
    """
    Muestra el mensaje de Game Over y actualiza el récord.
    """
    global high_score
    
    # Guardar nuevo récord si es necesario
    if score > high_score:
        high_score = score
        guardar_puntuacion_maxima(score)
        high_score_label.config(text=f"Récord:\n{high_score} (¡NUEVO!)")
    
    # Mostrar mensaje de Game Over
    canvas.create_text(
        GAME_WIDTH / 2, GAME_HEIGHT / 2,
        text="GAME OVER",
        font=("Arial", 30, "bold"),
        fill="red"
    )


# ============================================================================
# FUNCIONES DEL BUCLE DEL JUEGO
# ============================================================================

def fijar_pieza_y_siguiente_turno():
    """
    Función auxiliar que fija la pieza actual, limpia líneas,
    actualiza puntuación y crea nueva pieza.
    """
    fijar_pieza_actual()
    lineas_eliminadas = limpiar_lineas_completas()
    actualizar_puntuacion_y_nivel(lineas_eliminadas)
    crear_nueva_pieza()


def bucle_juego():
    """
    Función principal del bucle del juego (game loop).
    """
    if game_over_flag or is_paused:
        return  # Detener el bucle si el juego terminó o está en pausa
    
    # Mover la pieza hacia abajo (gravedad)
    if current_piece:
        nueva_y = current_piece['y'] + 1
        
        # Verificar colisión
        if not verificar_colision(obtener_forma_actual(), 
                                  current_piece['x'], 
                                  nueva_y):
            current_piece['y'] = nueva_y
        else:
            # Colisión detectada: fijar pieza y pasar al siguiente turno
            fijar_pieza_y_siguiente_turno()
    
    # Redibujar el juego
    dibujar_juego()
    
    # Programar próximo ciclo del bucle
    window.after(obtener_velocidad_juego(), bucle_juego)


# ============================================================================
# CONFIGURACIÓN DE LA INTERFAZ GRÁFICA
# ============================================================================

def configurar_ventana():
    """
    Configura la ventana principal y todos los widgets.
    """
    global window, canvas, next_canvas, hold_canvas
    global score_label, high_score_label, level_label
    global high_score, next_piece, board_state
    
    # ------------------------------------------------------------------------
    # Crear ventana principal
    # ------------------------------------------------------------------------
    window = tk.Tk()
    window.title("Tetris - Versión Mejorada")
    window.resizable(False, False)
    
    # ------------------------------------------------------------------------
    # Cargar récord y crear tablero
    # ------------------------------------------------------------------------
    high_score = leer_puntuacion_maxima()
    board_state = crear_tablero_vacio()
    
    # ------------------------------------------------------------------------
    # Crear frames (contenedores)
    # ------------------------------------------------------------------------
    
    # Frame principal para el área de juego
    frame_principal = tk.Frame(window, bg=EMPTY_CELL_COLOR)
    frame_principal.grid(row=0, column=0)
    
    # Frame lateral para información
    frame_lateral = tk.Frame(window, width=SIDE_PANEL_WIDTH, bg=SIDE_PANEL_BG)
    frame_lateral.grid(row=0, column=1, sticky="ns")  # "ns" = estirar verticalmente
    frame_lateral.pack_propagate(False)  # Evitar que el frame se encoja
    
    # ------------------------------------------------------------------------
    # Configurar panel lateral
    # ------------------------------------------------------------------------
    
    # Título del juego
    etiqueta_titulo = tk.Label(
        frame_lateral,
        text="TETRIS",
        font=("Arial", 24, "bold"),
        fg="white",
        bg=SIDE_PANEL_BG
    )
    etiqueta_titulo.pack(pady=10)
    
    # Récord
    high_score_label = tk.Label(
        frame_lateral,
        text=f"Récord:\n{high_score}",
        font=("Arial", 16),
        fg="white",
        bg=SIDE_PANEL_BG
    )
    high_score_label.pack(pady=20)
    
    # Puntuación actual
    score_label = tk.Label(
        frame_lateral,
        text=f"Puntuación:\n{score}",
        font=("Arial", 16),
        fg="white",
        bg=SIDE_PANEL_BG
    )
    score_label.pack(pady=20)
    
    # Nivel actual
    level_label = tk.Label(
        frame_lateral,
        text=f"Nivel:\n{level}",
        font=("Arial", 16),
        fg="white",
        bg=SIDE_PANEL_BG
    )
    level_label.pack(pady=20)
    
    # Sección Hold
    etiqueta_hold = tk.Label(
        frame_lateral,
        text="HOLD (C)",
        font=("Arial", 14),
        fg="white",
        bg=SIDE_PANEL_BG
    )
    etiqueta_hold.pack(pady=(10, 0))
    
    hold_canvas = tk.Canvas(
        frame_lateral,
        width=MINI_CANVAS_WIDTH,
        height=MINI_CANVAS_HEIGHT,
        bg="black",
        highlightthickness=0
    )
    hold_canvas.pack()
    
    # Sección Next
    etiqueta_next = tk.Label(
        frame_lateral,
        text="NEXT",
        font=("Arial", 14),
        fg="white",
        bg=SIDE_PANEL_BG
    )
    etiqueta_next.pack(pady=(20, 0))
    
    next_canvas = tk.Canvas(
        frame_lateral,
        width=MINI_CANVAS_WIDTH,
        height=MINI_CANVAS_HEIGHT,
        bg="black",
        highlightthickness=0
    )
    next_canvas.pack()
    
    # Instrucciones
    etiqueta_instrucciones = tk.Label(
        frame_lateral,
        text="Controles:\n"
             "← → : Mover\n"
             "↑ : Rotar\n"
             "↓ : Caída rápida\n"
             "Espacio : Caída dura\n"
             "C : Guardar pieza\n"
             "P : Pausa",
        font=("Arial", 10),
        fg="grey",
        bg=SIDE_PANEL_BG,
        justify="left"
    )
    etiqueta_instrucciones.pack(pady=(30, 0))
    
    # ------------------------------------------------------------------------
    # Configurar área de juego principal
    # ------------------------------------------------------------------------
    canvas = tk.Canvas(
        frame_principal,
        width=GAME_WIDTH,
        height=GAME_HEIGHT,
        bg=EMPTY_CELL_COLOR,
        highlightthickness=0
    )
    canvas.pack()
    
    # ------------------------------------------------------------------------
    # Configurar controles de teclado
    # ------------------------------------------------------------------------
    window.bind("<Left>", lambda evento: mover_pieza(-1))
    window.bind("<Right>", lambda evento: mover_pieza(1))
    window.bind("<Up>", lambda evento: rotar_pieza())
    window.bind("<Down>", lambda evento: bucle_juego())  # Caída rápida
    window.bind("<space>", lambda evento: caida_dura())
    window.bind("<c>", lambda evento: guardar_pieza())
    window.bind("<p>", lambda evento: alternar_pausa())
    
    # ------------------------------------------------------------------------
    # Inicializar juego
    # ------------------------------------------------------------------------
    
    # Crear primera siguiente pieza
    next_piece = crear_pieza_aleatoria()
    
    # Crear primera pieza actual
    crear_nueva_pieza()
    
    # Iniciar bucle del juego
    bucle_juego()


# ============================================================================
# PUNTO DE ENTRADA PRINCIPAL
# ============================================================================

def main():
    """
    Función principal que inicia el juego.
    """
    configurar_ventana()
    window.mainloop()


if __name__ == "__main__":
    main()