from database.conexion import obtener_conexion


TRANSACCIONES_INICIALES = [
    ("2026-05-02", "OP-200001", "credito", "PEN", 1500.00, "001-000111", "Pago factura F001-1001", "pendiente"),
    ("2026-05-03", "OP-200002", "credito", "USD", 1200.00, "001-000111", "Transferencia cliente", "pendiente"),
    ("2026-05-04", "OP-200003", "debito", "PEN", 850.00, "001-000111", "Pago proveedor", "pendiente"),
    ("2026-05-05", "OP-200004", "credito", "PEN", 3000.00, "001-000111", "Abono cliente ACME", "conciliado"),
    ("2026-05-07", "OP-200005", "credito", "PEN", 900.00, "001-000111", "Pago venta F001-1005", "pendiente"),
    ("2026-05-08", "OP-200006", "credito", "PEN", 700.00, "001-000111", "Cobranza antigua", "conciliado"),
]

COMPROBANTES_INICIALES = [
    ("F001", "1001", "2026-05-01", "PEN", 1500.00, "factura", "Cliente Andino", "pendiente"),
    ("F001", "1002", "2026-05-02", "USD", 1200.00, "factura", "Global Export", "pendiente"),
    ("F001", "1003", "2026-05-03", "PEN", 3000.00, "factura", "ACME S.A.", "conciliado"),
    ("F001", "1004", "2026-05-09", "PEN", 900.00, "factura", "Cliente Norte", "pendiente"),
    ("B001", "2001", "2026-05-06", "PEN", 700.00, "boleta", "Cliente Retail", "conciliado"),
]

PARES_CONCILIADOS = [
    ("OP-200004", "F001", "1003"),
    ("OP-200006", "B001", "2001"),
]


def cargar_tablas():

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("DELETE FROM conciliacion")
    cursor.execute("DELETE FROM comprobantes")
    cursor.execute("DELETE FROM transacciones_bancarias")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('transacciones_bancarias', 'comprobantes', 'conciliacion')")

    cursor.executemany(
        """
        INSERT INTO transacciones_bancarias (
            fecha_operacion,
            numero_operacion,
            tipo_operacion,
            moneda,
            monto,
            cuenta_destino,
            descripcion,
            estado_conciliacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        TRANSACCIONES_INICIALES,
    )

    cursor.executemany(
        """
        INSERT INTO comprobantes (
            serie,
            numero_documento,
            fecha_emision,
            moneda,
            monto,
            tipo_comprobante,
            cliente,
            estado_conciliacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        COMPROBANTES_INICIALES,
    )

    for numero_operacion, serie, numero_documento in PARES_CONCILIADOS:
        cursor.execute(
            """
            SELECT id
            FROM transacciones_bancarias
            WHERE numero_operacion = ?
            """,
            (numero_operacion,),
        )
        transaccion = cursor.fetchone()

        cursor.execute(
            """
            SELECT id
            FROM comprobantes
            WHERE serie = ? AND numero_documento = ?
            """,
            (serie, numero_documento),
        )
        comprobante = cursor.fetchone()

        if transaccion and comprobante:
            cursor.execute(
                """
                INSERT INTO conciliacion (transaccion_id, comprobante_id)
                VALUES (?, ?)
                """,
                (transaccion[0], comprobante[0]),
            )

    conexion.commit()
    conexion.close()

    print("Carga inicial completada en transacciones, comprobantes y conciliacion.")
