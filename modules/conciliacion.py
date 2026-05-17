import re
from database.conexion import obtener_conexion


transacciones_en_memoria = []
comprobantes_en_memoria = []
conciliaciones_en_memoria = []


def extraer_referencias(descripcion):
    if not descripcion:
        return set()

    return set(re.findall(r"\b([A-Z0-9]+-[A-Z0-9]+)\b", descripcion.upper()))


def obtener_referencias_comprobante(comprobante):
    numero_normal = comprobante["numero_correlativo"]
    numero_sin_ceros = str(int(numero_normal)) if numero_normal.isdigit() else numero_normal

    return {
        f"{comprobante['serie']}-{numero_normal}".upper(),
        f"{comprobante['serie']}-{numero_sin_ceros}".upper()
    }


def cargar_pendientes(cursor):
    cursor.execute("""
        SELECT id, fecha_operacion, numero_operacion, monto, descripcion
        FROM transacciones_bancarias
        WHERE estado_conciliacion = 'pendiente'
          AND tipo_operacion = 'credito'
        ORDER BY fecha_operacion ASC, id ASC
    """)

    transacciones = []

    for fila in cursor.fetchall():
        transacciones.append({
            "id": fila[0],
            "fecha_operacion": fila[1],
            "numero_operacion": fila[2],
            "monto": float(fila[3]),
            "descripcion": fila[4] or "",
            "estado_conciliacion": "pendiente"
        })

    cursor.execute("""
        SELECT id, serie, numero_correlativo, fecha_emision, total
        FROM comprobantes
        WHERE estado_conciliacion = 'pendiente'
        ORDER BY fecha_emision ASC, id ASC
    """)

    comprobantes = []

    for fila in cursor.fetchall():
        comprobantes.append({
            "id": fila[0],
            "serie": fila[1],
            "numero_correlativo": fila[2],
            "fecha_emision": fila[3],
            "monto": float(fila[4]),
            "estado_conciliacion": "pendiente"
        })

    return transacciones, comprobantes


def conciliar_en_memoria(transacciones, comprobantes):
    conciliaciones = []

    for transaccion in transacciones:
        if transaccion["estado_conciliacion"] != "pendiente":
            continue

        comprobante_encontrado = None
        referencias_transaccion = extraer_referencias(transaccion["descripcion"])

        # Primer criterio: referencia en la descripción.
        for comprobante in comprobantes:
            if comprobante["estado_conciliacion"] != "pendiente":
                continue

            referencias_comprobante = obtener_referencias_comprobante(comprobante)

            if referencias_transaccion.intersection(referencias_comprobante):
                comprobante_encontrado = comprobante
                break

        # Segundo criterio: monto exacto y fecha lógica.
        if comprobante_encontrado is None:
            for comprobante in comprobantes:
                if comprobante["estado_conciliacion"] != "pendiente":
                    continue

                mismo_monto = round(transaccion["monto"], 2) == round(comprobante["monto"], 2)
                fecha_valida = transaccion["fecha_operacion"] >= comprobante["fecha_emision"]

                if mismo_monto and fecha_valida:
                    comprobante_encontrado = comprobante
                    break

        if comprobante_encontrado:
            transaccion["estado_conciliacion"] = "conciliado"
            comprobante_encontrado["estado_conciliacion"] = "conciliado"

            conciliaciones.append({
                "transaccion_id": transaccion["id"],
                "numero_operacion": transaccion["numero_operacion"],
                "comprobante_id": comprobante_encontrado["id"],
                "referencia_comprobante": (
                    f"{comprobante_encontrado['serie']}-"
                    f"{comprobante_encontrado['numero_correlativo']}"
                ),
                "monto": transaccion["monto"]
            })

    return conciliaciones


def ejecutar_conciliacion_semi_automatica():
    global transacciones_en_memoria
    global comprobantes_en_memoria
    global conciliaciones_en_memoria

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    transacciones, comprobantes = cargar_pendientes(cursor)
    conexion.close()

    if not transacciones:
        print("\nNo hay transacciones de ingreso pendientes por conciliar.")
        return

    if not comprobantes:
        print("\nNo hay comprobantes pendientes por conciliar.")
        return

    conciliaciones = conciliar_en_memoria(transacciones, comprobantes)

    transacciones_en_memoria = transacciones
    comprobantes_en_memoria = comprobantes
    conciliaciones_en_memoria = conciliaciones

    print("\n===== RESULTADO DE CONCILIACIÓN SEMI-AUTOMÁTICA =====")
    print(f"Transacciones evaluadas: {len(transacciones)}")
    print(f"Comprobantes evaluados: {len(comprobantes)}")
    print(f"Conciliaciones encontradas: {len(conciliaciones)}")

    if conciliaciones:
        print("\nRelaciones encontradas:")

        for relacion in conciliaciones:
            print(
                f"- Operación {relacion['numero_operacion']} "
                f"=> Comprobante {relacion['referencia_comprobante']} "
                f"| Monto: {relacion['monto']:.2f}"
            )
    else:
        print("No se encontraron coincidencias automáticas.")


def ver_conciliaciones_en_memoria():
    if not conciliaciones_en_memoria:
        print("\nNo hay conciliaciones en memoria. Ejecute primero la conciliación semi-automática.")
        return

    print("\n===== CONCILIACIONES EN MEMORIA =====")

    for indice, relacion in enumerate(conciliaciones_en_memoria, 1):
        transaccion = buscar_transaccion_memoria(relacion["transaccion_id"])
        comprobante = buscar_comprobante_memoria(relacion["comprobante_id"])

        if transaccion and comprobante:
            print(f"\nConciliación #{indice}")
            print(
                f"Transacción : {transaccion['numero_operacion']} | "
                f"Fecha: {transaccion['fecha_operacion']} | "
                f"Monto: {transaccion['monto']:.2f} | "
                f"Descripción: {transaccion['descripcion']}"
            )
            print(
                f"Comprobante : {comprobante['serie']}-{comprobante['numero_correlativo']} | "
                f"Fecha emisión: {comprobante['fecha_emision']} | "
                f"Total: {comprobante['monto']:.2f}"
            )


def buscar_transaccion_memoria(transaccion_id):
    for transaccion in transacciones_en_memoria:
        if transaccion["id"] == transaccion_id:
            return transaccion

    return None


def buscar_comprobante_memoria(comprobante_id):
    for comprobante in comprobantes_en_memoria:
        if comprobante["id"] == comprobante_id:
            return comprobante

    return None


def buscar_transaccion_en_conciliacion():
    if not conciliaciones_en_memoria:
        print("\nNo hay conciliaciones en memoria. Ejecute primero la conciliación semi-automática.")
        return

    numero_operacion = input("Ingrese el número de operación: ").strip()

    for relacion in conciliaciones_en_memoria:
        transaccion = buscar_transaccion_memoria(relacion["transaccion_id"])

        if transaccion and transaccion["numero_operacion"] == numero_operacion:
            comprobante = buscar_comprobante_memoria(relacion["comprobante_id"])

            print("\n===== RESULTADO DE BÚSQUEDA =====")
            print(
                f"Transacción : {transaccion['numero_operacion']} | "
                f"Fecha: {transaccion['fecha_operacion']} | "
                f"Monto: {transaccion['monto']:.2f}"
            )

            if comprobante:
                print(
                    f"Comprobante : {comprobante['serie']}-{comprobante['numero_correlativo']} | "
                    f"Total: {comprobante['monto']:.2f}"
                )

            return

    print("No se encontró una conciliación para esa transacción.")


def normalizar_numero_comprobante(numero):
    if numero.isdigit() and len(numero) <= 8:
        return numero.zfill(8)

    return numero


def buscar_comprobante_en_conciliacion():
    if not conciliaciones_en_memoria:
        print("\nNo hay conciliaciones en memoria. Ejecute primero la conciliación semi-automática.")
        return

    serie = input("Ingrese la serie del comprobante: ").strip().upper()
    numero = input("Ingrese el número del comprobante: ").strip()
    numero = normalizar_numero_comprobante(numero)

    for relacion in conciliaciones_en_memoria:
        comprobante = buscar_comprobante_memoria(relacion["comprobante_id"])

        if (
            comprobante
            and comprobante["serie"] == serie
            and comprobante["numero_correlativo"] == numero
        ):
            transaccion = buscar_transaccion_memoria(relacion["transaccion_id"])

            print("\n===== RESULTADO DE BÚSQUEDA =====")
            print(
                f"Comprobante : {comprobante['serie']}-{comprobante['numero_correlativo']} | "
                f"Total: {comprobante['monto']:.2f}"
            )

            if transaccion:
                print(
                    f"Transacción : {transaccion['numero_operacion']} | "
                    f"Fecha: {transaccion['fecha_operacion']} | "
                    f"Monto: {transaccion['monto']:.2f}"
                )

            return

    print("No se encontró una conciliación para ese comprobante.")


def guardar_conciliaciones_en_bd():
    global conciliaciones_en_memoria

    if not conciliaciones_en_memoria:
        print("\nNo hay conciliaciones en memoria para guardar.")
        return

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        for relacion in conciliaciones_en_memoria:
            cursor.execute("""
                UPDATE transacciones_bancarias
                SET estado_conciliacion = 'conciliado'
                WHERE id = ?
            """, (relacion["transaccion_id"],))

            cursor.execute("""
                UPDATE comprobantes
                SET estado_conciliacion = 'conciliado'
                WHERE id = ?
            """, (relacion["comprobante_id"],))

            cursor.execute("""
                INSERT OR IGNORE INTO conciliacion (
                    transaccion_id,
                    comprobante_id
                ) VALUES (?, ?)
            """, (relacion["transaccion_id"], relacion["comprobante_id"]))

        conexion.commit()
        print(f"\n{len(conciliaciones_en_memoria)} conciliación(es) guardada(s) correctamente.")

        conciliaciones_en_memoria = []

    except Exception as error:
        conexion.rollback()
        print(f"No se pudieron guardar las conciliaciones: {error}")

    finally:
        conexion.close()


def ver_conciliaciones_guardadas():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT
            c.id,
            t.numero_operacion,
            t.fecha_operacion,
            t.monto,
            co.serie,
            co.numero_correlativo,
            co.fecha_emision,
            co.total,
            c.fecha_conciliacion
        FROM conciliacion c
        INNER JOIN transacciones_bancarias t
            ON c.transaccion_id = t.id
        INNER JOIN comprobantes co
            ON c.comprobante_id = co.id
        ORDER BY c.fecha_conciliacion DESC, c.id DESC
    """)

    resultados = cursor.fetchall()
    conexion.close()

    print("\n===== CONCILIACIONES GUARDADAS EN BD =====")

    if not resultados:
        print("No hay conciliaciones guardadas.")
        return

    for item in resultados:
        print(
            f"ID: {item[0]} | Operación: {item[1]} | "
            f"Fecha operación: {item[2]} | Monto: {item[3]:.2f} | "
            f"Comprobante: {item[4]}-{item[5]} | "
            f"Fecha emisión: {item[6]} | Total: {item[7]:.2f} | "
            f"Fecha conciliación: {item[8]}"
        )


def menu_conciliacion():
    while True:
        print("\n===== MÓDULO DE CONCILIACIÓN =====")
        print("1. Ejecutar conciliación semi-automática")
        print("2. Ver conciliaciones encontradas")
        print("3. Buscar transacción conciliada")
        print("4. Buscar comprobante conciliado")
        print("5. Guardar conciliaciones en BD")
        print("6. Ver conciliaciones guardadas en BD")
        print("7. Volver al menú principal")

        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            ejecutar_conciliacion_semi_automatica()
        elif opcion == "2":
            ver_conciliaciones_en_memoria()
        elif opcion == "3":
            buscar_transaccion_en_conciliacion()
        elif opcion == "4":
            buscar_comprobante_en_conciliacion()
        elif opcion == "5":
            guardar_conciliaciones_en_bd()
        elif opcion == "6":
            ver_conciliaciones_guardadas()
        elif opcion == "7":
            break
        else:
            print("Opción inválida.")