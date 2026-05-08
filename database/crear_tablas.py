from database.conexion import obtener_conexion


def crear_tablas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transacciones_bancarias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_operacion TEXT NOT NULL,
            numero_operacion TEXT NOT NULL UNIQUE,
            tipo_operacion TEXT NOT NULL CHECK(tipo_operacion IN ('credito', 'debito')),
            moneda TEXT NOT NULL CHECK(moneda IN ('PEN', 'USD')),
            monto REAL NOT NULL CHECK(monto > 0),
            cuenta_destino TEXT NOT NULL,
            descripcion TEXT,
            estado_conciliacion TEXT DEFAULT 'pendiente',
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comprobantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            serie TEXT NOT NULL,
            numero_documento TEXT NOT NULL,
            fecha_emision TEXT NOT NULL,
            moneda TEXT NOT NULL CHECK(moneda IN ('PEN', 'USD')),
            monto REAL NOT NULL CHECK(monto > 0),
            tipo_comprobante TEXT NOT NULL,
            cliente TEXT NOT NULL,
            estado_conciliacion TEXT DEFAULT 'pendiente'
        )
    """)

    conexion.commit()
    conexion.close()