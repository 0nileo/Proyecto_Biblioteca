from .models import Libro, Socio, Reserva

def registrar_libro(titulo, autor, isbn, anio, ejemplares):
    if anio <= 0:
        raise ValueError("El año de publicacion del libro no puede ser menor a 0")
    if ejemplares < 0:
        raise ValueError("No se puede registrar una cantidad negativa de ejemplares.")
    libro = Libro(
        titulo = titulo,
        autor = autor,
        isbn = isbn,
        anio_publicacion = anio,
        cantidad_disponible = ejemplares,
        cantidad_ejemplares = ejemplares        
    )

    libro.full_clean()
    libro.save()
    
    return libro

def registrar_socio(numero, nombre, apellido, dni, email):
    socio = Socio(
        numero_socio = numero,
        nombre = nombre,
        apellido = apellido,
        dni = dni,
        email = email
    )

    socio.full_clean()
    socio.save()
    return socio

def registrar_reserva(num_socio, num_libro):
    socio = Socio.objects.get(numero_socio = num_socio)
    libro = Libro.objects.get(isbn = num_libro)

    socio.solicitar_reserva(libro)
    return socio, libro

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

def listar_libros():
    return Libro.objects.all()

def listar_socios():
    return Socio.objects.all()

def listar_reservas():
    return Reserva.objects.all()

def buscar_libro_por_isbn(isbn):
    return Libro.objects.get(isbn=isbn)

def buscar_libro_por_titulo(titulo):
    return Libro.objects.filter(titulo__icontains=titulo)

def buscar_libro_por_autor(autor):
    return Libro.objects.filter(autor__icontains=autor)
