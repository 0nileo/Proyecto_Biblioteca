
# Importamos los tres modelos de nuestra aplicación.
# El punto inicial indica que models.py pertenece al mismo paquete.
from .models import Libro, Socio, Reserva


# =========================
# REGISTRO DE DATOS
# =========================

# Recibimos los datos de un libro, comprobamos nuestras reglas
# y utilizamos el modelo Libro para registrarlo en la base de datos.
def registrar_libro(titulo, autor, isbn, anio, ejemplares):

    # Validaciones propias del sistema.
    # Si un dato no cumple las condiciones, lanzamos un ValueError.
    if anio <= 0:
        raise ValueError("El año de publicacion del libro no puede ser menor a 0")
    if ejemplares < 0:
        raise ValueError("No se puede registrar una cantidad negativa de ejemplares.")

    # Construimos una instancia de Libro, pero todavía no se guarda
    # en la base de datos. Inicialmente todos los ejemplares están disponibles.
    libro = Libro(
        titulo = titulo,
        autor = autor,
        isbn = isbn,
        anio_publicacion = anio,
        cantidad_disponible = ejemplares,
        cantidad_ejemplares = ejemplares
    )

    # full_clean() ejecuta las validaciones definidas en el modelo:
    # campos obligatorios, tipos, longitudes, unicidad y restricciones.
    # Si hay errores, lanza ValidationError.
    # save() guarda el objeto utilizando el ORM de Django.
    libro.full_clean()
    libro.save()

    # Devolvemos el objeto creado para que el menú pueda mostrar sus datos.
    return libro


# El registro de socios sigue el mismo patrón que el de libros.
# El estado no se indica porque models.py lo establece como "activo"
# de forma predeterminada.
def registrar_socio(numero, nombre, apellido, dni, email):
    socio = Socio(
        numero_socio = numero,
        nombre = nombre,
        apellido = apellido,
        dni = dni,
        email = email
    )

    # Primero validamos los campos, incluyendo el formato del email
    # y la unicidad del número de socio y del DNI.
    # Después guardamos el nuevo registro en la base de datos.
    socio.full_clean()
    socio.save()
    return socio


# =========================
# GESTIÓN DE RESERVAS
# =========================

# Esta función coordina la búsqueda del socio y el libro.
# No implementamos aquí las reglas de la reserva porque ya
# están encapsuladas en Socio.solicitar_reserva().
def registrar_reserva(num_socio, num_libro):

    # objects.get() recupera un único objeto desde la base de datos.
    # Si no encuentra coincidencias, lanza DoesNotExist.
    socio = Socio.objects.get(numero_socio = num_socio)
    libro = Libro.objects.get(isbn = num_libro)

    # El modelo Socio verifica si está activo, si hay disponibilidad
    # y si no existe una reserva activa del mismo libro.
    # Si todo es válido, crea la reserva y descuenta un ejemplar.
    socio.solicitar_reserva(libro)

    # Python permite devolver varios objetos agrupados en una tupla.
    return socio, libro


# Los siguientes servicios siguen el mismo patrón:
# 1. Buscan una reserva por su identificador.
# 2. Invocan el método correspondiente del modelo Reserva.
# 3. Devuelven el objeto con su estado actualizado.
#
# Las reglas de cancelación, retiro y devolución permanecen
# en models.py, evitando duplicar la lógica de negocio.
def cancelar_reserva(id_reserva):
    reserva = Reserva.objects.get(id=id_reserva)
    reserva.cancelar()
    return reserva


def retirar_reserva(id_reserva):
    reserva = Reserva.objects.get(id=id_reserva)
    reserva.retirar()
    return reserva


def devolver_reserva(id_reserva):
    reserva = Reserva.objects.get(id=id_reserva)
    reserva.devolver()
    return reserva


# =========================
# LISTADOS GENERALES
# =========================

# objects.all() devuelve un QuerySet que representa todos los registros
# del modelo indicado. El menú se encarga de recorrerlos y mostrarlos.
def listar_libros():
    return Libro.objects.all()


def listar_socios():
    return Socio.objects.all()


def listar_reservas():
    return Reserva.objects.all()


# =========================
# BÚSQUEDAS
# =========================

# El ISBN es único, por eso utilizamos get() para buscar
# un único libro mediante una coincidencia exacta.
def buscar_libro_por_isbn(isbn):
    return Libro.objects.get(isbn=isbn)


# filter() devuelve un QuerySet, incluso si no encuentra resultados.
# __icontains permite encontrar coincidencias parciales de texto
# sin distinguir entre mayúsculas y minúsculas.
def buscar_libro_por_titulo(titulo):
    return Libro.objects.filter(titulo__icontains=titulo)


def buscar_libro_por_autor(autor):
    return Libro.objects.filter(autor__icontains=autor)


# El DNI es único, pero usamos filter(), por lo que recibimos
# un QuerySet con cero o un socio, sin lanzar DoesNotExist.
def buscar_socio_por_dni(dni):
    return Socio.objects.filter(dni=dni)


# Permite buscar socios cuyo nombre contenga el texto ingresado.
# Esta consulta no incluye el apellido.
def buscar_socio_por_nombre(nombre):
    return Socio.objects.filter(nombre__icontains=nombre)


# =========================
# CONSULTAS ESPECÍFICAS DEL ORM
# =========================

# __gt significa "greater than" (mayor que).
# Recuperamos libros con al menos un ejemplar disponible.
def listar_libros_disponibles():
    return Libro.objects.filter(cantidad_disponible__gt = 0)


# Si no agregamos un lookup, Django busca igualdad exacta.
# Recuperamos los libros que tienen cero ejemplares disponibles.
def listar_libros_sin_stock():
    return Libro.objects.filter(cantidad_disponible = 0)


# Filtramos las reservas por el valor exacto de su estado.
def listar_reservas_pendientes():
    return Reserva.objects.filter(estado_reserva = "pendiente")


# El doble guion bajo también permite recorrer relaciones ForeignKey.
# socio__numero_socio significa:
# "buscar reservas cuyo socio relacionado tenga ese número".
#
# order_by() organiza el resultado por fecha descendente
# y, cuando hay fechas iguales, utiliza el ID descendente.
def listar_reservas_por_socio(numero_socio):
    return Reserva.objects.filter(socio__numero_socio = numero_socio).order_by("-fecha_reserva", "-id")


# Buscamos reservas por un campo del libro relacionado.
# No filtramos por estado, así que incluye también reservas históricas.
def listar_reservas_por_isbn(isbn):
    return Reserva.objects.filter(libro__isbn=isbn)


# Recuperamos solamente los socios cuyo estado sea "activo".
def listar_socios_activos():
    return Socio.objects.filter(estado = "activo")
