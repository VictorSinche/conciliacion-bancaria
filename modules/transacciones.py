from database.conexion import obtener_conexion


def mostrar_transaccion(item):
    print(
        f"ID: {item[0]} | Fecha: {item[1]} | Operación: {item[2]} | "
        f"Tipo: {item[3]} | Moneda: {item[4]} | Monto: {item[5]} | "
        f"Cuenta: {item[6]} | Estado: {item[7]}"
    )


def registrar_transaccion():
    print("\n===== REGISTRAR TRANSACCIÓN BANCARIA =====")

    fecha = input("Fecha de operación YYYY-MM-DD: ")
    numero = input("Número de operación: ")
    tipo = input("Tipo de operación credito/debito: ").lower()
    moneda = input("Moneda PEN/USD: ").upper()

    try:
        monto = float(input("Monto: "))
    except ValueError:
        print("El monto debe ser un número válido.")
        return

    cuenta = input("Cuenta destino: ")
    descripcion = input("Descripción opcional: ")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            INSERT INTO transacciones_bancarias (
                fecha_operacion,
                numero_operacion,
                tipo_operacion,
                moneda,
                monto,
                cuenta_destino,
                descripcion
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (fecha, numero, tipo, moneda, monto, cuenta, descripcion))

        conexion.commit()
        print("Transacción registrada correctamente.")

    except Exception as error:
        print(f"No se pudo registrar la transacción: {error}")

    finally:
        conexion.close()


def listar_transacciones():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha_operacion, numero_operacion, tipo_operacion,
               moneda, monto, cuenta_destino, estado_conciliacion
        FROM transacciones_bancarias
        ORDER BY fecha_operacion DESC
    """)

    transacciones = cursor.fetchall()
    conexion.close()

    print("\n===== LISTADO DE TRANSACCIONES =====")

    if not transacciones:
        print("No hay transacciones registradas.")
        return

    for item in transacciones:
        mostrar_transaccion(item)


def buscar_por_numero_operacion():
    print("\n===== BUSCAR TRANSACCIÓN =====")

    numero = input("Ingrese el número de operación: ")

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha_operacion, numero_operacion, tipo_operacion,
               moneda, monto, cuenta_destino, estado_conciliacion
        FROM transacciones_bancarias
        WHERE numero_operacion = ?
    """, (numero,))

    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        print("\nTransacción encontrada:")
        mostrar_transaccion(resultado)
    else:
        print("No se encontró ninguna transacción con ese número de operación.")


def menu_transacciones():
    while True:
        print("\n===== MÓDULO DE TRANSACCIONES BANCARIAS =====")
        print("1. Registrar transacción")
        print("2. Listar transacciones")
        print("3. Buscar por número de operación")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_transaccion()
        elif opcion == "2":
            listar_transacciones()
        elif opcion == "3":
            buscar_por_numero_operacion()
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")