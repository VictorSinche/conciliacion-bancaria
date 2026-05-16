from database.conexion import obtener_conexion

# Estadísticas de monto en soles conciliados
def monto_soles_conciliados():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(monto), 0)
        FROM transacciones_bancarias
        WHERE estado_conciliacion = 'conciliado'
          AND moneda = 'PEN'
    """)
    total = cursor.fetchone()[0]
    conexion.close()

    print("MONTO EN SOLES CONCILIADOS")
    print(f"Total conciliado en PEN: S/. {total:.2f}")

# Estadísticas de facturas conciliadas  
def facturas_conciliadas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT COUNT(*), COALESCE(SUM(total), 0)
        FROM comprobantes
        WHERE estado_conciliacion = 'conciliado'
          AND tipo_codigo = '01'
    """)
    resultado = cursor.fetchone()
    conexion.close()

    cantidad = resultado[0]
    total = resultado[1]

    print("\n===== FACTURAS CONCILIADAS =====")
    print(f"Número de facturas conciliadas : {cantidad}")
    print(f"Monto total conciliado         : {total:.2f}")

# Estadísticas de ingresos del mes por conciliación
def ingresos_mes_conciliacion():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT strftime('%Y-%m', fecha_operacion) AS mes,
               COUNT(*) AS cantidad,
               SUM(monto) AS total
        FROM transacciones_bancarias
        WHERE estado_conciliacion = 'conciliado'
          AND tipo_operacion = 'credito'
        GROUP BY mes
        ORDER BY mes DESC
    """)
    resultados = cursor.fetchall()
    conexion.close()

    print("\n===== INGRESOS DEL MES POR CONCILIACIÓN =====")

    if not resultados:
        print("No hay ingresos conciliados registrados.")
        return

    for fila in resultados:
        print(f"Mes: {fila[0]} | Transacciones: {fila[1]} | Total: S/. {fila[2]:.2f}")


# Menú de estadísticas
def menu_estadisticas():
    while True:
        print("\n===== MÓDULO DE ESTADÍSTICAS =====")
        print("1. Monto en soles conciliados")
        print("2. Número y monto de facturas conciliadas")
        print("3. Ingresos del mes por conciliación")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

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