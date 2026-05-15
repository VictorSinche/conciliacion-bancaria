from database.conexion import obtener_conexion


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
            print("Pendiente: Jesús implementará facturas conciliadas.")
        elif opcion == "3":
            print("Pendiente: Jesús implementará ingresos del mes.")
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")