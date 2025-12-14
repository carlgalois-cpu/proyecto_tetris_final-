import tkinter as tk
import random
import json
import time

# =============================================
# CONFIGURACIÓN DEL JUEGO
# =============================================

# Constantes del tablero
ANCHO_TABLERO = 10
ALTO_TABLERO = 20
TAMANO_BLOQUE = 30

# Velocidad del juego (milisegundos entre movimientos)
VELOCIDAD_JUEGO = 500

# Sistema de puntuación
PUNTOS_POR_LINEA = 100
PUNTOS_POR_NIVEL = 50

# Colores de las piezas
COLORES = [
    "#1a1a1a",  # 0 - Vacío
    "#00f0f0",  # 1 - I (Cian)
    "#f0f000",  # 2 - O (Amarillo) 
    "#a000f0",  # 3 - T (Morado)
    "#00f000",  # 4 - S (Verde)
    "#f00000",  # 5 - Z (Rojo)
    "#0000f0",  # 6 - J (Azul)
    "#f0a000"   # 7 - L (Naranja)
]

# Formas de las piezas (todas las 7 piezas)
FORMAS_PIEZAS = [
    [], # 0. Vacío
    
    # Pieza I
    [
        [[0,0,0,0], 
         [1,1,1,1], 
         [0,0,0,0], 
         [0,0,0,0]],
        [[0,1,0,0], 
         [0,1,0,0], 
         [0,1,0,0], 
         [0,1,0,0]]
    ],
    
    # Pieza O
    [
        [[2,2], 
         [2,2]]
    ],
    
    # Pieza T
    [
        [[0,3,0], 
         [3,3,3], 
         [0,0,0]],
        [[0,3,0], 
         [0,3,3], 
         [0,3,0]],
        [[0,0,0], 
         [3,3,3], 
         [0,3,0]],
        [[0,3,0], 
         [3,3,0], 
         [0,3,0]]
    ],
    
    # Pieza S
    [
        [[0,4,4], 
         [4,4,0], 
         [0,0,0]],
        [[0,4,0], 
         [0,4,4], 
         [0,0,4]]
    ],
    
    # Pieza Z
    [
        [[5,5,0], 
         [0,5,5], 
         [0,0,0]],
        [[0,0,5], 
         [0,5,5], 
         [0,5,0]]
    ],
    
    # Pieza J
    [
        [[6,0,0], 
         [6,6,6], 
         [0,0,0]],
        [[0,6,6], 
         [0,6,0], 
         [0,6,0]],
        [[0,0,0], 
         [6,6,6], 
         [0,0,6]],
        [[0,6,0], 
         [0,6,0], 
         [6,6,0]]
    ],
    
    # Pieza L
    [
        [[0,0,7], 
         [7,7,7], 
         [0,0,0]],
        [[0,7,0], 
         [0,7,0], 
         [0,7,7]],
        [[0,0,0], 
         [7,7,7], 
         [7,0,0]],
        [[7,7,0], 
         [0,7,0], 
         [0,7,0]]
    ]
]

# Archivo para guardar el récord
ARCHIVO_RECORD = "tetris_record.txt"

# =============================================
# VARIABLES GLOBALES DEL JUEGO
# =============================================

# Estado del tablero
tablero = []

# Pieza actual en juego
pieza_actual = None

# Siguiente pieza
siguiente_pieza = None

# Estado del juego
juego_activo = False
juego_pausado = False
juego_terminado = False

# Puntuación y nivel
puntuacion = 0
nivel = 1
lineas_completadas = 0
record = 0

# Elementos de la interfaz
ventana = None
lienzo = None
etiqueta_puntuacion = None
etiqueta_nivel = None
etiqueta_lineas = None
etiqueta_record = None

# =============================================
# FUNCIONES DE PERSISTENCIA DE DATOS
# =============================================

def cargar_record():
    """Carga el récord desde el archivo"""
    global record
    try:
        archivo = open(ARCHIVO_RECORD, "r")
        contenido = archivo.read()
        archivo.close()
        
        if contenido:
            record = int(contenido)
        else:
            record = 0
            
    except FileNotFoundError:
        # Si el archivo no existe, empezamos con record 0
        record = 0
    except ValueError:
        # Si el archivo tiene contenido inválido
        record = 0
        
    return record

def guardar_record():
    """Guarda el récord en el archivo"""
    try:
        archivo = open(ARCHIVO_RECORD, "w")
        archivo.write(str(record))
        archivo.close()
        return True
    except:
        return False

# =============================================
# FUNCIONES DE LÓGICA DEL JUEGO
# =============================================

def crear_tablero_vacio():
    """Crea un tablero vacío lleno de ceros"""
    tablero_vacio = []
    for fila in range(ALTO_TABLERO):
        fila_vacia = []
        for columna in range(ANCHO_TABLERO):
            fila_vacia.append(0)
        tablero_vacio.append(fila_vacia)
    return tablero_vacio

def generar_pieza_aleatoria():
    """Genera una nueva pieza aleatoria"""
    tipo_pieza = random.randint(1, 7)  # Del 1 al 7 (0 es vacío)
    rotacion = 0
    
    # Posición inicial (centrada en la parte superior)
    x = ANCHO_TABLERO // 2 - 1
    y = 0
    
    return {
        'tipo': tipo_pieza,
        'rotacion': rotacion,
        'x': x,
        'y': y
    }

def obtener_forma_pieza(pieza):
    """Obtiene la forma actual de la pieza"""
    if pieza is None:
        return []
    
    tipo = pieza['tipo']
    rotacion = pieza['rotacion']
    
    return FORMAS_PIEZAS[tipo][rotacion]

def verificar_colision(forma, pos_x, pos_y):
    """Verifica si la pieza colisiona con algo"""
    for fila in range(len(forma)):
        for columna in range(len(forma[fila])):
            if forma[fila][columna] != 0:
                # Calcular posición en el tablero
                tablero_x = pos_x + columna
                tablero_y = pos_y + fila
                
                # Verificar si choca con las paredes
                if tablero_x < 0 or tablero_x >= ANCHO_TABLERO:
                    return True
                    
                # Verificar si choca con el suelo
                if tablero_y >= ALTO_TABLERO:
                    return True
                    
                # Verificar si choca con otras piezas (solo si está dentro del tablero)
                if tablero_y >= 0 and tablero[tablero_y][tablero_x] != 0:
                    return True
                    
    return False

def fijar_pieza_en_tablero():
    """Fija la pieza actual en el tablero"""
    global tablero
    
    if pieza_actual is None:
        return
        
    forma = obtener_forma_pieza(pieza_actual)
    tipo_pieza = pieza_actual['tipo']
    
    for fila in range(len(forma)):
        for columna in range(len(forma[fila])):
            if forma[fila][columna] != 0:
                pos_y = pieza_actual['y'] + fila
                pos_x = pieza_actual['x'] + columna
                
                # Solo fijar si está dentro del tablero visible
                if pos_y >= 0:
                    tablero[pos_y][pos_x] = tipo_pieza

def limpiar_lineas_completas():
    """Elimina líneas completas y devuelve cuántas limpió"""
    global tablero, lineas_completadas
    
    lineas_limpiadas = 0
    fila = ALTO_TABLERO - 1  # Empezar desde abajo
    
    while fila >= 0:
        # Verificar si la línea está completa
        linea_completa = True
        for columna in range(ANCHO_TABLERO):
            if tablero[fila][columna] == 0:
                linea_completa = False
                break
                
        if linea_completa:
            # Eliminar la línea completa
            tablero.pop(fila)
            # Añadir nueva línea vacía al principio
            tablero.insert(0, [0 for _ in range(ANCHO_TABLERO)])
            lineas_limpiadas += 1
            lineas_completadas += 1
        else:
            fila -= 1
            
    return lineas_limpiadas

def actualizar_puntuacion(lineas_limpiadas):
    """Actualiza la puntuación basada en líneas limpiadas"""
    global puntuacion, nivel, record
    
    if lineas_limpiadas == 0:
        return
        
    # Calcular puntos
    puntos_ganados = lineas_limpiadas * PUNTOS_POR_LINEA * nivel
    puntuacion += puntos_ganados
    
    # Actualizar nivel cada 5 líneas
    nuevo_nivel = (lineas_completadas // 5) + 1
    if nuevo_nivel != nivel:
        nivel = nuevo_nivel
        
    # Actualizar récord si es necesario
    if puntuacion > record:
        record = puntuacion
        guardar_record()
        
    # Actualizar la interfaz
    actualizar_interfaz()

def crear_nueva_pieza():
    """Crea una nueva pieza y verifica si el juego terminó"""
    global pieza_actual, siguiente_pieza, juego_terminado
    
    # Mover la siguiente pieza a actual
    pieza_actual = siguiente_pieza
    siguiente_pieza = generar_pieza_aleatoria()
    
    # Verificar si la nueva pieza causa game over
    forma = obtener_forma_pieza(pieza_actual)
    if verificar_colision(forma, pieza_actual['x'], pieza_actual['y']):
        juego_terminado = True
        mostrar_mensaje_fin_juego()

def mover_pieza_abajo():
    """Mueve la pieza actual hacia abajo"""
    global pieza_actual, juego_terminado
    
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    # Intentar mover hacia abajo
    nueva_y = pieza_actual['y'] + 1
    forma = obtener_forma_pieza(pieza_actual)
    
    if verificar_colision(forma, pieza_actual['x'], nueva_y):
        # No se puede mover más abajo, fijar la pieza
        fijar_pieza_en_tablero()
        
        # Limpiar líneas completas y actualizar puntuación
        lineas_limpiadas = limpiar_lineas_completas()
        actualizar_puntuacion(lineas_limpiadas)
        
        # Crear nueva pieza
        crear_nueva_pieza()
    else:
        # Se puede mover, actualizar posición
        pieza_actual['y'] = nueva_y

# =============================================
# FUNCIONES DE CONTROL DEL JUEGO
# =============================================

def mover_izquierda():
    """Mueve la pieza actual hacia la izquierda"""
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    nueva_x = pieza_actual['x'] - 1
    forma = obtener_forma_pieza(pieza_actual)
    
    if not verificar_colision(forma, nueva_x, pieza_actual['y']):
        pieza_actual['x'] = nueva_x

def mover_derecha():
    """Mueve la pieza actual hacia la derecha"""
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    nueva_x = pieza_actual['x'] + 1
    forma = obtener_forma_pieza(pieza_actual)
    
    if not verificar_colision(forma, nueva_x, pieza_actual['y']):
        pieza_actual['x'] = nueva_x

def rotar_pieza():
    """Rota la pieza actual"""
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    tipo_pieza = pieza_actual['tipo']
    rotaciones_disponibles = len(FORMAS_PIEZAS[tipo_pieza])
    
    nueva_rotacion = (pieza_actual['rotacion'] + 1) % rotaciones_disponibles
    
    # Guardar rotación original por si hay colisión
    rotacion_original = pieza_actual['rotacion']
    pieza_actual['rotacion'] = nueva_rotacion
    
    forma = obtener_forma_pieza(pieza_actual)
    
    # Si hay colisión, revertir la rotación
    if verificar_colision(forma, pieza_actual['x'], pieza_actual['y']):
        pieza_actual['rotacion'] = rotacion_original

def caida_rapida():
    """Hace que la pieza caiga más rápido"""
    global puntuacion
    
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    # Mover hacia abajo hasta que colisione
    while True:
        nueva_y = pieza_actual['y'] + 1
        forma = obtener_forma_pieza(pieza_actual)
        
        if verificar_colision(forma, pieza_actual['x'], nueva_y):
            break
        else:
            pieza_actual['y'] = nueva_y
            # Bonus de puntos por caída rápida
            puntuacion += 1
            
    # Fijar la pieza y continuar
    fijar_pieza_en_tablero()
    lineas_limpiadas = limpiar_lineas_completas()
    actualizar_puntuacion(lineas_limpiadas)
    crear_nueva_pieza()

def pausar_juego():
    """Pausa o reanuda el juego"""
    global juego_pausado
    
    if juego_terminado:
        return
        
    juego_pausado = not juego_pausado
    
    if juego_pausado:
        mostrar_mensaje_pausa()
    else:
        dibujar_juego()

def reiniciar_juego():
    """Reinicia el juego"""
    global tablero, pieza_actual, siguiente_pieza
    global juego_activo, juego_pausado, juego_terminado
    global puntuacion, nivel, lineas_completadas
    
    # Reiniciar estado del juego
    tablero = crear_tablero_vacio()
    pieza_actual = generar_pieza_aleatoria()
    siguiente_pieza = generar_pieza_aleatoria()
    
    juego_activo = True
    juego_pausado = False
    juego_terminado = False
    
    puntuacion = 0
    nivel = 1
    lineas_completadas = 0
    
    # Cargar récord actual
    cargar_record()
    
    # Actualizar interfaz
    actualizar_interfaz()
    dibujar_juego()

# =============================================
# FUNCIONES DE INTERFAZ GRÁFICA
# =============================================

def dibujar_tablero():
    """Dibuja el tablero en el lienzo"""
    # Limpiar el lienzo
    lienzo.delete("all")
    
    # Dibujar las piezas fijadas en el tablero
    for fila in range(ALTO_TABLERO):
        for columna in range(ANCHO_TABLERO):
            tipo_pieza = tablero[fila][columna]
            if tipo_pieza != 0:
                color = COLORES[tipo_pieza]
                
                x1 = columna * TAMANO_BLOQUE
                y1 = fila * TAMANO_BLOQUE
                x2 = x1 + TAMANO_BLOQUE
                y2 = y1 + TAMANO_BLOQUE
                
                lienzo.create_rectangle(x1, y1, x2, y2, fill=color, outline="#404040")

def dibujar_pieza_actual():
    """Dibuja la pieza actual en el lienzo"""
    if pieza_actual is None:
        return
        
    forma = obtener_forma_pieza(pieza_actual)
    color = COLORES[pieza_actual['tipo']]
    
    for fila in range(len(forma)):
        for columna in range(len(forma[fila])):
            if forma[fila][columna] != 0:
                x = (pieza_actual['x'] + columna) * TAMANO_BLOQUE
                y = (pieza_actual['y'] + fila) * TAMANO_BLOQUE
                
                # Solo dibujar si está en el área visible
                if y >= 0:
                    x1 = x
                    y1 = y
                    x2 = x + TAMANO_BLOQUE
                    y2 = y + TAMANO_BLOQUE
                    
                    lienzo.create_rectangle(x1, y1, x2, y2, fill=color, outline="white")

def dibujar_cuadricula():
    """Dibuja la cuadrícula del tablero"""
    ancho_lienzo = ANCHO_TABLERO * TAMANO_BLOQUE
    alto_lienzo = ALTO_TABLERO * TAMANO_BLOQUE
    
    # Líneas verticales
    for x in range(0, ancho_lienzo + 1, TAMANO_BLOQUE):
        lienzo.create_line(x, 0, x, alto_lienzo, fill="#404040")
    
    # Líneas horizontales
    for y in range(0, alto_lienzo + 1, TAMANO_BLOQUE):
        lienzo.create_line(0, y, ancho_lienzo, y, fill="#404040")

def dibujar_juego():
    """Dibuja todo el juego en el lienzo"""
    dibujar_tablero()
    dibujar_pieza_actual()
    dibujar_cuadricula()
    
    # Mostrar mensajes si es necesario
    if juego_pausado:
        mostrar_mensaje_pausa()
    elif juego_terminado:
        mostrar_mensaje_fin_juego()

def mostrar_mensaje_pausa():
    """Muestra mensaje de pausa"""
    ancho = ANCHO_TABLERO * TAMANO_BLOQUE
    alto = ALTO_TABLERO * TAMANO_BLOQUE
    
    lienzo.create_text(
        ancho // 2, alto // 2,
        text="PAUSA",
        font=("Arial", 30, "bold"),
        fill="white"
    )

def mostrar_mensaje_fin_juego():
    """Muestra mensaje de fin de juego"""
    ancho = ANCHO_TABLERO * TAMANO_BLOQUE
    alto = ALTO_TABLERO * TAMANO_BLOQUE
    
    lienzo.create_text(
        ancho // 2, alto // 2,
        text="GAME OVER",
        font=("Arial", 30, "bold"),
        fill="red"
    )

def actualizar_interfaz():
    """Actualiza los elementos de la interfaz"""
    if etiqueta_puntuacion:
        etiqueta_puntuacion.config(text=f"Puntuación: {puntuacion}")
        
    if etiqueta_nivel:
        etiqueta_nivel.config(text=f"Nivel: {nivel}")
        
    if etiqueta_lineas:
        etiqueta_lineas.config(text=f"Líneas: {lineas_completadas}")
        
    if etiqueta_record:
        etiqueta_record.config(text=f"Récord: {record}")

# =============================================
# BUCLE PRINCIPAL DEL JUEGO
# =============================================

def bucle_principal():
    """Bucle principal del juego"""
    if juego_activo and not juego_pausado and not juego_terminado:
        mover_pieza_abajo()
        dibujar_juego()
    
    # Programar siguiente iteración
    velocidad_actual = max(100, VELOCIDAD_JUEGO - (nivel - 1) * 50)
    ventana.after(velocidad_actual, bucle_principal)

# =============================================
# CONFIGURACIÓN DE LA VENTANA
# =============================================

def configurar_ventana():
    """Configura la ventana principal del juego"""
    global ventana, lienzo
    global etiqueta_puntuacion, etiqueta_nivel, etiqueta_lineas, etiqueta_record
    
    # Crear ventana principal
    ventana = tk.Tk()
    ventana.title("Tetris - Versión 3")
    ventana.resizable(False, False)
    
    # Calcular dimensiones
    ancho_juego = ANCHO_TABLERO * TAMANO_BLOQUE
    alto_juego = ALTO_TABLERO * TAMANO_BLOQUE
    ancho_ventana = ancho_juego + 200  # Espacio para panel lateral
    
    ventana.geometry(f"{ancho_ventana}x{alto_juego}")
    
    # ===== PANEL DE JUEGO =====
    marco_juego = tk.Frame(ventana, bg="#1a1a1a")
    marco_juego.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Lienzo del juego
    lienzo = tk.Canvas(
        marco_juego,
        width=ancho_juego,
        height=alto_juego,
        bg="#1a1a1a",
        highlightthickness=0
    )
    lienzo.pack()
    
    # ===== PANEL LATERAL =====
    marco_lateral = tk.Frame(ventana, width=200, bg="#2c2c2c")
    marco_lateral.pack(side=tk.RIGHT, fill=tk.Y)
    marco_lateral.pack_propagate(False)
    
    # Título
    titulo = tk.Label(
        marco_lateral,
        text="TETRIS",
        font=("Arial", 20, "bold"),
        fg="white",
        bg="#2c2c2c"
    )
    titulo.pack(pady=20)
    
    # Información del juego
    etiqueta_puntuacion = tk.Label(
        marco_lateral,
        text="Puntuación: 0",
        font=("Arial", 14),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_puntuacion.pack(pady=10)
    
    etiqueta_nivel = tk.Label(
        marco_lateral,
        text="Nivel: 1",
        font=("Arial", 14),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_nivel.pack(pady=10)
    
    etiqueta_lineas = tk.Label(
        marco_lateral,
        text="Líneas: 0",
        font=("Arial", 14),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_lineas.pack(pady=10)
    
    etiqueta_record = tk.Label(
        marco_lateral,
        text="Récord: 0",
        font=("Arial", 14),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_record.pack(pady=10)
    
    # Botones de control
    boton_reiniciar = tk.Button(
        marco_lateral,
        text="Reiniciar Juego",
        font=("Arial", 12),
        command=reiniciar_juego,
        bg="#4CAF50",
        fg="white",
        width=15
    )
    boton_reiniciar.pack(pady=20)
    
    boton_pausa = tk.Button(
        marco_lateral,
        text="Pausa (P)",
        font=("Arial", 12),
        command=pausar_juego,
        bg="#FF9800",
        fg="white",
        width=15
    )
    boton_pausa.pack(pady=10)
    
    # Controles
    controles_texto = """
Controles:
← → : Mover
↑ : Rotar
↓ : Bajar rápido
Espacio: Caída instantánea
P : Pausa
    """
    etiqueta_controles = tk.Label(
        marco_lateral,
        text=controles_texto,
        font=("Arial", 10),
        fg="lightgray",
        bg="#2c2c2c",
        justify=tk.LEFT
    )
    etiqueta_controles.pack(pady=20)
    
    # Configurar eventos de teclado
    def manejar_tecla(evento):
        if evento.keysym == 'Left':
            mover_izquierda()
        elif evento.keysym == 'Right':
            mover_derecha()
        elif evento.keysym == 'Up':
            rotar_pieza()
        elif evento.keysym == 'Down':
            mover_pieza_abajo()  # Caída más rápida
        elif evento.keysym == 'space':
            caida_rapida()
        elif evento.keysym == 'p':
            pausar_juego()
            
        dibujar_juego()
    
    ventana.bind('<KeyPress>', manejar_tecla)
    ventana.focus_set()

# =============================================
# FUNCIÓN PRINCIPAL
# =============================================

def main():
    """Función principal que inicia el juego"""
    global tablero, pieza_actual, siguiente_pieza, juego_activo
    
    # Cargar récord
    cargar_record()
    
    # Inicializar juego
    tablero = crear_tablero_vacio()
    pieza_actual = generar_pieza_aleatoria()
    siguiente_pieza = generar_pieza_aleatoria()
    juego_activo = True
    
    # Configurar interfaz
    configurar_ventana()
    
    # Actualizar interfaz por primera vez
    actualizar_interfaz()
    dibujar_juego()
    
    # Iniciar bucle del juego
    bucle_principal()
    
    # Iniciar aplicación
    ventana.mainloop()

# =============================================
# INICIAR JUEGO
# =============================================

if __name__ == "__main__":
    main()