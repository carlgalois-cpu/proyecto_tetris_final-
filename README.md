# 🎮 Tetris Procedural - Proyecto Final

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Linux](https://img.shields.io/badge/Platform-Linux-orange?style=for-the-badge&logo=linux&logoColor=white)
![Status](https://img.shields.io/badge/Status-Terminado-green?style=for-the-badge)

> Una implementación completa y estructurada del clásico juego Tetris, desarrollada en Python utilizando la biblioteca Tkinter con un enfoque procedural y modular.

## 📋 Tabla de Contenidos
- [Descripción](#-descripción)
- [Características](#-características)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Controles](#-controles)
- [Autor](#-autor)

---

## 📖 Descripción
Este proyecto es el resultado final de un análisis profundo de la lógica de programación estructurada. No solo recrea la mecánica del Tetris, sino que implementa sistemas complejos como detección de colisiones, rotación de matrices ("wall kicks") y persistencia de puntuaciones mediante JSON.

## ✨ Características
* **Sistema de Niveles:** La velocidad aumenta progresivamente.
* **Ghost Piece:** Visualización de dónde caerá la pieza.
* **Hold & Next:** Mecánicas modernas para guardar y previsualizar piezas.
* **High Scores:** Guardado automático de récords.
* **Diseño Modular:** Código limpio organizado por responsabilidades (Lógica, Vista, Control).

## 📂 Estructura del Proyecto
El repositorio está organizado de la siguiente manera para mantener el orden profesional:

```text
proyecto_tetris_final/
├── src/               # Código fuente principal
│   └── main.py        # Punto de entrada del juego
├── docs/              # Documentación, diagramas de flujo y lógica
├── assets/            # Recursos gráficos y capturas
└── old_versions/      # Historial de versiones del desarrollo
