from database.conexion import obtener_conexion
from datetime import datetime



def validar_fecha(fecha_str, required=False):
    if not fecha_str:
        return None if not required else False
    try:
        datetime.strptime(fecha_str, "%Y-%m-%d")
        return fecha_str
    except ValueError:
        return False


def validar_serie_para_tipo(serie, tipo_codigo):
    if not serie:
        return (False, "La serie no puede estar vacía.")
    if len(serie) > 4:
        return (False, "La serie no puede exceder 4 caracteres.")
    prefijo = SERIES_VALIDAS.get(tipo_codigo)
    if prefijo and not serie.startswith(prefijo):
        return (False, f"La serie debe comenzar con '{prefijo}' para el tipo seleccionado.")
    return (True, None)


def validar_y_normalizar_numero(numero):
    if not numero:
        return (False, "El número correlativo no puede estar vacío.")
    if not numero.isdigit():
        return (False, "El número correlativo debe contener solo dígitos.")
    if len(numero) > 8:
        return (False, "El número correlativo no puede exceder 8 caracteres.")
    numero_padded = numero.zfill(8)
    return (True, numero_padded)


TIPOS_COMPROBANTE = {
    "01": "Factura",
    "03": "Boleta de venta",
    "07": "Nota de crédito",
    "08": "Nota de débito",
}

SERIES_VALIDAS = {
    "01": "F",
    "03": "B",
    "07": "FC",
    "08": "FD",
}


def mostrar_comprobante(item):
    print(
        f"ID: {item[0]} | Fecha emisión: {item[1]} | "
        f"Vencimiento: {item[2] or 'N/A'} | Fecha pago: {item[3] or 'Sin pagar'} | "
        f"Tipo: {item[4]} | Serie: {item[5]}-{item[6]} | "
        f"RUC/DNI: {item[7]} | Emisor: {item[8]} | "
        f"Moneda: {item[9]} | Subtotal: {item[10]:.2f} | "
        f"IGV: {item[11]:.2f} | Total: {item[12]:.2f} | Estado: {item[13]}"
    )


def registrar_comprobante():
    print("\n===== REGISTRAR COMPROBANTE DE PAGO =====")

    print("Tipos de comprobante:")
    for codigo, nombre in TIPOS_COMPROBANTE.items():
        print(f"  {codigo} - {nombre}")

    tipo_codigo = input("Seleccione tipo (01/03/07/08): ").strip()
    if tipo_codigo not in TIPOS_COMPROBANTE:
        print("Tipo de comprobante inválido.")
        return

    tipo_nombre = TIPOS_COMPROBANTE[tipo_codigo]

    serie = input(f"Serie (ej. {SERIES_VALIDAS[tipo_codigo]}001): ").strip().upper()
    ok, msg = validar_serie_para_tipo(serie, tipo_codigo)
    if not ok:
        print(msg)
        return

    numero_input = input("Número correlativo (ej. 00000123): ").strip()
    ok, numero = validar_y_normalizar_numero(numero_input)
    if not ok:
        print(numero)
        return

    fecha_emision = input("Fecha de emisión (YYYY-MM-DD): ").strip()
    fecha_emision_val = validar_fecha(fecha_emision, required=True)
    if fecha_emision_val is False:
        print("Fecha de emisión inválida. Use el formato YYYY-MM-DD.")
        return

    fecha_vencimiento = input("Fecha de vencimiento (YYYY-MM-DD), Enter si es al contado: ").strip()
    fecha_vencimiento_val = validar_fecha(fecha_vencimiento, required=False)
    if fecha_vencimiento_val is False:
        print("Fecha de vencimiento inválida. Use el formato YYYY-MM-DD.")
        return
    if not fecha_vencimiento_val:
        fecha_vencimiento_val = fecha_emision_val

    fecha_pago = input("Fecha de pago real (YYYY-MM-DD), Enter si aún no se pagó: ").strip()
    fecha_pago_val = validar_fecha(fecha_pago, required=False)
    if fecha_pago_val is False:
        print("Fecha de pago inválida. Use el formato YYYY-MM-DD.")
        return
    fecha_pago_val = fecha_pago_val if fecha_pago_val else None

    ruc_dni = input("RUC o DNI del emisor/cliente: ").strip()
    if not ruc_dni.isdigit() or len(ruc_dni) not in (8, 11):
        print("El RUC debe tener 11 dígitos y el DNI 8 dígitos.")
        return

    nombre_emisor = input("Nombre o razón social del emisor/cliente: ").strip()
    if not nombre_emisor:
        print("El nombre no puede estar vacío.")
        return

    moneda = input("Moneda (PEN/USD): ").strip().upper()
    if moneda not in ("PEN", "USD"):
        print("Moneda inválida. Use PEN o USD.")
        return

    try:
        subtotal = float(input("Subtotal (sin IGV): "))
        if subtotal <= 0:
            print("El subtotal debe ser mayor a cero.")
            return
    except ValueError:
        print("El subtotal debe ser un número válido.")
        return

    igv = round(subtotal * 0.18, 2)
    total = round(subtotal + igv, 2)

    print(f"\nResumen del comprobante:")
    print(f"  Tipo           : {tipo_nombre}")
    print(f"  Serie-Número   : {serie}-{numero}")
    print(f"  Emisor         : {nombre_emisor} ({ruc_dni})")
    print(f"  Fecha emisión  : {fecha_emision_val}")
    print(f"  Vencimiento    : {fecha_vencimiento_val}")
    print(f"  Fecha pago     : {fecha_pago_val or 'Sin pagar'}")
    print(f"  Subtotal       : {moneda} {subtotal:.2f}")
    print(f"  IGV (18%)      : {moneda} {igv:.2f}")
    print(f"  Total          : {moneda} {total:.2f}")

    confirmar = input("\n¿Confirmar registro? (s/n): ").strip().lower()
    if confirmar != "s":
        print("Registro cancelado.")
        return

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pendiente')
        """, (
            tipo_nombre, tipo_codigo, serie, numero,
            fecha_emision_val, fecha_vencimiento_val, fecha_pago_val,
            ruc_dni, nombre_emisor, moneda, subtotal, igv, total
        ))

        conexion.commit()
        print("Comprobante registrado correctamente.")

    except Exception as error:
        print(f"No se pudo registrar el comprobante: {error}")

    finally:
        conexion.close()


def registrar_fecha_pago():
    print("\n===== REGISTRAR FECHA DE PAGO =====")
    serie = input("Serie (ej. F001): ").strip().upper()
    numero_input = input("Número correlativo: ").strip()
    fecha_pago = input("Fecha de pago real (YYYY-MM-DD): ").strip()

    # Validaciones
    ok, msg = validar_serie_para_tipo(serie, None)
    if not ok:
        print(msg)
        return
    ok, numero = validar_y_normalizar_numero(numero_input)
    if not ok:
        print(numero)
        return
    fecha_pago_val = validar_fecha(fecha_pago, required=True)
    if fecha_pago_val is False:
        print("Fecha de pago inválida. Use el formato YYYY-MM-DD.")
        return

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        cursor.execute("""
            UPDATE comprobantes
            SET fecha_pago = ?
            WHERE serie = ? AND numero_correlativo = ?
        """, (fecha_pago_val, serie, numero))

        if cursor.rowcount == 0:
            print("No se encontró el comprobante indicado.")
        else:
            conexion.commit()
            print("Fecha de pago registrada correctamente.")

    except Exception as error:
        print(f"Error al actualizar: {error}")

    finally:
        conexion.close()


def listar_comprobantes():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha_emision, fecha_vencimiento, fecha_pago,
               tipo_comprobante, serie, numero_correlativo,
               ruc_dni, nombre_emisor, moneda,
               subtotal, igv, total, estado_conciliacion
        FROM comprobantes
        ORDER BY fecha_emision DESC
    """)

    comprobantes = cursor.fetchall()
    conexion.close()

    print("\n===== LISTADO DE COMPROBANTES =====")

    if not comprobantes:
        print("No hay comprobantes registrados.")
        return

    for item in comprobantes:
        mostrar_comprobante(item)


def listar_pendientes_pago():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha_emision, fecha_vencimiento, fecha_pago,
               tipo_comprobante, serie, numero_correlativo,
               ruc_dni, nombre_emisor, moneda,
               subtotal, igv, total, estado_conciliacion
        FROM comprobantes
        WHERE fecha_pago IS NULL
            AND tipo_codigo IN ('01', '03', '08')
        ORDER BY fecha_vencimiento ASC
    """)

    comprobantes = cursor.fetchall()
    conexion.close()

    print("\n===== COMPROBANTES SIN FECHA DE PAGO =====")

    if not comprobantes:
        print("Todos los comprobantes tienen fecha de pago registrada.")
        return

    for item in comprobantes:
        mostrar_comprobante(item)


def buscar_por_serie_numero():
    print("\n===== BUSCAR COMPROBANTE =====")
    serie = input("Serie (ej. F001): ").strip().upper()
    numero_input = input("Número correlativo: ").strip()

    ok, msg = validar_serie_para_tipo(serie, None)
    if not ok:
        print(msg)
        return
    ok, numero = validar_y_normalizar_numero(numero_input)
    if not ok:
        print(numero)
        return

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha_emision, fecha_vencimiento, fecha_pago,
               tipo_comprobante, serie, numero_correlativo,
               ruc_dni, nombre_emisor, moneda,
               subtotal, igv, total, estado_conciliacion
        FROM comprobantes
        WHERE serie = ? AND numero_correlativo = ?
    """, (serie, numero))

    resultado = cursor.fetchone()
    conexion.close()

    if resultado:
        print("\nComprobante encontrado:")
        mostrar_comprobante(resultado)
    else:
        print("No se encontró ningún comprobante con esa serie y número.")


def buscar_por_ruc():
    print("\n===== BUSCAR POR RUC/DNI =====")

    ruc_dni = input("Ingrese RUC o DNI: ").strip()

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, fecha_emision, fecha_vencimiento, fecha_pago,
               tipo_comprobante, serie, numero_correlativo,
               ruc_dni, nombre_emisor, moneda,
               subtotal, igv, total, estado_conciliacion
        FROM comprobantes
        WHERE ruc_dni = ?
        ORDER BY fecha_emision DESC
    """, (ruc_dni,))

    resultados = cursor.fetchall()
    conexion.close()

    print(f"\n===== COMPROBANTES DE {ruc_dni} =====")

    if not resultados:
        print("No se encontraron comprobantes para ese RUC/DNI.")
        return

    for item in resultados:
        mostrar_comprobante(item)


def menu_comprobantes():
    while True:
        print("\n===== MÓDULO DE COMPROBANTES DE PAGO =====")
        print("1. Registrar comprobante")
        print("2. Listar comprobantes")
        print("3. Listar comprobantes sin pagar")
        print("4. Registrar fecha de pago")
        print("5. Buscar por serie y número")
        print("6. Buscar por RUC/DNI")
        print("7. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            registrar_comprobante()
        elif opcion == "2":
            listar_comprobantes()
        elif opcion == "3":
            listar_pendientes_pago()
        elif opcion == "4":
            registrar_fecha_pago()
        elif opcion == "5":
            buscar_por_serie_numero()
        elif opcion == "6":
            buscar_por_ruc()
        elif opcion == "7":
            break
        else:
            print("Opción inválida.")