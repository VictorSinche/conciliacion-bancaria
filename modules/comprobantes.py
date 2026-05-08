def menu_comprobantes():
    while True:
        print("\n===== MÓDULO DE COMPROBANTES =====")
        print("1. Registrar comprobante")
        print("2. Listar comprobantes")
        print("3. Buscar comprobante")
        print("4. Volver al menú principal")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            print("Pendiente: Liz implementará el registro de comprobantes.")
        elif opcion == "2":
            print("Pendiente: Liz implementará el listado de comprobantes.")
        elif opcion == "3":
            print("Pendiente: Liz implementará la búsqueda de comprobantes.")
        elif opcion == "4":
            break
        else:
            print("Opción inválida.")