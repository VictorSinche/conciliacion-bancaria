def menu_conciliacion():
    while True:
        print("\n===== MÓDULO DE CONCILIACIÓN =====")
        print("1. Ejecutar conciliación semi-automática")
        print("2. Ver transacciones conciliadas")
        print("3. Ver transacciones pendientes")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            print("Pendiente: Marco implementará la conciliación.")
        elif opcion == "2":
            print("Pendiente: Marco implementará consulta de conciliados.")
        elif opcion == "3":
            print("Pendiente: Marco implementará consulta de pendientes.")
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")