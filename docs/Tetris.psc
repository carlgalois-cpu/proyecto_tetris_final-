Algoritmo Tetris
    // --- 1. CONFIGURACIÓN INICIAL ---
    Definir tablero, fila, col Como Entero;
    // El tablero será de 20 filas y 10 columnas
    Dimension tablero[20, 10];
    
    Definir juego_activo Como Logico;
    Definir tecla_presionada Como Caracter;
    
    // Inicializamos el tablero "limpio" (lleno de ceros)
    Para fila <- 1 Hasta 20 Hacer
        Para col <- 1 Hasta 10 Hacer
            tablero[fila, col] <- 0;
        FinPara
    FinPara
    
    juego_activo <- Verdadero;
    
    // --- 2. BUCLE DEL JUEGO (Aquí ocurre la magia) ---
    Mientras juego_activo = Verdadero Hacer
        
        // Limpiamos pantalla para dibujar de nuevo
        Limpiar Pantalla;
        Escribir "--- TETRIS (Simulado) ---";
        
        // Dibujamos el tablero (Simplificado para ver que funciona)
        Para fila <- 1 Hasta 20 Hacer
            // Dibujar una línea del tablero
            Escribir "| . . . . . . . . . . |"; 
        FinPara
        Escribir "-----------------------";
        
        // Pedimos movimiento al usuario
        Escribir "Escribe A (izq), D (der), S (bajar) y pulsa Enter:";
        Leer tecla_presionada;
        
        // Decidimos qué hacer según la tecla
        Segun tecla_presionada Hacer
            "a", "A":
                Escribir ">> Moviendo pieza a la IZQUIERDA...";
                Esperar 1 Segundos;
            "d", "D":
                Escribir ">> Moviendo pieza a la DERECHA...";
                Esperar 1 Segundos;
            "s", "S":
                Escribir ">> Bajando pieza...";
                Esperar 1 Segundos;
            "x", "X":
                // Truco para salir del bucle y terminar
                juego_activo <- Falso;
            De Otro Modo:
                Escribir "Tecla no válida, la pieza cae por gravedad...";
                Esperar 1 Segundos;
        FinSegun
        
    FinMientras
    
    Escribir "GAME OVER - Fin del juego";
FinAlgoritmo