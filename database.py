
# ==========================================
# GAMEDEX
# Archivo: database.py
# Gestión de la base de datos SQLite
# ==========================================

import sqlite3
import os


# ==========================================
# RUTA DE LA BASE DE DATOS
# ==========================================

# Obtenemos la carpeta donde está este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construimos la ruta de gamedex.db
DB_PATH = os.path.join(BASE_DIR, "gamedex.db")


# ==========================================
# CONEXIÓN CON SQLITE
# ==========================================

def conectar():
    """
    Abre una conexión con la base de datos.
    Devuelve el objeto conexión.
    """

    return sqlite3.connect(DB_PATH)


# ==========================================
# INICIALIZAR BASE DE DATOS
# ==========================================

def inicializar_bd():
    """
    Crea la tabla videojuegos si todavía no existe.
    Se ejecuta al iniciar GameDex.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videojuegos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                genero TEXT,
                plataforma TEXT,
                anio INTEGER,
                puntuacion REAL
            )
        """)

        conexion.commit()

    finally:
        conexion.close()


# ==========================================
# VALIDAR LOS DATOS
# ==========================================

def validar_videojuego(titulo, anio, puntuacion):
    """
    Comprueba que los datos del videojuego sean correctos.

    El título es obligatorio.
    El año debe ser un entero entre 1950 y 2100.
    La puntuación debe estar entre 1 y 5.
    """

    # Comprobar que el título no esté vacío
    if not titulo or not titulo.strip():
        raise ValueError("El título es obligatorio.")

    # Validar el año
    if anio is not None:

        try:
            anio = int(anio)

        except (ValueError, TypeError):
            raise ValueError("El año debe ser un número entero.")

        if anio < 1950 or anio > 2100:
            raise ValueError(
                "El año debe estar entre 1950 y 2100."
            )

    # Validar puntuación
    if puntuacion is not None:

        try:
            puntuacion = float(puntuacion)

        except (ValueError, TypeError):
            raise ValueError(
                "La puntuación debe ser numérica."
            )

        if puntuacion < 1 or puntuacion > 5:
            raise ValueError(
                "La puntuación debe estar entre 1 y 5."
            )

    # Devolvemos los datos corregidos
    return titulo.strip(), anio, puntuacion


# ==========================================
# AÑADIR VIDEOJUEGO
# ==========================================

def agregar_videojuego(titulo, genero, plataforma, anio, puntuacion):
    """
    Inserta un videojuego nuevo en SQLite.
    """

    # Validamos los datos antes de guardarlos
    titulo, anio, puntuacion = validar_videojuego(
        titulo, anio, puntuacion
    )

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO videojuegos
            (titulo, genero, plataforma, anio, puntuacion)
            VALUES (?, ?, ?, ?, ?)
        """, (
            titulo,
            genero,
            plataforma,
            anio,
            puntuacion
        ))

        conexion.commit()

        # Devolvemos el identificador del videojuego creado
        return cursor.lastrowid

    finally:
        conexion.close()


# ==========================================
# OBTENER TODOS LOS VIDEOJUEGOS
# ==========================================

def obtener_videojuegos():
    """
    Devuelve todos los videojuegos almacenados.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT * FROM videojuegos
            ORDER BY titulo COLLATE NOCASE
        """)

        return cursor.fetchall()

    finally:
        conexion.close()


# ==========================================
# EDITAR VIDEOJUEGO
# ==========================================

def editar_videojuego(id, titulo, genero, plataforma, anio, puntuacion):
    """
    Modifica los datos de un videojuego existente.
    """

    # Validamos los datos
    titulo, anio, puntuacion = validar_videojuego(
        titulo, anio, puntuacion
    )

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE videojuegos
            SET titulo = ?,
                genero = ?,
                plataforma = ?,
                anio = ?,
                puntuacion = ?
            WHERE id = ?
        """, (
            titulo,
            genero,
            plataforma,
            anio,
            puntuacion,
            id
        ))

        conexion.commit()

        # True si se ha modificado algún registro
        return cursor.rowcount > 0

    finally:
        conexion.close()


# ==========================================
# ELIMINAR VIDEOJUEGO
# ==========================================

def eliminar_videojuego(id):
    """
    Elimina un videojuego utilizando su identificador.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            DELETE FROM videojuegos
            WHERE id = ?
        """, (id,))

        conexion.commit()

        return cursor.rowcount > 0

    finally:
        conexion.close()


# ==========================================
# BUSCAR VIDEOJUEGOS
# ==========================================

def buscar_videojuegos(texto):
    """
    Busca videojuegos cuyo título contenga el texto indicado.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT * FROM videojuegos
            WHERE titulo LIKE ?
            ORDER BY titulo COLLATE NOCASE
        """, (f"%{texto}%",))

        return cursor.fetchall()

    finally:
        conexion.close()


# ==========================================
# FILTRAR VIDEOJUEGOS
# ==========================================

def filtrar_videojuegos(genero=None, plataforma=None, texto=None):
    """
    Filtra los videojuegos por género, plataforma y título.

    Los parámetros son opcionales.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        # Consulta inicial
        consulta = """
            SELECT * FROM videojuegos
            WHERE 1=1
        """

        parametros = []

        # Aplicar filtro de género
        if genero:
            consulta += " AND genero = ?"
            parametros.append(genero)

        # Aplicar filtro de plataforma
        if plataforma:
            consulta += " AND plataforma = ?"
            parametros.append(plataforma)

        # Aplicar búsqueda por título
        if texto:
            consulta += " AND titulo LIKE ?"
            parametros.append(f"%{texto}%")

        consulta += " ORDER BY titulo COLLATE NOCASE"

        cursor.execute(consulta, parametros)

        return cursor.fetchall()

    finally:
        conexion.close()


# ==========================================
# OBTENER PLATAFORMAS
# ==========================================

def obtener_plataformas():
    """
    Devuelve las plataformas diferentes existentes.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT DISTINCT plataforma
            FROM videojuegos
            WHERE plataforma IS NOT NULL
              AND TRIM(plataforma) != ''
            ORDER BY plataforma
        """)

        resultados = cursor.fetchall()

        return [fila[0] for fila in resultados]

    finally:
        conexion.close()


# ==========================================
# OBTENER GÉNEROS
# ==========================================

def obtener_generos():
    """
    Devuelve los géneros diferentes existentes.
    """

    conexion = conectar()

    try:
        cursor = conexion.cursor()

        cursor.execute("""
            SELECT DISTINCT genero
            FROM videojuegos
            WHERE genero IS NOT NULL
              AND TRIM(genero) != ''
            ORDER BY genero
        """)

        resultados = cursor.fetchall()

        return [fila[0] for fila in resultados]

    finally:
        conexion.close()
