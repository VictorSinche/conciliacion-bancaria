from database.crear_tablas import crear_tablas
from database.conexion import obtener_conexion


TRANSACCIONES_PRUEBA = [
    ("2026-05-01", "OP-100001", "credito", "PEN", 2500.00, "193-654658-65487-154", "Pago de cliente Minera Andina"),
    ("2026-05-02", "OP-100002", "credito", "USD", 1200.50, "193-654658-65487-154", "Pago parcial de factura internacional"),
    ("2026-05-03", "OP-100003", "debito", "PEN", 850.00, "193-654658-65487-154", "Pago a proveedor local"),
    ("2026-05-04", "OP-100004", "credito", "PEN", 4300.00, "193-654658-65487-154", "Cobranza por venta de repuestos"),
    ("2026-05-05", "OP-100005", "debito", "USD", 980.75, "193-654658-65487-154", "Pago a proveedor extranjero"),
    ("2026-05-06", "OP-100006", "credito", "PEN", 1750.00, "193-654658-65487-154", "Abono por factura pendiente"),
    ("2026-05-07", "OP-100007", "debito", "PEN", 620.00, "193-654658-65487-154", "Pago de servicio logístico"),
    ("2026-05-08", "OP-100008", "credito", "USD", 2100.00, "193-654658-65487-154", "Pago de cliente corporativo"),
    ("2026-05-09", "OP-100009", "credito", "PEN", 3900.00, "193-654658-65487-154", "Cobranza de factura B2B"),
    ("2026-05-10", "OP-100010", "debito", "PEN", 1100.00, "193-654658-65487-154", "Pago de obligación tributaria")
]


def insertar_transacciones_prueba():
    crear_tablas()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.executemany("""
        INSERT OR IGNORE INTO transacciones_bancarias (
            fecha_operacion,
            numero_operacion,
            tipo_operacion,
            moneda,
            monto,
            cuenta_destino,
            descripcion
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, TRANSACCIONES_PRUEBA)

    conexion.commit()
    conexion.close()

    print("Datos de prueba insertados correctamente.")


if __name__ == "__main__":
    insertar_transacciones_prueba()