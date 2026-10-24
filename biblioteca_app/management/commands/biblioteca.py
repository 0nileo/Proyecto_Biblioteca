from django.core.management.base import BaseCommand
from biblioteca_app.models import Libro, Socio, Reserva


class Command(BaseCommand):

    help = "Sistema de gestión de biblioteca por consola"

    def handle(self, *args, **options):
        while True:
            print("\n===== BIBLIOTECA =====\n")
            print("1. Registrar libro")
            print("2. Registrar socio")
            print("3. Solicitar reserva")
            print("4. Salir")

            opcion = input("\nSeleccione una opción: ")

            match opcion:
                case "1":
                    try:
                        titulo = input("Ingrese el titulo del libro: ")
                        autor = input("Ingrese el autor del libro: ")
                        isbn = input("Ingrese el ISBN del libro: ")
                        anio = int(input("Ingrese el año de publicacion: "))
                        ejemplares = int(input("Ingrese la cantidad de ejemplares que tiene: "))

                        Libro.objects.create(
                        titulo = titulo ,
                        autor = autor ,
                        isbn = isbn ,
                        anio_publicacion = anio ,
                        cantidad_ejemplares = ejemplares ,
                        cantidad_disponible = ejemplares
                        )
                        print("Libro creado exitosamente!.")

                    except ValueError:
                        print("Se ingresó un número inválido.")

                case "2":
                    print("Registrar socio")
                case "3":
                    print("Solicitar reserva")
                case "4":
                    print("Saliendo del sistema...")
                    break
                case _:
                    print("Opción inválida. Intente nuevamente.")