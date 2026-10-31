from django.core.management.base import BaseCommand
from biblioteca_app.models import Libro, Socio, Reserva
from biblioteca_app import services
from django.db import IntegrityError
from django.core.exceptions import ValidationError

class Command(BaseCommand):

    help = "Sistema de gestión de biblioteca por consola"

    def handle(self, *args, **options):
        while True:
            print("\n===== BIBLIOTECA =====\n")
            print("1. Buscar Libro")
            print("2. Registrar libro")
            print("3. Registrar socio")
            print("4. Solicitar reserva")
            print("5. Cancelar reserva")
            print("6. Retirar libro reservado")
            print("7. Devolver libro")
            print("8. Listar libros")
            print("9. Listar Socios")
            print("10. Listar Reservas")
            print("11. Salir")

            opcion = input("\nSeleccione una opción: ")

            match opcion:
                case "1":
                    self.menu_buscar_libro()

                case "2":
                    try:
                        titulo = input("Ingrese el titulo del libro: ")
                        autor = input("Ingrese el autor del libro: ")
                        isbn = input("Ingrese el ISBN del libro: ")
                        anio = int(input("Ingrese el año de publicacion: "))
                        ejemplares = int(input("Ingrese la cantidad de ejemplares que tiene: "))
                        libro = services.registrar_libro(titulo, autor, isbn, anio, ejemplares)
                        print(f"Libro '{libro.titulo}' registrado correctamente.")

                    except ValidationError as error:
                        print(f"Error de validación: {error}")

                    except IntegrityError:
                        print("No se pudo registrar el libro. Verificá que el ISBN no esté repetido.")

                    except ValueError as error:
                        print(f"Error: {error}")

                case "3":
                    try:
                        numero = input("Ingrese el numero de socio a crear: ")
                        nombre = input("Ingrese nombre del titular: ")
                        apellido = input("Ingrese el apellido del titular: ")
                        dni = input("Ingrese el numero de DNI del titular: ")
                        email = input("Ingrese el correo electronico del titular: ")
                        socio = services.registrar_socio(numero, nombre, apellido, dni, email)
                        print(f"Socio numero: {socio.numero_socio} fue creado exitosamente.")

                    except ValueError as error:
                        print(f"Error: {error}")

                    except IntegrityError:
                        print("No se pudo registrar al socio. Verificár que el numero de socio o DNI no esté repetido.")
                      
                case "4":
                    try:
                        print("Ingrese a continuación...")
                        num_socio = input("El numero de socio: ")
                        num_libro = input("El ISBN del libro a reservar: ")
                        socio, libro = services.registrar_reserva(num_socio, num_libro)
                        print(f"Se ha realizado la reserva exitosamente: {socio.nombre} reservó {libro.titulo}")

                    except Socio.DoesNotExist:
                        print("El número de socio ingresado no existe.")

                    except Libro.DoesNotExist:
                        print("El ISBN ingresado no corresponde a ningún libro.")
                        
                    except ValueError as error:
                        print(f"Error: {error}")

                case "5":
                    try:
                        id_reserva = input("Ingrese el numero de reserva a cancelar: ")
                        reserva = services.cancelar_reserva(id_reserva)
                        print(f"Se ha cancelado la reserva exitosamente: {reserva.libro.titulo} a nombre de {reserva.socio.nombre} {reserva.socio.apellido}")

                    except Reserva.DoesNotExist:
                        print("No se ha encontrado una reserva bajo el numero brindado")

                    except ValueError as error:
                        print(f"Error: {error}")

                case "6":
                    try:
                        id_reserva = input("Ingrese el numero de reserva a retirar: ")
                        reserva = services.retirar_reserva(id_reserva)
                        print(f"Se ha realizado el retiro de la reserva exitosamente: {reserva.socio.nombre} {reserva.socio.apellido} ha retirado {reserva.libro.titulo}")

                    except Reserva.DoesNotExist:
                        print("No se ha encontrado una reserva bajo el numero brindado")

                    except ValueError as error:
                        print(f"Error: {error}")

                case "7":
                    try:
                        id_reserva = input("Ingrese el numero de reserva a devolver: ")
                        reserva = services.devolver_reserva(id_reserva)
                        print(f"Se ha realizado la devolución de la reserva exitosamente: {reserva.socio.nombre} {reserva.socio.apellido} ha devuelto {reserva.libro.titulo}")

                    except Reserva.DoesNotExist:
                        print("No se ha encontrado una reserva bajo el numero brindado")

                    except ValueError as error:
                        print(f"Error: {error}")

                case "8":
                    libros = services.listar_libros()
                    if not libros:
                        print("No se han encontrado libros para listar")
                    else:
                        print("\n===== LISTADO DE LIBROS =====")
                        for item in libros:
                            print(item)
                            print("-----------------------")
                case "9":
                    socios = services.listar_socios()
                    if not socios:
                        print("No se han encontrado socios para listar")
                    else:
                        print("\n===== LISTADO DE SOCIOS =====")
                        for item in socios:
                            print(item)
                            print("-----------------------")
                case "10":
                    reservas = services.listar_reservas()
                    if not reservas:
                        print("No se han encontrado reservas para listar")
                    else:
                        print("\n===== LISTADO DE RESERVAS =====")
                        for item in reservas:
                            print(item)
                            print("-----------------------")
                    
                case "11":
                    print("Saliendo del sistema...")
                    break
                case _:
                    print("Opción inválida. Intente nuevamente.")

    def menu_buscar_libro(self):
        while True:
            print("\n===== BUSCAR LIBROS =====")
            print("1. Buscar por ISBN")
            print("2. Buscar por título")
            print("3. Buscar por autor")
            print("4. Volver al menú principal")

            opcion = input("\nSeleccione una opción: ")

            match opcion:
                case "1":
                    try:
                        isbn = input("Ingrese el ISBN del libro que quiera buscar: ")
                        print(f"{services.buscar_libro_por_isbn(isbn)}")
                    except Libro.DoesNotExist:
                        print("No se ha encontrado un libro bajo el ISBN brindado.")
                case "2":
                    titulo = input("Ingrese el titulo del libro que quiera buscar: ")
                    libros = services.buscar_libro_por_titulo(titulo)

                    if not libros:
                            print("No se encontraron libros con ese título.")
                    else:
                        for libro in libros:
                            print(libro)
                            print("-----------------------")
                case "3":
                    autor = input("Ingrese el autor del libro que quiera buscar: ")
                    libros = services.buscar_libro_por_autor(autor)
                    if not libros:
                        print("No se encontraron libros con ese autor.")
                    else:
                        for libro in libros:
                            print(libro)
                            print("-----------------------")
                case "4":
                    print("Regresando al menu principal...")
                    break




