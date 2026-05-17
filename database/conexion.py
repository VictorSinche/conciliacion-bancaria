import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
RUTA_DB = BASE_DIR / "data" / "conciliacion_bancaria.db"


def obtener_conexion():
    RUTA_DB.parent.mkdir(exist_ok=True)

    conexion = sqlite3.connect(RUTA_DB)
    conexion.execute("PRAGMA foreign_keys = ON")

    return conexion