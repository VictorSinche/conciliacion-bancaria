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
    ("factura", "01", "F001", "00001001", "2026-05-01", "2026-05-31", None, "20100000001", "Cliente Andino", "PEN", 1271.19, 228.81, 1500.00, "pendiente"),
    ("factura", "01", "F001", "00001002", "2026-05-02", "2026-05-31", None, "20100000002", "Global Export", "USD", 1016.95, 183.05, 1200.00, "pendiente"),
    ("factura", "01", "F001", "00001003", "2026-05-03", "2026-05-31", "2026-05-05", "20100000003", "ACME S.A.", "PEN", 2542.37, 457.63, 3000.00, "conciliado"),
    ("factura", "01", "F001", "00001004", "2026-05-09", "2026-05-31", None, "20100000004", "Cliente Norte", "PEN", 762.71, 137.29, 900.00, "pendiente"),
    ("boleta", "03", "B001", "00002001", "2026-05-06", "2026-05-06", "2026-05-08", "10100000001", "Cliente Retail", "PEN", 593.22, 106.78, 700.00, "conciliado"),
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
            tipo_comprobante,
            tipo_codigo,
            serie,
            numero_correlativo,
            fecha_emision,
            fecha_vencimiento,
            fecha_pago,
            ruc_dni,
            nombre_emisor,
            moneda,
            subtotal,
            igv,
            total,
            estado_conciliacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        COMPROBANTES_INICIALES,
    )

    for numero_operacion, serie, numero_correlativo in PARES_CONCILIADOS:
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
            WHERE serie = ? AND numero_correlativo = ?
            """,
            (serie, numero_correlativo),
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
