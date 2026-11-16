# GameDex

**GameDex** es una aplicación de escritorio desarrollada en **Python** con **PySide6** y **SQLite3** destinada a catalogar, organizar y gestionar una biblioteca personal de videojuegos. 

Este proyecto ha sido diseñado aplicando principios avanzados de **Diseño de Interfaces (DI)**: jerarquía visual, diseño modular mediante Qt Designer, creación de componentes gráficos reutilizables, usabilidad, accesibilidad y persistencia de datos local.

---

## Tabla de Contenidos
- [Características Principales](#-características-principales)
- [Tecnologías Utilizadas](#-tecnologías-utilizadas)
- [Arquitectura del Proyecto](#-arquitectura-del-proyecto)
- [Requisitos Previos e Instalación](#-requisitos-previos-e-instalación)
- [Uso de la Aplicación](#-uso-de-la-aplicación)
- [Esquema de Base de Datos](#-esquema-de-base-de-datos)
- [Usabilidad y Accesibilidad](#-usabilidad-y-accesibilidad)
- [Equipo de Desarrollo](#-equipo-de-desarrollo)

---

## Características Principales

* **Gestión CRUD Completa:** Añade, visualiza, edita y elimina videojuegos de tu colección con validación de campos en tiempo real.
* **Catálogo Visual Dinámico:** Vista principal (*Dashboard*) que renderiza los juegos mediante tarjetas personalizadas (`GameCard`).
* **Búsqueda y Filtrado Instantáneo:** Barra de búsqueda en tiempo real por título y filtros dinámicos por género y plataforma.
* **Persistencia Automática:** Creación e inicialización automática de la base de datos SQLite y sus tablas al arrancar la aplicación si no existen previamente.
* **Interfaz Adaptable (Responsive):** Uso estricto de *Layouts* (`QVBoxLayout`, `QHBoxLayout`, `QGridLayout`) para evitar solapamientos al redimensionar la ventana.
* **Confirmaciones y Feedback:** Diálogos modales de confirmación antes de realizar acciones destructivas (eliminación) y mensajes claros de éxito o error.

---

## Tecnologías Utilizadas

| Tecnología / Herramienta | Propósito en el proyecto |
| :--- | :--- |
| **Python 3.10+** | Lenguaje principal y lógica de negocio (POO). |
| **PySide6 (Qt6)** | Motor gráfico y renderizado de la interfaz de usuario. |
| **Qt Designer** | Diseño visual modular de vistas y formularios (`.ui`). |
| **SQLite 3** | Motor de base de datos relacional local ligero. |
| **Git & GitHub** | Control de versiones y flujo de trabajo colaborativo. |

---

## Arquitectura del Proyecto

El repositorio sigue una estructura modular limpia para separar la lógica de negocio, la capa de datos y la capa de presentación:

```text
GameDex/
│
├── main.py                 # Punto de entrada principal de la aplicación
├── database.py             # Gestión de conexión, inicialización y consultas SQLite
├── requirements.txt        # Dependencias del proyecto
├── README.md               # Documentación del repositorio
├── README.pdf              # Memoria entregable del proyecto
│
├── ui/                     # Interfaces visuales diseñadas en Qt Designer
│   ├── main_window.ui      # Ventana principal y estructura de navegación
│   └── game_form.ui        # Formulario modal/vista para alta y edición
│
├── components/             # Componentes gráficos propios y reutilizables
│   └── game_card.py        # Widget personalizado (QFrame/QWidget) para cada juego
│
└── resources/              # Recursos estáticos (cargados mediante rutas relativas)
    ├── images/             # Carátulas por defecto y recursos gráficos
    └── icons/              # Iconografía de la interfaz (editar, borrar, buscar...)
