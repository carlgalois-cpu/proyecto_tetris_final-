import tkinter as tk
import random
import json

# --- 1. Constantes del Juego (Expandidas) ---

# --- Tablero ---
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
SQUARE_SIZE = 30 # Tamaño de bloque en el tablero principal

# --- Dimensiones ---
# Lienzo principal del juego
GAME_WIDTH = BOARD_WIDTH * SQUARE_SIZE
GAME_HEIGHT = BOARD_HEIGHT * SQUARE_SIZE
# Panel lateral para información
SIDE_PANEL_WIDTH = 200
# Dimensiones totales de la ventana
WINDOW_WIDTH = GAME_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = GAME_HEIGHT

# --- Lienzos Pequeños (Next y Hold) ---
SQUARE_SIZE_SMALL = 20 # Bloques más pequeños
MINI_CANVAS_WIDTH = 4 * SQUARE_SIZE_SMALL
MINI_CANVAS_HEIGHT = 4 * SQUARE_SIZE_SMALL

# --- Velocidad y Niveles ---
BASE_SPEED = 500   # Velocidad inicial (ms)
SPEED_DECREMENT = 40 # Cuánto se reduce la velocidad por nivel
MIN_SPEED = 100    # Velocidad máxima
LEVEL_UP_LINES = 10 # Líneas para subir de nivel

# --- Puntuación ---
SCORE_VALUES = {
    1: 40, 2: 100, 3: 300, 4: 1200
}

# --- Archivo de Récord ---
HIGH_SCORE_FILE = "tetris_highscore.json"

# --- Colores ---
PIECE_COLORS = [
    "#1a1a1a", # 0: Vacío
    "#00f0f0", # 1: I (Cian)
    "#f0f000", # 2: O (Amarillo)
    "#a000f0", # 3: T (Morado)
    "#00f000", # 4: S (Verde)
    "#f00000", # 5: Z (Rojo)
    "#0000f0", # 6: J (Azul)
    "#f0a000"  # 7: L (Naranja)
]
GRID_COLOR = "#404040"
EMPTY_CELL_COLOR = "#1a1a1a"
GHOST_COLOR = "#606060" # Color para la pieza fantasma

# --- Formas ---
PIECE_SHAPES = [
    [], # 0. Vacío
    [[[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]], [[0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,0,0]]], # 1. 'I'
    [[[2,2], [2,2]]], # 2. 'O'
    [[[0,3,0], [3,3,3], [0,0,0]], [[0,3,0], [0,3,3], [0,3,0]], [[0,0,0], [3,3,3], [0,3,0]], [[0,3,0], [3,3,0], [0,3,0]]], # 3. 'T'
    [[[0,4,4], [4,4,0], [0,0,0]], [[0,4,0], [0,4,4], [0,0,4]]], # 4. 'S'
    [[[5,5,0], [0,5,5], [0,0,0]], [[0,0,5], [0,5,5], [0,5,0]]], # 5. 'Z'
    [[[6,0,0], [6,6,6], [0,0,0]], [[0,6,6], [0,6,0], [0,6,0]], [[0,0,0], [6,6,6], [0,0,6]], [[0,6,0], [0,6,0], [6,6,0]]], # 6. 'J'
    [[[0,0,7], [7,7,7], [0,0,0]], [[0,7,0], [0,7,0], [0,7,7]], [[0,0,0], [7,7,7], [7,0,0]], [[7,7,0], [0,7,0], [0,7,0]]]  # 7. 'L'
]

# --- 2. Variables de Estado Global ---

# --- Estado del Tablero ---
board_state = [] # La matriz del juego

# --- Estado de Puntuación y Nivel ---
score = 0
high_score = 0
level = 1
lines_cleared_count = 0 # Contador de líneas para subir de nivel

# --- Estado de las Piezas ---
current_piece = {} # Pieza activa
next_piece = {}    # Siguiente pieza
held_piece = {}    # Pieza guardada
can_hold = True    # Flag para permitir "Hold" solo una vez por pieza

# --- Estado del Juego ---
game_over_flag = False
is_paused = False

# --- Objetos de Tkinter (globales para fácil acceso) ---
window = None
canvas = None
next_canvas = None # Lienzo para la siguiente pieza
hold_canvas = None # Lienzo para la pieza guardada
score_label = None
high_score_label = None
level_label = None

# --- 3. Lógica del Juego (Funciones) ---

# --- Lógica de Piezas y Tablero ---

def create_empty_board():
    """Crea la matriz lógica del tablero, llena de 0s."""
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def get_random_piece():
    """Devuelve un *nuevo* diccionario de pieza aleatoria."""
    shape_index = random.randint(1, 7)
    return {
        'shape_index': shape_index,
        'rotation': 0,
        'x': (BOARD_WIDTH // 2) - 2, # Posición inicial
        'y': 0
    }

def get_current_shape():
    """Devuelve la matriz de la forma actual."""
    if not current_piece: return []
    shape_index = current_piece['shape_index']
    rotation = current_piece['rotation']
    return PIECE_SHAPES[shape_index][rotation]

def create_new_piece():
    """
    Mueve la 'next_piece' a 'current_piece' y genera una nueva 'next_piece'.
    """
    global current_piece, next_piece, can_hold, game_over_flag
    
    current_piece = next_piece
    next_piece = get_random_piece()
    draw_mini_piece(next_canvas, next_piece) # Actualiza el lienzo "Next"
    
    can_hold = True # Permite volver a usar "Hold"
    
    # Comprobación de Game Over
    if check_collision(get_current_shape(), current_piece['x'], current_piece['y']):
        game_over_flag = True
        show_game_over_message()

def check_collision(shape, x, y):
    """
    Verifica si una 'shape' en la posición (x, y) es válida.
    Devuelve True si hay colisión (inválida).
    Devuelve False si no hay colisión (válida).
    """
    for y_offset, row in enumerate(shape):
        for x_offset, cell_value in enumerate(row):
            if cell_value != 0:
                board_x = x + x_offset
                board_y = y + y_offset
                
                # Paredes (izquierda/derecha)
                if board_x < 0 or board_x >= BOARD_WIDTH: return True
                # Suelo
                if board_y >= BOARD_HEIGHT: return True
                # Otras piezas (solo si está dentro del tablero)
                if board_y >= 0 and board_state[board_y][board_x] != 0: return True
    return False

def fix_piece():
    """"Imprime" la pieza actual en el board_state (la fija)."""
    global board_state
    
    shape = get_current_shape()
    piece_x = current_piece['x']
    piece_y = current_piece['y']
    color_index = current_piece['shape_index']

    for y, row in enumerate(shape):
        for x, cell_value in enumerate(row):
            if cell_value != 0:
                if piece_y + y >= 0:
                    board_state[piece_y + y][piece_x + x] = color_index

def clear_completed_lines():
    """
    Revisa y limpia líneas completas. Devuelve el número de líneas limpiadas.
    """
    global board_state
    
    # 1. Crear un nuevo tablero solo con las filas que NO están llenas
    new_board = [row for row in board_state if 0 in row]
    
    # 2. Calcular cuántas líneas se limpiaron
    lines_cleared = BOARD_HEIGHT - len(new_board)
    
    # 3. Crear nuevas filas vacías para la parte superior
    empty_rows = [[0 for _ in range(BOARD_WIDTH)] for _ in range(lines_cleared)]
    
    # 4. Combinar las filas vacías con el nuevo tablero
    board_state = empty_rows + new_board
    
    return lines_cleared

# --- Lógica de Puntuación y Nivel ---

def update_score_and_level(lines_cleared):
    """Actualiza la puntuación y el nivel basado en las líneas limpiadas."""
    global score, level, lines_cleared_count, high_score
    
    if lines_cleared == 0:
        return

    # 1. Actualizar Puntuación
    score += SCORE_VALUES.get(lines_cleared, 0) * level
    score_label.config(text=f"Puntuación:\n{score}")
    
    # 2. Actualizar Nivel
    lines_cleared_count += lines_cleared
    if lines_cleared_count >= LEVEL_UP_LINES:
        level += 1
        lines_cleared_count -= LEVEL_UP_LINES
        level_label.config(text=f"Nivel:\n{level}")
        
    # 3. Comprobar Récord (en tiempo real)
    if score > high_score:
        high_score = score # Actualiza el high_score local
        high_score_label.config(text=f"Récord:\n{score}")

def get_game_speed():
    """Calcula la velocidad del juego basado en el nivel."""
    return max(MIN_SPEED, BASE_SPEED - ((level - 1) * SPEED_DECREMENT))

# --- Controles del Jugador (Nuevas Funciones) ---

def move_piece(dx):
    """Mueve la pieza horizontalmente."""
    if not current_piece or game_over_flag or is_paused: return
    
    new_x = current_piece['x'] + dx
    if not check_collision(get_current_shape(), new_x, current_piece['y']):
        current_piece['x'] = new_x
    
    draw_game(canvas) # Redibujar inmediatamente

def rotate_piece():
    """Rota la pieza activa."""
    if not current_piece or game_over_flag or is_paused: return

    # 1. Calcular la nueva rotación
    shape_index = current_piece['shape_index']
    rotations = PIECE_SHAPES[shape_index]
    num_rotations = len(rotations)
    new_rotation = (current_piece['rotation'] + 1) % num_rotations
    new_shape = PIECE_SHAPES[shape_index][new_rotation]
    
    # 2. Comprobar si la nueva forma es válida (con "Wall Kick" simple)
    # Intenta mover la pieza si choca al rotar
    for kick_x in [0, -1, 1, -2, 2]: # Prueba 5 posiciones (0, izq, der, izq2, der2)
        if not check_collision(new_shape, current_piece['x'] + kick_x, current_piece['y']):
            current_piece['rotation'] = new_rotation
            current_piece['x'] += kick_x
            draw_game(canvas)
            return

def hard_drop():
    """Baja la pieza instantáneamente (Hard Drop)."""
    if not current_piece or game_over_flag or is_paused: return
    
    # 1. Encontrar la posición más baja
    test_y = current_piece['y']
    while not check_collision(get_current_shape(), current_piece['x'], test_y + 1):
        test_y += 1
    
    current_piece['y'] = test_y
    
    # 2. Fijar la pieza y pasar al siguiente turno
    fix_piece_and_next_turn()
    draw_game(canvas)

### --- CORRECCIÓN AQUÍ --- ###
def hold_piece():
    """Guarda la pieza actual o la intercambia con la guardada."""
    # 1. Declarar TODAS las globales al INICIO
    global current_piece, held_piece, can_hold, game_over_flag
    
    # 2. Ahora podemos LEER game_over_flag sin error
    if game_over_flag or is_paused or not can_hold: return
    
    can_hold = False # Solo se puede usar 'hold' una vez
    
    if not held_piece: # Si 'Hold' está vacío
        held_piece = current_piece
        create_new_piece()
    else:
        # Intercambiar
        current_piece, held_piece = held_piece, current_piece
        
    # Resetear la posición de la pieza que *entra* al tablero
    current_piece['x'] = (BOARD_WIDTH // 2) - 2
    current_piece['y'] = 0
    
    # Comprobar si el intercambio causa Game Over
    if check_collision(get_current_shape(), current_piece['x'], current_piece['y']):
        # 3. La declaración 'global' extra de antes se elimina
        game_over_flag = True
        show_game_over_message()

    draw_mini_piece(hold_canvas, held_piece)
    draw_game(canvas)
### --- FIN DE LA CORRECCIÓN --- ###

def toggle_pause():
    """Pausa o reanuda el juego."""
    global is_paused
    if game_over_flag: return
    
    is_paused = not is_paused
    
    if is_paused:
        # Mostrar mensaje de pausa
        canvas.create_text(
            GAME_WIDTH / 2, GAME_HEIGHT / 2,
            text="PAUSADO", font=("Arial", 30, "bold"), fill="white", tags="pause_msg"
        )
    else:
        # Quitar mensaje y reanudar el bucle
        canvas.delete("pause_msg")
        game_loop(canvas) # Re-lanzar el bucle

# --- Lógica de JSON ---

def load_high_score():
    try:
        with open(HIGH_SCORE_FILE, 'r') as f:
            data = json.load(f)
            return data.get('high_score', 0)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0

def save_high_score(new_score):
    data = {'high_score': new_score}
    try:
        with open(HIGH_SCORE_FILE, 'w') as f:
            json.dump(data, f)
    except IOError as e:
        print(f"No se pudo guardar el récord: {e}")

# --- 4. Funciones de Dibujo (Expandidas) ---

def draw_board_state(canvas):
    """Dibuja el tablero fijo (piezas en el fondo)."""
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            x1, y1 = x * SQUARE_SIZE, y * SQUARE_SIZE
            x2, y2 = x1 + SQUARE_SIZE, y1 + SQUARE_SIZE
            cell_value = board_state[y][x]
            color = PIECE_COLORS[cell_value]
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=GRID_COLOR)

def draw_ghost_piece(canvas):
    """Dibuja la 'sombra' de la pieza en el fondo."""
    if not current_piece: return
    
    shape = get_current_shape()
    piece_x = current_piece['x']
    
    # 1. Encontrar la 'y' fantasma (misma lógica que hard_drop)
    ghost_y = current_piece['y']
    while not check_collision(shape, piece_x, ghost_y + 1):
        ghost_y += 1
        
    # 2. Dibujar la forma en esa 'y'
    for y, row in enumerate(shape):
        for x, cell_value in enumerate(row):
            if cell_value != 0:
                canvas_x = (piece_x + x) * SQUARE_SIZE
                canvas_y = (ghost_y + y) * SQUARE_SIZE
                if canvas_y >= 0:
                    canvas.create_rectangle(canvas_x, canvas_y, 
                                            canvas_x + SQUARE_SIZE, canvas_y + SQUARE_SIZE, 
                                            fill="", outline=GHOST_COLOR, width=2)

def draw_current_piece(canvas):
    """Dibuja la pieza activa que está cayendo."""
    if not current_piece: return
        
    shape = get_current_shape()
    shape_color = PIECE_COLORS[current_piece['shape_index']]
    piece_x = current_piece['x']
    piece_y = current_piece['y']

    for y, row in enumerate(shape):
        for x, cell_value in enumerate(row):
            if cell_value != 0:
                canvas_x = (piece_x + x) * SQUARE_SIZE
                canvas_y = (piece_y + y) * SQUARE_SIZE
                if canvas_y >= 0:
                    canvas.create_rectangle(canvas_x, canvas_y, 
                                            canvas_x + SQUARE_SIZE, canvas_y + SQUARE_SIZE, 
                                            fill=shape_color, outline="white")

def draw_mini_piece(mini_canvas, piece):
    """Función genérica para dibujar en los lienzos 'Next' y 'Hold'."""
    mini_canvas.delete("all")
    if not piece: return
    
    shape_index = piece['shape_index']
    shape = PIECE_SHAPES[shape_index][0] # Usar siempre la rotación 0
    color = PIECE_COLORS[shape_index]
    
    # Centrar la pieza en el lienzo pequeño
    offset_x = (MINI_CANVAS_WIDTH - (len(shape[0]) * SQUARE_SIZE_SMALL)) / 2
    offset_y = (MINI_CANVAS_HEIGHT - (len(shape) * SQUARE_SIZE_SMALL)) / 2
    
    for y, row in enumerate(shape):
        for x, cell_value in enumerate(row):
            if cell_value != 0:
                x1 = offset_x + x * SQUARE_SIZE_SMALL
                y1 = offset_y + y * SQUARE_SIZE_SMALL
                x2 = x1 + SQUARE_SIZE_SMALL
                y2 = y1 + SQUARE_SIZE_SMALL
                mini_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="white")

def draw_game(canvas):
    """Función maestra de dibujo (limpia y dibuja todo)."""
    if game_over_flag: return
    
    canvas.delete("all")
    draw_board_state(canvas)
    draw_ghost_piece(canvas)
    draw_current_piece(canvas)

def show_game_over_message():
    """Muestra 'Game Over' y guarda el récord si es necesario."""
    global high_score
    
    # Guardar récord
    if score > high_score:
        high_score = score
        save_high_score(score)
        high_score_label.config(text=f"Récord:\n{high_score} (¡NUEVO!)")
    
    # Mostrar mensaje
    canvas.create_text(
        GAME_WIDTH / 2, GAME_HEIGHT / 2,
        text="GAME OVER",
        font=("Arial", 30, "bold"),
        fill="red"
    )

# --- 5. Bucle de Juego (Game Loop) ---

def fix_piece_and_next_turn():
    """Función auxiliar para fijar, limpiar, puntuar y crear la siguiente pieza."""
    fix_piece()
    lines_cleared = clear_completed_lines()
    update_score_and_level(lines_cleared)
    create_new_piece()

def game_loop(canvas):
    """El motor principal del juego."""
    if game_over_flag or is_paused:
        return # Detener el bucle si hay pausa o game over

    # 1. Mover la pieza hacia abajo (gravedad)
    if current_piece:
        new_y = current_piece['y'] + 1
        
        # 2. Comprobar colisión vertical
        if not check_collision(get_current_shape(), current_piece['x'], new_y):
            current_piece['y'] = new_y
        else:
            # ¡Colisión! Fijar la pieza y pasar al siguiente turno
            fix_piece_and_next_turn()

    # 3. Redibujar todo
    draw_game(canvas)
    
    # 4. Repetir el bucle
    window.after(get_game_speed(), game_loop, canvas)

# --- 6. Configuración de la Ventana (Layout) ---

def setup_game():
    """Crea la ventana, todos los widgets, y arranca el juego."""
    global window, canvas, score_label, high_score_label, level_label
    global next_canvas, hold_canvas, high_score, next_piece, board_state
    
    window = tk.Tk()
    window.title("Tetris Pulido")
    window.resizable(False, False)
    
    # --- Cargar Récord y Crear Tablero ---
    high_score = load_high_score()
    board_state = create_empty_board()
    
    # --- Crear Frames (Contenedores) ---
    # Frame principal para el tablero de juego
    main_frame = tk.Frame(window, bg=EMPTY_CELL_COLOR)
    main_frame.grid(row=0, column=0)
    
    # Frame lateral para la información
    side_frame = tk.Frame(window, width=SIDE_PANEL_WIDTH, bg="#2c2c2c")
    side_frame.grid(row=0, column=1, sticky="ns") # n_s = estirar verticalmente
    side_frame.pack_propagate(False) # Evitar que el frame se encoja

    # --- 1. Panel Lateral (side_frame) ---
    tk.Label(side_frame, text="TETRIS", font=("Arial", 24, "bold"), fg="white", bg="#2c2c2c").pack(pady=10)
    
    high_score_label = tk.Label(side_frame, text=f"Récord:\n{high_score}", font=("Arial", 16), fg="white", bg="#2c2c2c")
    high_score_label.pack(pady=20)
    
    score_label = tk.Label(side_frame, text=f"Puntuación:\n{score}", font=("Arial", 16), fg="white", bg="#2c2c2c")
    score_label.pack(pady=20)
    
    level_label = tk.Label(side_frame, text=f"Nivel:\n{level}", font=("Arial", 16), fg="white", bg="#2c2c2c")
    level_label.pack(pady=20)
    
    # --- Lienzo 'Hold' ---
    tk.Label(side_frame, text="HOLD (C)", font=("Arial", 14), fg="white", bg="#2c2c2c").pack(pady=(10, 0))
    hold_canvas = tk.Canvas(side_frame, width=MINI_CANVAS_WIDTH, height=MINI_CANVAS_HEIGHT, bg="black", highlightthickness=0)
    hold_canvas.pack()
    
    # --- Lienzo 'Next' ---
    tk.Label(side_frame, text="NEXT", font=("Arial", 14), fg="white", bg="#2c2c2c").pack(pady=(20, 0))
    next_canvas = tk.Canvas(side_frame, width=MINI_CANVAS_WIDTH, height=MINI_CANVAS_HEIGHT, bg="black", highlightthickness=0)
    next_canvas.pack()

    # --- Instrucciones ---
    tk.Label(side_frame, text="Pausa: P", font=("Arial", 12), fg="grey", bg="#2c2c2c").pack(pady=(30, 0))
    
    # --- 2. Panel Principal (main_frame) ---
    canvas = tk.Canvas(main_frame, 
                       width=GAME_WIDTH, 
                       height=GAME_HEIGHT, 
                       bg=EMPTY_CELL_COLOR,
                       highlightthickness=0)
    canvas.pack()

    # --- 3. Vínculos del Teclado (Key Binds) ---
    # El 'lambda event:' es necesario para que la función acepte el
    # argumento 'event' que Tkinter envía automáticamente.
    window.bind("<Left>", lambda event: move_piece(-1))
    window.bind("<Right>", lambda event: move_piece(1))
    window.bind("<Up>", lambda event: rotate_piece())
    window.bind("<Down>", lambda event: game_loop(canvas)) # Acelera la caída (Soft Drop)
    window.bind("<space>", lambda event: hard_drop())
    window.bind("<c>", lambda event: hold_piece())
    window.bind("<p>", lambda event: toggle_pause())

    # --- 4. Iniciar el Juego ---
    # Preparar las primeras piezas
    next_piece = get_random_piece()
    create_new_piece()
    
    # Iniciar el bucle
    game_loop(canvas)
    window.mainloop()

# --- 7. Iniciar el Juego ---
if __name__ == "__main__":
    setup_game()