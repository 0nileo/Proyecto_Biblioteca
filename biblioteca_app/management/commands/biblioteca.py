
# BaseCommand permite crear comandos personalizados de Django
# que se ejecutan desde la terminal mediante manage.py.
from django.core.management.base import BaseCommand

# Importamos los modelos para reconocer sus excepciones específicas.
from biblioteca_app.models import Libro, Socio, Reserva

# Importamos el módulo de servicios, encargado de realizar
# las operaciones y consultas de nuestro sistema.
from biblioteca_app import services

# Excepciones utilizadas para manejar errores de base de datos
# y validaciones sin cerrar inesperadamente el programa.
from django.db import IntegrityError
from django.core.exceptions import ValidationError


# Django reconoce esta clase como un comando personalizado.
# Se ejecuta mediante: python manage.py biblioteca
class Command(BaseCommand):

    help = "Sistema de gestión de biblioteca por consola"

    # handle() es el punto de entrada del comando.
    # Django lo ejecuta automáticamente al iniciar la aplicación.
    def handle(self, *args, **options):

        # while True mantiene el menú funcionando hasta que
        # el usuario elija salir mediante break.
        while True:
            print("\n===== BIBLIOTECA =====\n")
            print("1. Administrar Libros")
            print("2. Administrar Socios")
            print("3. Administrar Reservas")
            print("4. Salir")

            opcion = input("\nSeleccione una opción: ")

            # match/case permite ejecutar distintas instrucciones
            # según la opción seleccionada por el usuario.
            match opcion:
                case "1":
                    self.menu_libros()

                case "2":
                    self.menu_socios()

                case "3":
                    self.menu_reservas()

                case "4":
                    print("Saliendo del sistema...")
                    break

                # El guion bajo captura cualquier opción no contemplada.
                case _:
                    print("Opción inválida. Intente nuevamente.")


    # =========================
    # ADMINISTRACIÓN DE LIBROS
    # =========================

    # Agrupamos las operaciones relacionadas con libros
    # para mantener organizado el menú principal.
    def menu_libros(self):
        while True:
            print("\n===== MENU LIBROS =====\n")
            print("1. Registrar nuevo libro")
            print("2. Buscar libro por ISBN")
            print("3. Buscar libro por título")
            print("4. Buscar libro por autor")
            print("5. Listar libros")
            print("6. Listar libros disponibles")
            print("7. Listar libros sin stock")
            print("8. Volver al menú principal")

            opcion = input("\nSeleccione una opción: ")

            match opcion:

                case "1":
                    # El menú solicita los datos, pero delega el registro
                    # y las validaciones al servicio registrar_libro().
                    try:
                        titulo = input("Ingrese el titulo del libro: ")
                        autor = input("Ingrese el autor del libro: ")
                        isbn = input("Ingrese el ISBN del libro: ")
                        anio = int(input("Ingrese el año de publicacion: "))
                        ejemplares = int(input("Ingrese la cantidad de ejemplares que tiene: "))

                        # El servicio devuelve el objeto Libro creado.
                        libro = services.registrar_libro(
                            titulo, autor, isbn, anio, ejemplares
                        )
                        print(f"Libro '{libro.titulo}' registrado correctamente.")

                    # ValidationError aparece cuando full_clean()
                    # detecta campos incorrectos o restricciones inválidas.
                    except ValidationError as error:
                        print(f"Error de validación: {error}")

                    # IntegrityError puede ocurrir al incumplir
                    # alguna restricción de integridad de la BD.
                    except IntegrityError:
                        print("No se pudo registrar el libro. Verificá que el ISBN no esté repetido.")

                    # ValueError captura valores incorrectos, como letras
                    # donde esperamos números o cantidades negativas.
                    except ValueError as error:
                        print(f"Error: {error}")

                case "2":
                    # Buscamos un único libro por su ISBN, que es único.
                    # Si no existe, get() lanza Libro.DoesNotExist.
                    try:
                        isbn = input("Ingrese el ISBN del libro que quiera buscar: ")
                        print(f"{services.buscar_libro_por_isbn(isbn)}")

                    except Libro.DoesNotExist:
                        print("No se ha encontrado un libro bajo el ISBN brindado.")

                case "3":
                    # El servicio devuelve un QuerySet con todos
                    # los libros cuyo título coincide parcialmente.
                    titulo = input("Ingrese el titulo del libro que quiera buscar: ")
                    libros = services.buscar_libro_por_titulo(titulo)

                    # Un QuerySet vacío no lanza DoesNotExist.
                    # Por eso comprobamos si contiene resultados.
                    if not libros:
                        print("No se encontraron libros con ese título.")
                    else:
                        for libro in libros:
                            print(libro)
                            print("-----------------------")

                case "4":
                    # Aplicamos el mismo procedimiento para buscar
                    # coincidencias parciales por autor.
                    autor = input("Ingrese el autor del libro que quiera buscar: ")
                    libros = services.buscar_libro_por_autor(autor)

                    if not libros:
                        print("No se encontraron libros con ese autor.")
                    else:
                        for libro in libros:
                            print(libro)
                            print("-----------------------")

                case "5":
                    # all() recupera todos los registros del modelo.
                    # El servicio consulta y el menú muestra los resultados.
                    libros = services.listar_libros()

                    if not libros:
                        print("No se han encontrado libros para listar")
                    else:
                        print("\n===== LISTADO DE LIBROS =====")
                        for item in libros:
                            print(item)
                            print("-----------------------")

                case "6":
                    # Listamos solamente los libros con stock mayor a cero.
                    libros = services.listar_libros_disponibles()

                    if not libros:
                        print("No se encontraron libros disponibles.")
                    else:
                        for libro in libros:
                            print(libro)
                            print("-----------------------")

                case "7":
                    # Listamos los libros que no tienen ejemplares disponibles.
                    libros = services.listar_libros_sin_stock()

                    if not libros:
                        print("No se encontraron libros sin stock.")
                    else:
                        for libro in libros:
                            print(libro)
                            print("-----------------------")

                case "8":
                    # break termina este while, pero no el menú principal.
                    # La ejecución regresa al método handle().
                    print("Regresando al menu principal...")
                    break

                case _:
                    print("Opción inválida. Intente nuevamente.")


    # =========================
    # ADMINISTRACIÓN DE SOCIOS
    # =========================

    def menu_socios(self):
        while True:
            print("\n===== MENU SOCIOS =====\n")
            print("1. Registrar nuevo socio")
            print("2. Buscar socio por DNI")
            print("3. Buscar socio por nombre o apellido")
            print("4. Listar socios")
            print("5. Listar socios activos")
            print("6. Volver al menú principal")

            opcion = input("\nSeleccione una opción: ")

            match opcion:

                case "1":
                    # Reunimos los datos del socio y llamamos al servicio.
                    # Las validaciones y el guardado se hacen fuera del menú.
                    try:
                        numero = input("Ingrese el numero de socio a crear: ")
                        nombre = input("Ingrese nombre del titular: ")
                        apellido = input("Ingrese el apellido del titular: ")
                        dni = input("Ingrese el numero de DNI del titular: ")
                        email = input("Ingrese el correo electronico del titular: ")

                        socio = services.registrar_socio(
                            numero, nombre, apellido, dni, email
                        )

                        print(f"Socio numero: {socio.numero_socio} fue creado exitosamente.")

                    # Capturamos los errores de validación del modelo,
                    # valores inválidos y restricciones de integridad.
                    except ValidationError as error:
                        print(f"Error de validación: {error}")

                    except ValueError as error:
                        print(f"Error: {error}")

                    except IntegrityError:
                        print("No se pudo registrar al socio. Verificár que el numero de socio o DNI no esté repetido.")

                case "2":
                    # Aunque el DNI es único, nuestro servicio utiliza
                    # filter() y devuelve una colección de resultados.
                    dni = input("Ingrese el DNI del socio que quiera buscar: ")
                    socios = services.buscar_socio_por_dni(dni)

                    if not socios:
                        print("No se encontraron socios con ese numero de DNI.")
                    else:
                        for socio in socios:
                            print(socio)
                            print("-----------------------")

                case "3":
                    # Búsqueda parcial de socios mediante el ORM.
                    nombre = input("Ingrese el nombre o apellido del socio que quiera buscar: ")
                    socios = services.buscar_socio_por_nombre(nombre)

                    if not socios:
                        print("No se encontraron socios con ese nombre.")
                    else:
                        for socio in socios:
                            print(socio)
                            print("-----------------------")

                case "4":
                    # Recuperamos todos los socios registrados.
                    socios = services.listar_socios()

                    if not socios:
                        print("No se encontraron socios.")
                    else:
                        for socio in socios:
                            print(socio)
                            print("-----------------------")

                case "5":
                    # El servicio filtra solamente los socios activos.
                    socios = services.listar_socios_activos()

                    if not socios:
                        print("No se encontraron socios activos.")
                    else:
                        for socio in socios:
                            print(socio)
                            print("-----------------------")

                case "6":
                    print("Regresando al menu principal...")
                    break

                case _:
                    print("Opción inválida. Intente nuevamente.")


    # =========================
    # ADMINISTRACIÓN DE RESERVAS
    # =========================

    # Este menú permite gestionar el ciclo de vida de una reserva:
    # pendiente -> retirada -> finalizada.
    # Una reserva pendiente también puede cancelarse.
    def menu_reservas(self):
        while True:
            print("\n===== MENU RESERVAS =====\n")
            print("1. Registrar nueva reserva")
            print("2. Cancelar reserva")
            print("3. Listar reservas")
            print("4. Listar reservas pendientes")
            print("5. Listar reservas por socio")
            print("6. Listar reservas por libro")
            print("7. Retirar libro reservado")
            print("8. Devolver libro reservado")
            print("9. Volver al menú principal")

            opcion = input("\nSeleccione una opción: ")

            match opcion:

                case "1":
                    try:
                        print("Ingrese a continuación...")
                        num_socio = input("El numero de socio: ")
                        num_libro = input("El ISBN del libro a reservar: ")

                        # El servicio busca los objetos Socio y Libro
                        # y ejecuta la operación solicitar_reserva().
                        # Devuelve ambos objetos para mostrar la confirmación.
                        socio, libro = services.registrar_reserva(
                            num_socio, num_libro
                        )

                        print(f"Se ha realizado la reserva exitosamente: {socio.nombre} reservó {libro.titulo}")

                    except ValidationError as error:
                        print(f"Error de validación: {error}")

                    # get() lanza DoesNotExist cuando no encuentra
                    # el socio o el libro solicitado.
                    except Socio.DoesNotExist:
                        print("El número de socio ingresado no existe.")

                    except Libro.DoesNotExist:
                        print("El ISBN ingresado no corresponde a ningún libro.")

                    # Las reglas de negocio pueden lanzar ValueError:
                    # socio inactivo, falta de stock o reserva duplicada.
                    except ValueError as error:
                        print(f"Error: {error}")

                case "2":
                    # Buscamos la reserva mediante su ID.
                    # El modelo verifica que esté pendiente y, al cancelarla,
                    # devuelve un ejemplar al stock disponible.
                    try:
                        id_reserva = input("Ingrese el numero de reserva a cancelar: ")
                        reserva = services.cancelar_reserva(id_reserva)

                        print(f"Se ha cancelado la reserva exitosamente: {reserva.libro.titulo} a nombre de {reserva.socio.nombre} {reserva.socio.apellido}")

                    except Reserva.DoesNotExist:
                        print("No se ha encontrado una reserva bajo el numero brindado")

                    except ValueError as error:
                        print(f"Error: {error}")

                case "3":
                    # Listado general de reservas, sin filtrar por estado.
                    reservas = services.listar_reservas()

                    if not reservas:
                        print("No se han encontrado reservas para listar")
                    else:
                        print("\n===== LISTADO DE RESERVAS =====")
                        for item in reservas:
                            print(item)
                            print("-----------------------")

                case "4":
                    # El servicio devuelve únicamente reservas pendientes.
                    reservas = services.listar_reservas_pendientes()

                    if not reservas:
                        print("No se han encontrado reservas para listar en estado pendiente")
                    else:
                        print(f"\n===== LISTADO DE RESERVAS PENDIENTES =====")
                        for item in reservas:
                            print(item)
                            print("-----------------------")

                case "5":
                    # Consultamos el historial de reservas de un socio.
                    # Incluye todos los estados y está ordenado por fecha e ID.
                    numero_socio = input("Ingrese el numero de socio: ")
                    reservas = services.listar_reservas_por_socio(numero_socio)

                    if not reservas:
                        print("No se han encontrado reservas para listar del socio ingresado")
                    else:
                        print("\n===== LISTADO DE RESERVAS =====\n")
                        for item in reservas:
                            print(item)
                            print("-----------------------")

                case "6":
                    # Consultamos todas las reservas relacionadas con un libro
                    # mediante su ISBN, sin importar el estado.
                    isbn = input("Ingrese el isbn del libro: ")
                    reservas = services.listar_reservas_por_isbn(isbn)

                    if not reservas:
                        print("No se han encontrado reservas para listar")
                    else:
                        print("\n===== LISTADO DE RESERVAS =====\n")
                        for item in reservas:
                            print(item)
                            print("-----------------------")

                case "7":
                    # Retirar una reserva pendiente cambia su estado
                    # a retirada, pero no vuelve a descontar stock.
                    try:
                        id_reserva = input("Ingrese el numero de reserva a retirar: ")
                        reserva = services.retirar_reserva(id_reserva)

                        print(f"Se ha realizado el retiro de la reserva exitosamente: {reserva.socio.nombre} {reserva.socio.apellido} ha retirado {reserva.libro.titulo}")

                    except Reserva.DoesNotExist:
                        print("No se ha encontrado una reserva bajo el numero brindado")

                    except ValueError as error:
                        print(f"Error: {error}")

                case "8":
                    # La devolución finaliza una reserva retirada
                    # y vuelve a incrementar el stock disponible del libro.
                    try:
                        id_reserva = input("Ingrese el numero de reserva a devolver: ")
                        reserva = services.devolver_reserva(id_reserva)

                        print(f"Se ha realizado la devolución de la reserva exitosamente: El socio/a: {reserva.socio.nombre} {reserva.socio.apellido} ha devuelto {reserva.libro.titulo}")

                    except Reserva.DoesNotExist:
                        print("No se ha encontrado una reserva bajo el numero brindado")

                    except ValueError as error:
                        print(f"Error: {error}")

                case "9":
                    print("Regresando al menu principal...")
                    break

                case _:
                    print("Opción inválida. Intente nuevamente.")
