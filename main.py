from modules.transacciones import menu_transacciones
from modules.comprobantes import menu_comprobantes
from modules.conciliacion import menu_conciliacion
from modules.estadisticas import menu_estadisticas
from database.crear_tablas import crear_tablas


def menu_principal():
    crear_tablas()

    while True:
        print("\n===== SISTEMA DE CONCILIACIÓN BANCARIA =====")
        print("1. Transacciones bancarias")
        print("2. Comprobantes")
        print("3. Conciliación")
        print("4. Estadísticas")
        print("5. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            menu_transacciones()
        elif opcion == "2":
            menu_comprobantes()
        elif opcion == "3":
            menu_conciliacion()
        elif opcion == "4":
            menu_estadisticas()
        elif opcion == "5":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    menu_principal()