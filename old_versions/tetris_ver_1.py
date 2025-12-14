import tkinter as tk
import random

# --- 1. Constantes del Juego (Versión Simplificada) ---
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
SQUARE_SIZE = 30

# Colores básicos
PIECE_COLORS = [
    "#1a1a1a",  # Vacío
    "#00f0f0",  # I (Cian)
    "#f0f000",  # O (Amarillo)
    "#a000f0",  # T (Morado)
    "#00f000",  # S (Verde)
    "#f00000",  # Z (Rojo)
    "#0000f0",  # J (Azul)
    "#f0a000"   # L (Naranja)
]

# Formas básicas de las piezas
PIECE_SHAPES = [
    [], # 0. Vacío
    [[[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]], [[0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,0,0]]], # I
    [[[2,2], [2,2]]], # O
    [[[0,3,0], [3,3,3], [0,0,0]], [[0,3,0], [0,3,3], [0,3,0]], [[0,0,0], [3,3,3], [0,3,0]], [[0,3,0], [3,3,0], [0,3,0]]], # T
]

# --- 2. Variables de Estado Global ---
board_state = []
current_piece = None
game_over_flag = False

# --- 3. Funciones Básicas del Juego ---
def create_empty_board():
    """Crea un tablero vacío"""
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def get_random_piece():
    """Devuelve una pieza aleatoria simple"""
    shape_index = random.randint(1, 3)  # Solo I, O y T para empezar
    return {
        'shape_index': shape_index,
        'rotation': 0,
        'x': BOARD_WIDTH // 2 - 2,
        'y': 0
    }

def get_current_shape():
    """Obtiene la forma actual de la pieza"""
    if not current_piece: 
        return []
    return PIECE_SHAPES[current_piece['shape_index']][current_piece['rotation']]

def check_collision(shape, x, y):
    """Verifica colisiones básicas"""
    for y_offset, row in enumerate(shape):
        for x_offset, cell_value in enumerate(row):
            if cell_value != 0:
                board_x = x + x_offset
                board_y = y + y_offset
                
                if board_x < 0 or board_x >= BOARD_WIDTH:
                    return True
                if board_y >= BOARD_HEIGHT:
                    return True
                if board_y >= 0 and board_state[board_y][board_x] != 0:
                    return True
    return False

def fix_piece():
    """Fija la pieza actual en el tablero"""
    global board_state
    
    shape = get_current_shape()
    piece_x = current_piece['x']
    piece_y = current_piece['y']
    color_index = current_piece['shape_index']

    for y, row in enumerate(shape):
        for x, cell_value in enumerate(row):
            if cell_value != 0 and piece_y + y >= 0:
                board_state[piece_y + y][piece_x + x] = color_index

def create_new_piece():
    """Crea una nueva pieza y verifica game over"""
    global current_piece, game_over_flag
    
    current_piece = get_random_piece()
    
    # Comprobar si la nueva pieza causa game over
    if check_collision(get_current_shape(), current_piece['x'], current_piece['y']):
        game_over_flag = True
        canvas.create_text(
            BOARD_WIDTH * SQUARE_SIZE / 2, 
            BOARD_HEIGHT * SQUARE_SIZE / 2,
            text="GAME OVER", 
            font=("Arial", 30, "bold"), 
            fill="red"
        )

# --- 4. Funciones de Dibujo Simplificadas ---
def draw_board():
    """Dibuja el tablero completo"""
    canvas.delete("all")
    
    # Dibjar las piezas fijadas
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            if board_state[y][x] != 0:
                color = PIECE_COLORS[board_state[y][x]]
                canvas.create_rectangle(
                    x * SQUARE_SIZE, y * SQUARE_SIZE,
                    (x + 1) * SQUARE_SIZE, (y + 1) * SQUARE_SIZE,
                    fill=color, outline="#404040"
                )
    
    # Dibujar la pieza actual
    if current_piece and not game_over_flag:
        shape = get_current_shape()
        color = PIECE_COLORS[current_piece['shape_index']]
        
        for y, row in enumerate(shape):
            for x, cell_value in enumerate(row):
                if cell_value != 0:
                    canvas_x = (current_piece['x'] + x) * SQUARE_SIZE
                    canvas_y = (current_piece['y'] + y) * SQUARE_SIZE
                    if canvas_y >= 0:
                        canvas.create_rectangle(
                            canvas_x, canvas_y,
                            canvas_x + SQUARE_SIZE, canvas_y + SQUARE_SIZE,
                            fill=color, outline="white"
                        )

# --- 5. Bucle del Juego Simplificado ---
def game_loop():
    """Bucle principal del juego"""
    if not game_over_flag:
        # Mover la pieza hacia abajo
        if current_piece:
            new_y = current_piece['y'] + 1
            
            if not check_collision(get_current_shape(), current_piece['x'], new_y):
                current_piece['y'] = new_y
            else:
                # Fijar pieza y crear nueva
                fix_piece()
                create_new_piece()
        
        draw_board()
    
    # Continuar el bucle
    window.after(500, game_loop)  # Velocidad fija

# --- 6. Configuración Inicial de la Ventana ---
def setup_game():
    global window, canvas, board_state
    
    window = tk.Tk()
    window.title("Tetris - Primera Etapa")
    
    # Configurar el lienzo
    canvas = tk.Canvas(
        window,
        width=BOARD_WIDTH * SQUARE_SIZE,
        height=BOARD_HEIGHT * SQUARE_SIZE,
        bg="#1a1a1a"
    )
    canvas.pack()
    
    # Inicializar el juego
    board_state = create_empty_board()
    create_new_piece()
    
    # Iniciar el bucle del juego
    game_loop()
    window.mainloop()

# --- 7. Iniciar el Juego ---
if __name__ == "__main__":
    setup_game()