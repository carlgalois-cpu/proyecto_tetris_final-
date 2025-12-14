import tkinter as tk
from tkinter import messagebox
import random
import json
import time

# =============================================
# CONFIGURACIÓN DEL JUEGO - VERSIÓN 4
# =============================================

# Constantes del tablero
ANCHO_TABLERO = 10
ALTO_TABLERO = 20
TAMANO_BLOQUE = 30

# Sistema de puntuación mejorado
PUNTOS_POR_LINEA = 100
BONUS_NIVEL = 50
BONUS_CAIDA_RAPIDA = 1

# Velocidades por nivel
VELOCIDAD_BASE = 500
VELOCIDAD_MINIMA = 100
REDUCCION_VELOCIDAD = 40

# Colores mejorados
COLORES = [
    "#1a1a1a",  # 0 - Vacío (negro)
    "#00f0f0",  # 1 - I (Cian brillante)
    "#f0f000",  # 2 - O (Amarillo)
    "#a000f0",  # 3 - T (Morado)
    "#00f000",  # 4 - S (Verde)
    "#f00000",  # 5 - Z (Rojo)
    "#0000f0",  # 6 - J (Azul)
    "#f0a000"   # 7 - L (Naranja)
]

# Color de fondo y cuadrícula
COLOR_FONDO = "#1a1a1a"
COLOR_CUADRICULA = "#404040"

# Formas de las piezas (todas las 7 piezas clásicas)
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

# Archivos de datos
ARCHIVO_RECORD = "tetris_record.json"
ARCHIVO_HISTORIAL = "tetris_historial.json"

# =============================================
# VARIABLES GLOBALES DEL JUEGO
# =============================================

# Estado del juego
tablero = []
pieza_actual = None
siguiente_pieza = None
juego_activo = False
juego_pausado = False
juego_terminado = False

# Estadísticas
puntuacion = 0
nivel = 1
lineas_completadas = 0
record = 0
tiempo_inicio = 0

# Elementos de interfaz
ventana = None
lienzo = None
lienzo_siguiente = None
etiqueta_puntuacion = None
etiqueta_nivel = None
etiqueta_lineas = None
etiqueta_record = None
etiqueta_tiempo = None

# =============================================
# FUNCIONES DE PERSISTENCIA DE DATOS - MEJORADAS
# =============================================

def cargar_datos_desde_archivo(nombre_archivo):
    """Carga datos desde un archivo JSON"""
    try:
        with open(nombre_archivo, 'r') as archivo:
            datos = json.load(archivo)
        return datos
    except FileNotFoundError:
        # Si el archivo no existe, devolver datos vacíos
        return {}
    except json.JSONDecodeError:
        messagebox.showerror("Error", f"El archivo {nombre_archivo} está corrupto")
        return {}

def guardar_datos_en_archivo(nombre_archivo, datos):
    """Guarda datos en un archivo JSON"""
    try:
        with open(nombre_archivo, 'w') as archivo:
            json.dump(datos, archivo)
        return True
    except Exception as error:
        messagebox.showerror("Error", f"No se pudo guardar: {error}")
        return False

def cargar_record():
    """Carga el récord desde el archivo"""
    global record
    datos = cargar_datos_desde_archivo(ARCHIVO_RECORD)
    record = datos.get('record', 0)
    return record

def guardar_record():
    """Guarda el récord actual"""
    datos = {'record': record}
    return guardar_datos_en_archivo(ARCHIVO_RECORD, datos)

def guardar_partida_en_historial():
    """Guarda la partida actual en el historial"""
    if puntuacion == 0:
        return  # No guardar partidas con 0 puntos
    
    # Cargar historial existente
    historial = cargar_datos_desde_archivo(ARCHIVO_HISTORIAL)
    
    # Crear lista de partidas si no existe
    if 'partidas' not in historial:
        historial['partidas'] = []
    
    # Crear datos de la partida
    partida = {
        'fecha': time.strftime("%Y-%m-%d %H:%M:%S"),
        'puntuacion': puntuacion,
        'nivel': nivel,
        'lineas': lineas_completadas,
        'tiempo': time.time() - tiempo_inicio
    }
    
    # Agregar partida al historial
    historial['partidas'].append(partida)
    
    # Mantener solo las últimas 10 partidas
    if len(historial['partidas']) > 10:
        historial['partidas'] = historial['partidas'][-10:]
    
    # Guardar historial
    guardar_datos_en_archivo(ARCHIVO_HISTORIAL, historial)

def mostrar_historial():
    """Muestra el historial de partidas"""
    historial = cargar_datos_desde_archivo(ARCHIVO_HISTORIAL)
    
    if 'partidas' not in historial or not historial['partidas']:
        messagebox.showinfo("Historial", "No hay partidas guardadas aún.")
        return
    
    # Crear texto del historial
    texto_historial = "ÚLTIMAS PARTIDAS:\n\n"
    for partida in reversed(historial['partidas']):
        minutos = int(partida['tiempo']) // 60
        segundos = int(partida['tiempo']) % 60
        texto_historial += f"Puntos: {partida['puntuacion']} | Nivel: {partida['nivel']}\n"
        texto_historial += f"Líneas: {partida['lineas']} | Tiempo: {minutos:02d}:{segundos:02d}\n"
        texto_historial += f"Fecha: {partida['fecha']}\n"
        texto_historial += "-" * 30 + "\n"
    
    messagebox.showinfo("Historial de Partidas", texto_historial)

# =============================================
# FUNCIONES DE LÓGICA DEL JUEGO - MEJORADAS
# =============================================

def crear_tablero_vacio():
    """Crea un tablero vacío para empezar el juego"""
    tablero_nuevo = []
    for fila in range(ALTO_TABLERO):
        fila_nueva = []
        for columna in range(ANCHO_TABLERO):
            fila_nueva.append(0)  # 0 representa vacío
        tablero_nuevo.append(fila_nueva)
    return tablero_nuevo

def generar_pieza_aleatoria():
    """Genera una nueva pieza aleatoria"""
    tipo_pieza = random.randint(1, 7)  # Del 1 al 7 (todas las piezas)
    return {
        'tipo': tipo_pieza,
        'rotacion': 0,
        'x': ANCHO_TABLERO // 2 - 1,  # Posición centrada
        'y': 0  # Empieza en la parte superior
    }

def obtener_forma_actual():
    """Obtiene la forma de la pieza actual"""
    if pieza_actual is None:
        return []
    
    tipo = pieza_actual['tipo']
    rotacion = pieza_actual['rotacion']
    return FORMAS_PIEZAS[tipo][rotacion]

def verificar_colision(forma, pos_x, pos_y):
    """Verifica si la pieza colisiona con paredes, suelo u otras piezas"""
    for fila in range(len(forma)):
        for columna in range(len(forma[fila])):
            # Solo verificar celdas que no están vacías
            if forma[fila][columna] != 0:
                tablero_x = pos_x + columna
                tablero_y = pos_y + fila
                
                # Verificar paredes izquierda y derecha
                if tablero_x < 0 or tablero_x >= ANCHO_TABLERO:
                    return True
                
                # Verificar suelo
                if tablero_y >= ALTO_TABLERO:
                    return True
                
                # Verificar otras piezas (solo si está dentro del tablero)
                if tablero_y >= 0 and tablero[tablero_y][tablero_x] != 0:
                    return True
                    
    return False

def fijar_pieza_actual():
    """Fija la pieza actual en el tablero"""
    global tablero
    
    if pieza_actual is None:
        return
        
    forma = obtener_forma_actual()
    tipo_pieza = pieza_actual['tipo']
    
    for fila in range(len(forma)):
        for columna in range(len(forma[fila])):
            if forma[fila][columna] != 0:
                pos_y = pieza_actual['y'] + fila
                pos_x = pieza_actual['x'] + columna
                
                # Solo fijar si está dentro del tablero visible
                if pos_y >= 0:
                    tablero[pos_y][pos_x] = tipo_pieza

def encontrar_lineas_completas():
    """Encuentra y elimina líneas completas, devuelve cuántas eliminó"""
    global tablero, lineas_completadas
    
    lineas_eliminadas = 0
    fila_actual = ALTO_TABLERO - 1  # Empezar desde abajo
    
    while fila_actual >= 0:
        # Verificar si toda la fila está llena
        fila_completa = True
        for columna in range(ANCHO_TABLERO):
            if tablero[fila_actual][columna] == 0:
                fila_completa = False
                break
                
        if fila_completa:
            # Eliminar la fila completa
            tablero.pop(fila_actual)
            # Añadir nueva fila vacía al principio
            tablero.insert(0, [0 for _ in range(ANCHO_TABLERO)])
            lineas_eliminadas += 1
            lineas_completadas += 1
        else:
            fila_actual -= 1
            
    return lineas_eliminadas

def calcular_puntuacion_lineas(cantidad_lineas):
    """Calcula la puntuación ganada por limpiar líneas"""
    if cantidad_lineas == 0:
        return 0
        
    # Sistema de puntuación clásico de Tetris
    if cantidad_lineas == 1:
        return 100 * nivel
    elif cantidad_lineas == 2:
        return 300 * nivel
    elif cantidad_lineas == 3:
        return 500 * nivel
    elif cantidad_lineas == 4:
        return 800 * nivel
    else:
        return cantidad_lineas * 100 * nivel

def actualizar_estadisticas(lineas_limpiadas):
    """Actualiza puntuación, nivel y récord"""
    global puntuacion, nivel, record
    
    if lineas_limpiadas > 0:
        # Sumar puntos por líneas
        puntuacion += calcular_puntuacion_lineas(lineas_limpiadas)
        
        # Actualizar nivel cada 5 líneas
        nuevo_nivel = (lineas_completadas // 5) + 1
        if nuevo_nivel > nivel:
            nivel = nuevo_nivel
            
        # Actualizar récord si es necesario
        if puntuacion > record:
            record = puntuacion
            
    # Actualizar la interfaz
    actualizar_panel_informacion()

def crear_siguiente_pieza():
    """Crea la siguiente pieza y verifica fin del juego"""
    global pieza_actual, siguiente_pieza, juego_terminado
    
    # Mover siguiente pieza a actual
    pieza_actual = siguiente_pieza
    siguiente_pieza = generar_pieza_aleatoria()
    
    # Verificar si el juego debe terminar
    forma = obtener_forma_actual()
    if verificar_colision(forma, pieza_actual['x'], pieza_actual['y']):
        juego_terminado = True
        guardar_partida_en_historial()

def calcular_velocidad_actual():
    """Calcula la velocidad basada en el nivel"""
    velocidad = VELOCIDAD_BASE - ((nivel - 1) * REDUCCION_VELOCIDAD)
    if velocidad < VELOCIDAD_MINIMA:
        return VELOCIDAD_MINIMA
    return velocidad

# =============================================
# FUNCIONES DE CONTROL - MANTENIENDO SIMPLICIDAD
# =============================================

def mover_pieza_abajo():
    """Mueve la pieza actual hacia abajo (gravedad)"""
    global pieza_actual
    
    if pieza_actual is None or juego_terminado or juego_pausado:
        return False
        
    nueva_y = pieza_actual['y'] + 1
    forma = obtener_forma_actual()
    
    if verificar_colision(forma, pieza_actual['x'], nueva_y):
        # No se puede mover más, fijar pieza
        fijar_pieza_actual()
        lineas_limpiadas = encontrar_lineas_completas()
        actualizar_estadisticas(lineas_limpiadas)
        crear_siguiente_pieza()
        return False
    else:
        # Se puede mover, actualizar posición
        pieza_actual['y'] = nueva_y
        return True

def mover_izquierda():
    """Mueve la pieza actual hacia la izquierda"""
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    nueva_x = pieza_actual['x'] - 1
    forma = obtener_forma_actual()
    
    if not verificar_colision(forma, nueva_x, pieza_actual['y']):
        pieza_actual['x'] = nueva_x

def mover_derecha():
    """Mueve la pieza actual hacia la derecha"""
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    nueva_x = pieza_actual['x'] + 1
    forma = obtener_forma_actual()
    
    if not verificar_colision(forma, nueva_x, pieza_actual['y']):
        pieza_actual['x'] = nueva_x

def rotar_pieza():
    """Rota la pieza actual si es posible"""
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    tipo_pieza = pieza_actual['tipo']
    rotaciones_posibles = len(FORMAS_PIEZAS[tipo_pieza])
    
    # Calcular nueva rotación
    nueva_rotacion = (pieza_actual['rotacion'] + 1) % rotaciones_posibles
    
    # Guardar rotación original por si hay colisión
    rotacion_original = pieza_actual['rotacion']
    pieza_actual['rotacion'] = nueva_rotacion
    
    forma_nueva = obtener_forma_actual()
    
    # Si hay colisión, revertir la rotación
    if verificar_colision(forma_nueva, pieza_actual['x'], pieza_actual['y']):
        pieza_actual['rotacion'] = rotacion_original

def caida_rapida():
    """Acelera la caída de la pieza actual"""
    global puntuacion
    
    if pieza_actual is None or juego_terminado or juego_pausado:
        return
        
    # Mover hacia abajo hasta que colisione
    while True:
        nueva_y = pieza_actual['y'] + 1
        forma = obtener_forma_actual()
        
        if verificar_colision(forma, pieza_actual['x'], nueva_y):
            break
        else:
            pieza_actual['y'] = nueva_y
            # Bonus de puntos por caída rápida
            puntuacion += BONUS_CAIDA_RAPIDA
            
    # Fijar la pieza y continuar
    fijar_pieza_actual()
    lineas_limpiadas = encontrar_lineas_completas()
    actualizar_estadisticas(lineas_limpiadas)
    crear_siguiente_pieza()

def pausar_juego():
    """Pausa o reanuda el juego"""
    global juego_pausado
    
    if juego_terminado:
        return
        
    juego_pausado = not juego_pausado
    
    if juego_pausado:
        mostrar_mensaje("JUEGO EN PAUSA", "yellow")
    else:
        dibujar_juego()

def reiniciar_juego():
    """Reinicia completamente el juego"""
    global tablero, pieza_actual, siguiente_pieza
    global juego_activo, juego_pausado, juego_terminado
    global puntuacion, nivel, lineas_completadas, tiempo_inicio
    
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
    tiempo_inicio = time.time()
    
    # Cargar récord
    cargar_record()
    
    # Actualizar interfaz
    actualizar_panel_informacion()
    dibujar_juego()
    dibujar_siguiente_pieza()

# =============================================
# FUNCIONES DE INTERFAZ - MEJORADAS
# =============================================

def dibujar_tablero():
    """Dibuja todas las piezas fijadas en el tablero"""
    for fila in range(ALTO_TABLERO):
        for columna in range(ANCHO_TABLERO):
            tipo_pieza = tablero[fila][columna]
            if tipo_pieza != 0:
                color = COLORES[tipo_pieza]
                x1 = columna * TAMANO_BLOQUE
                y1 = fila * TAMANO_BLOQUE
                x2 = x1 + TAMANO_BLOQUE
                y2 = y1 + TAMANO_BLOQUE
                
                lienzo.create_rectangle(x1, y1, x2, y2, fill=color, outline=COLOR_CUADRICULA)

def dibujar_pieza_actual():
    """Dibuja la pieza actual que está cayendo"""
    if pieza_actual is None:
        return
        
    forma = obtener_forma_actual()
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
        lienzo.create_line(x, 0, x, alto_lienzo, fill=COLOR_CUADRICULA)
    
    # Líneas horizontales
    for y in range(0, alto_lienzo + 1, TAMANO_BLOQUE):
        lienzo.create_line(0, y, ancho_lienzo, y, fill=COLOR_CUADRICULA)

def dibujar_siguiente_pieza():
    """Dibuja la siguiente pieza en el panel lateral"""
    if lienzo_siguiente is None or siguiente_pieza is None:
        return
        
    # Limpiar el lienzo de siguiente pieza
    lienzo_siguiente.delete("all")
    
    forma = FORMAS_PIEZAS[siguiente_pieza['tipo']][0]  # Primera rotación
    color = COLORES[siguiente_pieza['tipo']]
    
    # Centrar la pieza en el lienzo pequeño
    ancho_forma = len(forma[0])
    alto_forma = len(forma)
    
    tamano_mini_bloque = 20
    offset_x = (80 - ancho_forma * tamano_mini_bloque) // 2
    offset_y = (80 - alto_forma * tamano_mini_bloque) // 2
    
    for fila in range(alto_forma):
        for columna in range(ancho_forma):
            if forma[fila][columna] != 0:
                x1 = offset_x + columna * tamano_mini_bloque
                y1 = offset_y + fila * tamano_mini_bloque
                x2 = x1 + tamano_mini_bloque
                y2 = y1 + tamano_mini_bloque
                
                lienzo_siguiente.create_rectangle(x1, y1, x2, y2, fill=color, outline="white")

def dibujar_juego():
    """Dibuja todo el juego en el lienzo principal"""
    lienzo.delete("all")
    dibujar_tablero()
    dibujar_pieza_actual()
    dibujar_cuadricula()
    
    # Mostrar mensajes si es necesario
    if juego_pausado:
        mostrar_mensaje("JUEGO EN PAUSA", "yellow")
    elif juego_terminado:
        mostrar_mensaje("GAME OVER", "red")

def mostrar_mensaje(texto, color):
    """Muestra un mensaje en el centro del lienzo"""
    ancho = ANCHO_TABLERO * TAMANO_BLOQUE
    alto = ALTO_TABLERO * TAMANO_BLOQUE
    
    # Fondo semitransparente
    lienzo.create_rectangle(
        ancho * 0.1, alto * 0.4,
        ancho * 0.9, alto * 0.6,
        fill="black", outline=color, width=2
    )
    
    # Texto del mensaje
    lienzo.create_text(
        ancho // 2, alto // 2,
        text=texto,
        font=("Arial", 24, "bold"),
        fill=color
    )

def actualizar_panel_informacion():
    """Actualiza todas las etiquetas del panel lateral"""
    if etiqueta_puntuacion:
        etiqueta_puntuacion.config(text=f"Puntuación: {puntuacion}")
        
    if etiqueta_nivel:
        etiqueta_nivel.config(text=f"Nivel: {nivel}")
        
    if etiqueta_lineas:
        etiqueta_lineas.config(text=f"Líneas: {lineas_completadas}")
        
    if etiqueta_record:
        etiqueta_record.config(text=f"Récord: {record}")
        
    if etiqueta_tiempo and juego_activo and not juego_terminado:
        tiempo_transcurrido = int(time.time() - tiempo_inicio)
        minutos = tiempo_transcurrido // 60
        segundos = tiempo_transcurrido % 60
        etiqueta_tiempo.config(text=f"Tiempo: {minutos:02d}:{segundos:02d}")

# =============================================
# BUCLE PRINCIPAL DEL JUEGO
# =============================================

def bucle_principal():
    """Bucle principal que controla el juego"""
    if juego_activo and not juego_pausado and not juego_terminado:
        mover_pieza_abajo()
        dibujar_juego()
        actualizar_panel_informacion()
    
    # Programar siguiente iteración
    velocidad = calcular_velocidad_actual()
    ventana.after(velocidad, bucle_principal)

# =============================================
# CONFIGURACIÓN DE LA VENTANA - MEJORADA
# =============================================

def configurar_ventana_principal():
    """Configura toda la interfaz gráfica"""
    global ventana, lienzo, lienzo_siguiente
    global etiqueta_puntuacion, etiqueta_nivel, etiqueta_lineas, etiqueta_record, etiqueta_tiempo
    
    # Crear ventana principal
    ventana = tk.Tk()
    ventana.title("Tetris - Versión 4")
    ventana.resizable(False, False)
    
    # Calcular dimensiones
    ancho_juego = ANCHO_TABLERO * TAMANO_BLOQUE
    alto_juego = ALTO_TABLERO * TAMANO_BLOQUE
    ancho_ventana = ancho_juego + 250  # Más espacio para panel lateral
    
    ventana.geometry(f"{ancho_ventana}x{alto_juego}")
    ventana.configure(bg=COLOR_FONDO)
    
    # ===== MARCO PRINCIPAL DEL JUEGO =====
    marco_juego = tk.Frame(ventana, bg=COLOR_FONDO)
    marco_juego.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Lienzo del juego principal
    lienzo = tk.Canvas(
        marco_juego,
        width=ancho_juego,
        height=alto_juego,
        bg=COLOR_FONDO,
        highlightthickness=0
    )
    lienzo.pack(padx=10, pady=10)
    
    # ===== PANEL LATERAL DE INFORMACIÓN =====
    marco_lateral = tk.Frame(ventana, width=250, bg="#2c2c2c")
    marco_lateral.pack(side=tk.RIGHT, fill=tk.Y)
    marco_lateral.pack_propagate(False)
    
    # Título del juego
    titulo = tk.Label(
        marco_lateral,
        text="TETRIS",
        font=("Arial", 24, "bold"),
        fg="#00f0f0",
        bg="#2c2c2c"
    )
    titulo.pack(pady=20)
    
    # Información del juego
    etiqueta_puntuacion = tk.Label(
        marco_lateral,
        text="Puntuación: 0",
        font=("Arial", 14, "bold"),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_puntuacion.pack(pady=8)
    
    etiqueta_nivel = tk.Label(
        marco_lateral,
        text="Nivel: 1",
        font=("Arial", 14, "bold"),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_nivel.pack(pady=8)
    
    etiqueta_lineas = tk.Label(
        marco_lateral,
        text="Líneas: 0",
        font=("Arial", 14, "bold"),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_lineas.pack(pady=8)
    
    etiqueta_record = tk.Label(
        marco_lateral,
        text="Récord: 0",
        font=("Arial", 14, "bold"),
        fg="gold",
        bg="#2c2c2c"
    )
    etiqueta_record.pack(pady=8)
    
    etiqueta_tiempo = tk.Label(
        marco_lateral,
        text="Tiempo: 00:00",
        font=("Arial", 14, "bold"),
        fg="white",
        bg="#2c2c2c"
    )
    etiqueta_tiempo.pack(pady=8)
    
    # Separador
    separador = tk.Frame(marco_lateral, height=2, bg="#404040")
    separador.pack(fill=tk.X, padx=20, pady=20)
    
    # Siguiente pieza
    tk.Label(
        marco_lateral,
        text="SIGUIENTE PIEZA:",
        font=("Arial", 12, "bold"),
        fg="white",
        bg="#2c2c2c"
    ).pack(pady=5)
    
    lienzo_siguiente = tk.Canvas(
        marco_lateral,
        width=80,
        height=80,
        bg="black",
        highlightthickness=1,
        highlightbackground="#404040"
    )
    lienzo_siguiente.pack(pady=10)
    
    # Botones de control
    boton_reiniciar = tk.Button(
        marco_lateral,
        text="NUEVO JUEGO",
        font=("Arial", 12, "bold"),
        command=reiniciar_juego,
        bg="#4CAF50",
        fg="white",
        width=15,
        height=2
    )
    boton_reiniciar.pack(pady=10)
    
    boton_pausa = tk.Button(
        marco_lateral,
        text="PAUSA (P)",
        font=("Arial", 12, "bold"),
        command=pausar_juego,
        bg="#FF9800",
        fg="white",
        width=15,
        height=2
    )
    boton_pausa.pack(pady=5)
    
    boton_historial = tk.Button(
        marco_lateral,
        text="VER HISTORIAL",
        font=("Arial", 12, "bold"),
        command=mostrar_historial,
        bg="#2196F3",
        fg="white",
        width=15,
        height=2
    )
    boton_historial.pack(pady=10)
    
    # Controles del teclado
    controles_texto = """
CONTROLES:

← → : MOVER
↑    : ROTAR
↓    : BAJAR RÁPIDO
ESPACIO : CAÍDA INSTANTÁNEA
P    : PAUSA
    """
    etiqueta_controles = tk.Label(
        marco_lateral,
        text=controles_texto,
        font=("Arial", 11),
        fg="lightgray",
        bg="#2c2c2c",
        justify=tk.LEFT
    )
    etiqueta_controles.pack(pady=20)
    
    # Configurar eventos de teclado
    def manejar_tecla_presionada(evento):
        if evento.keysym == 'Left':
            mover_izquierda()
        elif evento.keysym == 'Right':
            mover_derecha()
        elif evento.keysym == 'Up':
            rotar_pieza()
        elif evento.keysym == 'Down':
            mover_pieza_abajo()
        elif evento.keysym == 'space':
            caida_rapida()
        elif evento.keysym == 'p':
            pausar_juego()
            
        dibujar_juego()
    
    ventana.bind('<KeyPress>', manejar_tecla_presionada)
    ventana.focus_set()

# =============================================
# FUNCIÓN PRINCIPAL
# =============================================

def main():
    """Función principal que inicia la aplicación"""
    global tablero, pieza_actual, siguiente_pieza, juego_activo, tiempo_inicio
    
    # Cargar récord existente
    cargar_record()
    
    # Inicializar juego
    tablero = crear_tablero_vacio()
    pieza_actual = generar_pieza_aleatoria()
    siguiente_pieza = generar_pieza_aleatoria()
    juego_activo = True
    tiempo_inicio = time.time()
    
    # Configurar interfaz
    configurar_ventana_principal()
    
    # Dibujar estado inicial
    actualizar_panel_informacion()
    dibujar_juego()
    dibujar_siguiente_pieza()
    
    # Iniciar bucle del juego
    bucle_principal()
    
    # Iniciar aplicación
    ventana.mainloop()

# =============================================
# INICIAR APLICACIÓN
# =============================================

if __name__ == "__main__":
    main()