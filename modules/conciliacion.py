import re

from database.conexion import obtener_conexion


# Variables globales para mantener datos en memoria durante la sesión
_transacciones_en_memoria = None
_comprobantes_en_memoria = None
_conciliaciones_en_memoria = None


def _extraer_referencias(descripcion):
    if not descripcion:
        return set()

    referencias = re.findall(r"\b([A-Za-z0-9]+-[A-Za-z0-9]+)\b", descripcion.upper())
    return set(referencias)


def _cargar_listas_pendientes(cursor):
    cursor.execute(
        """
        SELECT id, fecha_operacion, numero_operacion, monto, descripcion
        FROM transacciones_bancarias
        WHERE estado_conciliacion = 'pendiente'
          AND tipo_operacion = 'credito'
        ORDER BY fecha_operacion ASC, id ASC
        """
    )
    transacciones = []
    for fila in cursor.fetchall():
        transacciones.append(
            {
                "id": fila[0],
                "fecha_operacion": fila[1],
                "numero_operacion": fila[2],
                "monto": fila[3],
                "descripcion": fila[4] or "",
                "estado_conciliacion": "pendiente",
            }
        )

    cursor.execute(
        """
        SELECT id, serie, numero_correlativo, fecha_emision, monto
        FROM comprobantes
        WHERE estado_conciliacion = 'pendiente'
        ORDER BY fecha_emision ASC, id ASC
        """
    )
    comprobantes = []
    for fila in cursor.fetchall():
        comprobantes.append(
            {
                "id": fila[0],
                "serie": fila[1],
                "numero_correlativo": fila[2],
                "fecha_emision": fila[3],
                "monto": fila[4],
                "estado_conciliacion": "pendiente",
            }
        )

    return transacciones, comprobantes


def _conciliar_en_memoria(transacciones, comprobantes):
    conciliaciones = []

    for transaccion in transacciones:
        if transaccion["estado_conciliacion"] != "pendiente":
            continue

        referencias = _extraer_referencias(transaccion["descripcion"])
        comprobante_encontrado = None

        if referencias:
            for comprobante in comprobantes:
                if comprobante["estado_conciliacion"] != "pendiente":
                    continue

                referencia = f"{comprobante['serie']}-{comprobante['numero_correlativo']}".upper()
                if referencia in referencias:
                    comprobante_encontrado = comprobante
                    break

        if not comprobante_encontrado:
            for comprobante in comprobantes:
                if comprobante["estado_conciliacion"] != "pendiente":
                    continue

                if (
                    transaccion["monto"] == comprobante["monto"]
                    and transaccion["fecha_operacion"] >= comprobante["fecha_emision"]
                ):
                    comprobante_encontrado = comprobante
                    break

        if comprobante_encontrado:
            transaccion["estado_conciliacion"] = "conciliado"
            comprobante_encontrado["estado_conciliacion"] = "conciliado"
            conciliaciones.append(
                {
                    "transaccion_id": transaccion["id"],
                    "numero_operacion": transaccion["numero_operacion"],
                    "comprobante_id": comprobante_encontrado["id"],
                    "referencia_comprobante": f"{comprobante_encontrado['serie']}-{comprobante_encontrado['numero_correlativo']}",
                }
            )

    return conciliaciones


def _persistir_conciliaciones(cursor, conciliaciones):
    for relacion in conciliaciones:
        cursor.execute(
            """
            UPDATE transacciones_bancarias
            SET estado_conciliacion = 'conciliado'
            WHERE id = ?
            """,
            (relacion["transaccion_id"],),
        )

        cursor.execute(
            """
            UPDATE comprobantes
            SET estado_conciliacion = 'conciliado'
            WHERE id = ?
            """,
            (relacion["comprobante_id"],),
        )

        cursor.execute(
            """
            INSERT OR IGNORE INTO conciliacion (transaccion_id, comprobante_id)
            VALUES (?, ?)
            """,
            (relacion["transaccion_id"], relacion["comprobante_id"]),
        )


def ejecutar_conciliacion_semi_automatica():
    global _transacciones_en_memoria, _comprobantes_en_memoria, _conciliaciones_en_memoria
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    transacciones, comprobantes = _cargar_listas_pendientes(cursor)
    conexion.close()

    if not transacciones:
        print("No hay transacciones de ingreso pendientes por conciliar.")
        return

    conciliaciones = _conciliar_en_memoria(transacciones, comprobantes)
    
    _transacciones_en_memoria = transacciones
    _comprobantes_en_memoria = comprobantes
    _conciliaciones_en_memoria = conciliaciones

    print("\n===== RESULTADO DE CONCILIACIÓN =====")
    print(f"Total transacciones evaluadas: {len(transacciones)}")
    print(f"Total conciliadas: {len(conciliaciones)}")

    if conciliaciones:
        print("\nRelaciones generadas:")
        for relacion in conciliaciones:
            print(
                f"- Operación {relacion['numero_operacion']} => "
                f"Comprobante {relacion['referencia_comprobante']}"
            )


def ver_conciliaciones():
    global _conciliaciones_en_memoria, _transacciones_en_memoria, _comprobantes_en_memoria
    
    if _conciliaciones_en_memoria is None or not _conciliaciones_en_memoria:
        print("No hay conciliaciones en memoria. Ejecute primero la conciliación semi-automática.")
        return

    print("\n===== CONCILIACIONES EN MEMORIA =====\n")
    
    for idx, relacion in enumerate(_conciliaciones_en_memoria, 1):
        transaccion = None
        comprobante = None
        
        for t in _transacciones_en_memoria:
            if t["id"] == relacion["transaccion_id"]:
                transaccion = t
                break
        
        for c in _comprobantes_en_memoria:
            if c["id"] == relacion["comprobante_id"]:
                comprobante = c
                break
        
        if transaccion and comprobante:
            print(f"Conciliación #{idx}")
            print(f"  Transacción: Op.{transaccion['numero_operacion']} | Fecha: {transaccion['fecha_operacion']} | Monto: {transaccion['monto']} | Desc: {transaccion['descripcion']}")
            print(f"  Comprobante: {comprobante['serie']}-{comprobante['numero_correlativo']} | Fecha: {comprobante['fecha_emision']} | Monto: {comprobante['monto']}")
            print()


def buscar_transaccion_en_conciliacion():
    global _conciliaciones_en_memoria, _transacciones_en_memoria, _comprobantes_en_memoria
    
    if _conciliaciones_en_memoria is None or not _conciliaciones_en_memoria:
        print("No hay conciliaciones en memoria. Ejecute primero la conciliación semi-automática.")
        return
    
    numero_operacion = input("Ingrese el número de operación: ").strip()

    transaccion_encontrada = None
    conciliacion_encontrada = None
    
    for t in _transacciones_en_memoria:
        if t["numero_operacion"] == numero_operacion:
            transaccion_encontrada = t
            break
    
    if not transaccion_encontrada:
        print(f"No se encontró la transacción: {numero_operacion}")
        return
    
    for conc in _conciliaciones_en_memoria:
        if conc["transaccion_id"] == transaccion_encontrada["id"]:
            conciliacion_encontrada = conc
            break
    
    if not conciliacion_encontrada:
        print(f"La transacción {numero_operacion} no está conciliada.")
        return
    
    comprobante = None
    for c in _comprobantes_en_memoria:
        if c["id"] == conciliacion_encontrada["comprobante_id"]:
            comprobante = c
            break
    
    print("\n===== RESULTADO DE BÚSQUEDA =====\n")
    print(f"Transacción: Op.{transaccion_encontrada['numero_operacion']} | Fecha: {transaccion_encontrada['fecha_operacion']} | Monto: {transaccion_encontrada['monto']} | Desc: {transaccion_encontrada['descripcion']}")
    if comprobante:
        print(f"Comprobante: {comprobante['serie']}-{comprobante['numero_correlativo']} | Fecha: {comprobante['fecha_emision']} | Monto: {comprobante['monto']}")
    print()


def buscar_comprobante_en_conciliacion():
    global _conciliaciones_en_memoria, _transacciones_en_memoria, _comprobantes_en_memoria
    
    if _conciliaciones_en_memoria is None or not _conciliaciones_en_memoria:
        print("No hay conciliaciones en memoria. Ejecute primero la conciliación semi-automática.")
        return
    
    serie = input("Ingrese la serie del comprobante: ").strip()
    numero = input("Ingrese el número del comprobante: ").strip()

    comprobante_encontrado = None
    conciliacion_encontrada = None
    
    for c in _comprobantes_en_memoria:
        if c["serie"] == serie and c["numero_correlativo"] == numero:
            comprobante_encontrado = c
            break
    
    if not comprobante_encontrado:
        print(f"No se encontró el comprobante: {serie}-{numero}")
        return
    
    for conc in _conciliaciones_en_memoria:
        if conc["comprobante_id"] == comprobante_encontrado["id"]:
            conciliacion_encontrada = conc
            break
    
    if not conciliacion_encontrada:
        print(f"El comprobante {serie}-{numero} no está conciliado.")
        return
    
    transaccion = None
    for t in _transacciones_en_memoria:
        if t["id"] == conciliacion_encontrada["transaccion_id"]:
            transaccion = t
            break
    
    print("\n===== RESULTADO DE BÚSQUEDA =====\n")
    print(f"Comprobante: {comprobante_encontrado['serie']}-{comprobante_encontrado['numero_correlativo']} | Fecha: {comprobante_encontrado['fecha_emision']} | Monto: {comprobante_encontrado['monto']}")
    if transaccion:
        print(f"Transacción: Op.{transaccion['numero_operacion']} | Fecha: {transaccion['fecha_operacion']} | Monto: {transaccion['monto']} | Desc: {transaccion['descripcion']}")
    print()


def guardar_conciliaciones_en_bd():
    global _conciliaciones_en_memoria
    
    if _conciliaciones_en_memoria is None or not _conciliaciones_en_memoria:
        print("No hay conciliaciones en memoria para guardar.")
        return
    
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    
    _persistir_conciliaciones(cursor, _conciliaciones_en_memoria)
    
    conexion.commit()
    conexion.close()
    
    print(f"\n✓ {len(_conciliaciones_en_memoria)} conciliación(es) guardada(s) en la base de datos.")
    _conciliaciones_en_memoria = None


def menu_conciliacion():
    while True:
        print("\n===== MÓDULO DE CONCILIACIÓN =====")
        print("1. Ejecutar conciliación semi-automática")
        print("2. Ver conciliaciones (en memoria)")
        print("3. Buscar transaccion en conciliación")
        print("4. Buscar comprobante en conciliación")
        print("5. Guardar conciliaciones en BD")
        print("6. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            ejecutar_conciliacion_semi_automatica()
        elif opcion == "2":
            ver_conciliaciones()
        elif opcion == "3":
            buscar_transaccion_en_conciliacion()
        elif opcion == "4":
            buscar_comprobante_en_conciliacion()
        elif opcion == "5":
            guardar_conciliaciones_en_bd()
        elif opcion == "6":
            break
        else:
            print("Opción inválida.")