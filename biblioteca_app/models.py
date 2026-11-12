# Importamos las herramientas de Django necesarias para definir
# modelos, manejar fechas y realizar operaciones seguras en la BD.

from django.db import models
from django.utils import timezone
from django.db import transaction

# Cada clase que hereda de models.Model representa una entidad del sistema.
# Django utiliza estas definiciones para gestionar las tablas de la BD
# mediante su ORM, sin necesidad de escribir SQL directamente.

class Libro(models.Model):

    # Definimos los campos del libro y sus tipos de datos.
    # CharField almacena texto e IntegerField almacena números enteros.
    # error_messages permite personalizar los errores de validación.

    titulo = models.CharField(max_length=200, error_messages={"blank": "El título del libro no puede estar vacio."})
    autor = models.CharField(max_length=150, error_messages={"blank": "El autor del libro no puede estar vacio."})
    isbn = models.CharField(max_length=13, unique=True, error_messages={
                                "blank": "El ISBN no puede estar vacio.",
                                "unique": "Se ha encontrado otro libro registrado bajo el mismo ISBN."
                                                                        })
    anio_publicacion = models.IntegerField(error_messages={
                                "blank": "El año de publicación no puede estar vacio.",
                                })
    cantidad_disponible = models.IntegerField()
    cantidad_ejemplares = models.IntegerField(error_messages={
                                "blank": "El campo cantidad de ejemplares no puede estar vacio ",
                                "invalid": "El campo cantidad de ejemplares solo pueden ser numeros."
                                })

    # Meta permite definir configuraciones adicionales del modelo.
    # CheckConstraint establece reglas directamente en la base de datos:
    # 1. La cantidad disponible nunca puede ser negativa.
    # 2. La cantidad disponible nunca puede superar el total de ejemplares.
    # Q expresa una condición y F permite comparar valores de dos campos.

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(cantidad_disponible__gte=0),
                name="libro_disponibles_no_negativos"),
        
            models.CheckConstraint(
                condition=models.Q(cantidad_disponible__lte=models.F("cantidad_ejemplares")),
                name="libro_disponible_menor_a_libro_cantidad_total"
            )
            ]

    # __str__ define cómo se representa el objeto cuando lo imprimimos.
    # Lo utilizamos en los listados del menú para mostrar información legible.

    def __str__(self):
        return f"""
Libro: {self.titulo}
Autor: {self.autor}
ISBN: {self.isbn}
Año de publicacion: {self.anio_publicacion}
Ejemplares disponibles: {self.cantidad_disponible}/{self.cantidad_ejemplares}
"""


# Representa a una persona registrada como socio de la biblioteca.
# unique=True impide repetir identificadores como número de socio y DNI.

class Socio(models.Model):
    numero_socio = models.CharField(max_length=10, unique=True, error_messages={
                                "blank": "El numero de socio es un campo obligatorio.",
                                "unique": "Ya existe un socio registrado con el mismo numero de socio."                               
                                })
    nombre = models.CharField(max_length=50, error_messages={"blank": "El nombre del socio no puede estar vacio."})
    apellido = models.CharField(max_length=70, error_messages={"blank": "El apellido del socio no puede estar vacio."})
    dni = models.CharField(max_length=10, unique=True, error_messages={
                                "blank": "El DNI del socio no puede estar vacio.",
                                "unique": "Ya existe un socio registrado con el mismo numero de DNI."
                                })
    email = models.EmailField(max_length=254, error_messages={
                                "blank": "El campo email no puede estar vacio",
                                "invalid": "El email ingresado no es un formato de email valido."
                                })

    # choices limita los estados admitidos durante la validación del modelo.
    # Todo socio nuevo comienza activo gracias a default='activo'.

    estado = models.CharField(choices= [('activo', 'Activo'),
                                         ('inactivo', 'Inactivo')],
                                           default='activo', max_length=10)

    def __str__(self):
        return f"""{self.nombre} {self.apellido} socio numero:{self.numero_socio}.
DNI: {self.dni}, Email: {self.email}, Estado: {self.estado}"""


    # Regla de negocio: un socio puede solicitar una reserva
    # solamente si cumple las condiciones establecidas.

    def solicitar_reserva(self, libro):

        # Validamos que el socio esté habilitado.
        if self.estado == 'inactivo':
            raise ValueError("El socio está inactivo")

        # Verificamos que todavía existan ejemplares disponibles.
        if libro.cantidad_disponible <= 0:
            raise ValueError("No hay ejemplares disponibles")

        # related_name="reservas" permite acceder a las reservas del socio.
        # filter() busca reservas de este libro con estado pendiente o retirada.
        # exists() comprueba si existe al menos una coincidencia.

        if self.reservas.filter(libro=libro, estado_reserva__in=["pendiente", "retirada"]).exists():
            raise ValueError("El socio ya tiene una reserva activa para este libro")

        # transaction.atomic() agrupa las operaciones en una transacción.
        # Si ocurre un error dentro del bloque, se revierten sus cambios.
        # Primero creamos la reserva y luego descontamos un ejemplar.

        with transaction.atomic():
            Reserva.objects.create(socio = self, libro = libro)
            libro.cantidad_disponible -= 1
            libro.save()


# Reserva relaciona a un Socio con un Libro mediante claves foráneas.
# Cada reserva registra cuándo se creó y en qué estado se encuentra.

class Reserva(models.Model):

    # ForeignKey establece una relación de muchos a uno.
    # Un socio puede tener muchas reservas y un libro puede aparecer
    # en muchas reservas, pero cada reserva apunta a un socio y un libro.
    # PROTECT impide eliminar un socio o libro si tiene reservas asociadas.
    # related_name permite consultar la relación desde el otro modelo.
    
    socio = models.ForeignKey(Socio, on_delete=models.PROTECT, related_name="reservas")
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT, related_name="reservas")

    # timezone.localdate asigna por defecto la fecha actual.
    fecha_reserva = models.DateField(default=timezone.localdate)

    # Las reservas siguen un ciclo de estados:
    # pendiente -> retirada -> finalizada
    # Una reserva pendiente también puede cancelarse.
    estado_reserva = models.CharField(choices = [('pendiente', 'Pendiente'), 
                                                 ('retirada', 'Retirada'), 
                                                 ('cancelada', 'Cancelada'),
                                                 ('finalizada', 'Finalizada')],
                                                 default = 'pendiente', max_length=12)


    # Mostramos el ID generado por Django y los datos de los objetos
    # relacionados mediante self.socio y self.libro.
    def __str__(self):
        return f"""
Reserva ID: {self.id} 
A nombre de: {self.socio.nombre} {self.socio.apellido}
Libro: {self.libro.titulo}
Fecha de reserva:{self.fecha_reserva}
Estado de reserva:{self.estado_reserva}
"""

    # Cancelación: solamente se permite si la reserva está pendiente.
    # Al cancelarse, el ejemplar reservado vuelve al stock disponible.
    def cancelar(self):
        if self.estado_reserva != 'pendiente':
            raise ValueError(f"No se puede cancelar una reserva en estado: {self.estado_reserva}")

        with transaction.atomic():
            self.estado_reserva = 'cancelada'
            self.libro.cantidad_disponible += 1

            # update_fields indica qué campos queremos actualizar en la BD.
            self.save(update_fields=["estado_reserva"])
            self.libro.save(update_fields=["cantidad_disponible"])

    # Retiro: cambia la reserva de pendiente a retirada.
    # No se modifica el stock porque ya se descontó al reservar.
    def retirar(self):
        if self.estado_reserva != 'pendiente':
            raise ValueError(f"No se puede retirar una reserva en estado: {self.estado_reserva}")

        self.estado_reserva = 'retirada'
        self.save(update_fields=["estado_reserva"])

    # Devolución: únicamente se permite devolver una reserva retirada.
    # Al devolver el libro, finalizamos la reserva y recuperamos el stock.
    def devolver(self):
        if self.estado_reserva != 'retirada':
            raise ValueError(f"No se puede devolver una reserva en estado: {self.estado_reserva}")

        # Ambos cambios se ejecutan dentro de una misma transacción.
        with transaction.atomic():
            self.estado_reserva = 'finalizada'
            self.libro.cantidad_disponible +=1
            self.save(update_fields=["estado_reserva"])
            self.libro.save(update_fields=["cantidad_disponible"])
