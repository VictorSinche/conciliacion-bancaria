import sqlite3
from datetime import datetime
from database.conexion import obtener_conexion


def mostrar_transaccion(item):
    print(
        f"ID: {item[0]} | Fecha: {item[1]} | Operación: {item[2]} | "
        f"Tipo: {item[3]} | Moneda: {item[4]} | Monto: {item[5]:.2f} | "
        f"Cuenta: {item[6]} | Estado: {item[7]}"
    )


def validar_fecha(fecha):
    try:
        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def registrar_transaccion():
    print("\n===== REGISTRAR TRANSACCIÓN BANCARIA =====")

    fecha = input("Fecha de operación YYYY-MM-DD: ").strip()

    if not validar_fecha(fecha):
        print("La fecha debe tener el formato correcto: YYYY-MM-DD.")
        return

    numero = input("Número de operación: ").strip()

    if not numero:
        print("El número de operación es obligatorio.")
        return

    tipo = input("Tipo de operación credito/debito: ").strip().lower().replace("é", "e")

    if tipo not in ("credito", "debito"):
        print("El tipo de operación debe ser credito o debito.")
        return

    moneda = input("Moneda PEN/USD: ").strip().upper()

    if moneda not in ("PEN", "USD"):
        print("La moneda debe ser PEN o USD.")
        return

    try:
        monto = float(input("Monto: ").strip())

        if monto <= 0:
            print("El monto debe ser mayor que cero.")
            return

    except ValueError:
        print("El monto debe ser un número válido.")
        return

    cuenta = input("Cuenta destino: ").strip()

    if not cuenta:
        print("La cuenta destino es obligatoria.")
        return

    descripcion = input("Descripción opcional: ").strip()

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

    except sqlite3.IntegrityError:
        print("No se pudo registrar la transacción. Verifique que el número de operación no esté repetido.")

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
        ORDER BY fecha_operacion DESC, id DESC
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

    numero = input("Ingrese el número de operación: ").strip()

    if not numero:
        print("Debe ingresar un número de operación.")
        return

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

        opcion = input("Seleccione una opción: ").strip()

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