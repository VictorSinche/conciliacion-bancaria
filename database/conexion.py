import sqlite3
from pathlib import Path


RUTA_DB = Path("data/conciliacion_bancaria.db")


def obtener_conexion():
    RUTA_DB.parent.mkdir(exist_ok=True)
    return sqlite3.connect(RUTA_DB)