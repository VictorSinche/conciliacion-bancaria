from database.conexion import obtener_conexion


def monto_soles_conciliados():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(t.monto), 0)
        FROM conciliacion c
        INNER JOIN transacciones_bancarias t
            ON c.transaccion_id = t.id
        WHERE t.moneda = 'PEN'
          AND t.estado_conciliacion = 'conciliado'
    """)

    total = cursor.fetchone()[0]
    conexion.close()

    print("\n===== MONTO EN SOLES CONCILIADOS =====")
    print(f"Total conciliado en PEN: S/. {total:.2f}")


def facturas_conciliadas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT co.moneda,
               COUNT(*) AS cantidad,
               COALESCE(SUM(co.total), 0) AS total
        FROM conciliacion c
        INNER JOIN comprobantes co
            ON c.comprobante_id = co.id
        WHERE co.tipo_codigo = '01'
          AND co.estado_conciliacion = 'conciliado'
        GROUP BY co.moneda
        ORDER BY co.moneda
    """)

    resultados = cursor.fetchall()
    conexion.close()

    print("\n===== FACTURAS CONCILIADAS =====")

    if not resultados:
        print("No hay facturas conciliadas registradas.")
        return

    total_facturas = 0

    for moneda, cantidad, total in resultados:
        total_facturas += cantidad
        simbolo = "S/." if moneda == "PEN" else "$"
        print(f"Moneda: {moneda} | Facturas: {cantidad} | Monto: {simbolo} {total:.2f}")

    print(f"Total de facturas conciliadas: {total_facturas}")


def ingresos_mes_conciliacion():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m', t.fecha_operacion) AS mes,
               t.moneda,
               COUNT(*) AS cantidad,
               COALESCE(SUM(t.monto), 0) AS total
        FROM conciliacion c
        INNER JOIN transacciones_bancarias t
            ON c.transaccion_id = t.id
        WHERE t.estado_conciliacion = 'conciliado'
          AND t.tipo_operacion = 'credito'
        GROUP BY mes, t.moneda
        ORDER BY mes DESC, t.moneda
    """)

    resultados = cursor.fetchall()
    conexion.close()

    print("\n===== INGRESOS DEL MES POR CONCILIACIÓN =====")

    if not resultados:
        print("No hay ingresos conciliados registrados.")
        return

    for mes, moneda, cantidad, total in resultados:
        simbolo = "S/." if moneda == "PEN" else "$"
        print(
            f"Mes: {mes} | Moneda: {moneda} | "
            f"Transacciones: {cantidad} | Total: {simbolo} {total:.2f}"
        )


def menu_estadisticas():
    while True:
        print("\n===== MÓDULO DE ESTADÍSTICAS =====")
        print("1. Monto en soles conciliados")
        print("2. Número y monto de facturas conciliadas")
        print("3. Ingresos del mes por conciliación")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            monto_soles_conciliados()
        elif opcion == "2":
            facturas_conciliadas()
        elif opcion == "3":
            ingresos_mes_conciliacion()
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")