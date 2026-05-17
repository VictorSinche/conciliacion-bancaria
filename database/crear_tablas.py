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
            estado_conciliacion TEXT NOT NULL DEFAULT 'pendiente'
                CHECK(estado_conciliacion IN ('pendiente', 'conciliado')),
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comprobantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_comprobante TEXT NOT NULL CHECK(tipo_comprobante IN ('factura', 'boleta', 'nota_credito', 'nota_debito')),
            tipo_codigo TEXT NOT NULL CHECK(tipo_codigo IN ('01', '03', '07', '08')),
            serie TEXT NOT NULL,
            numero_correlativo TEXT NOT NULL,
            fecha_emision TEXT NOT NULL,
            fecha_vencimiento TEXT NOT NULL,
            fecha_pago TEXT,
            ruc_dni TEXT NOT NULL,
            nombre_emisor TEXT NOT NULL,
            moneda TEXT NOT NULL CHECK(moneda IN ('PEN', 'USD')),
            subtotal REAL NOT NULL CHECK(subtotal > 0),
            igv REAL NOT NULL CHECK(igv >= 0),
            total REAL NOT NULL CHECK(total > 0),
            estado_conciliacion TEXT NOT NULL DEFAULT 'pendiente'
                CHECK(estado_conciliacion IN ('pendiente', 'conciliado')),
            fecha_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(serie, numero_correlativo)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conciliacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaccion_id INTEGER NOT NULL UNIQUE,
            comprobante_id INTEGER NOT NULL UNIQUE,
            fecha_conciliacion TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(transaccion_id)
                REFERENCES transacciones_bancarias(id)
                ON DELETE CASCADE,

            FOREIGN KEY(comprobante_id)
                REFERENCES comprobantes(id)
                ON DELETE CASCADE
        )
    """)

    conexion.commit()
    conexion.close()