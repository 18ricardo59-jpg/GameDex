# Ejecuta: python diagnostico.py   (no necesita PySide6)
import database
print("Ruta BD:", database.DB_PATH)
database.inicializar_bd()
filas = database.obtener_videojuegos()
print("Videojuegos en la BD:", len(filas))
for f in filas:
    print("  ", f)
try:
    import PySide6
    print("PySide6:", PySide6.__version__)
except ImportError:
    print("PySide6 NO está instalado")
