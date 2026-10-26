from django.db import models
from django.utils import timezone
from django.db import transaction

class Libro(models.Model):
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
    
    def __str__(self):
        return f"""
Libro: {self.titulo}
Autor: {self.autor}
ISBN: {self.isbn}
Año de publicacion: {self.anio_publicacion}
Ejemplares disponibles: {self.cantidad_disponible}/{self.cantidad_ejemplares}
"""


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
    estado = models.CharField(choices= [('activo', 'Activo'),
                                         ('inactivo', 'Inactivo')],
                                           default='activo', max_length=10)

    def __str__(self):
        return f"""{self.nombre} {self.apellido} socio numero:{self.numero_socio}.
DNI: {self.dni}, Email: {self.email}, Estado: {self.estado}"""


    def solicitar_reserva(self, libro):
        if self.estado == 'inactivo':
            raise ValueError("El socio está inactivo")

        if libro.cantidad_disponible <= 0:
            raise ValueError("No hay ejemplares disponibles")

        if self.reservas.filter(libro=libro, estado_reserva__in=["pendiente", "retirada"]).exists():
            raise ValueError("El socio ya tiene una reserva activa para este libro")

        with transaction.atomic():
            Reserva.objects.create(socio = self, libro = libro)
            libro.cantidad_disponible -= 1
            libro.save()





class Reserva(models.Model):
    socio = models.ForeignKey(Socio, on_delete=models.PROTECT, related_name="reservas")
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT, related_name="reservas")
    fecha_reserva = models.DateField(default=timezone.localdate)
    estado_reserva = models.CharField(choices = [('pendiente', 'Pendiente'), 
                                                 ('retirada', 'Retirada'), 
                                                 ('cancelada', 'Cancelada'),
                                                 ('finalizada', 'Finalizada')],
                                                 default = 'pendiente', max_length=12)



    def __str__(self):
        return f"""
Reserva ID: {self.id} 
A nombre de: {self.socio.nombre} {self.socio.apellido}
Libro: {self.libro.titulo}
Fecha de reserva:{self.fecha_reserva}
Estado de reserva:{self.estado_reserva}
"""

    def cancelar(self):
        if self.estado_reserva != 'pendiente':
            raise ValueError(f"No se puede cancelar una reserva en estado: {self.estado_reserva}")

        with transaction.atomic():
            self.estado_reserva = 'cancelada'
            self.libro.cantidad_disponible += 1
            self.save(update_fields=["estado_reserva"])
            self.libro.save(update_fields=["cantidad_disponible"])

    def retirar(self):
        if self.estado_reserva != 'pendiente':
            raise ValueError(f"No se puede retirar una reserva en estado: {self.estado_reserva}")

        self.estado_reserva = 'retirada'
        self.save(update_fields=["estado_reserva"])

    def devolver(self):
        if self.estado_reserva != 'retirada':
            raise ValueError(f"No se puede devolver una reserva en estado: {self.estado_reserva}")
        with transaction.atomic():
            self.estado_reserva = 'finalizada'
            self.libro.cantidad_disponible +=1
            self.save(update_fields=["estado_reserva"])
            self.libro.save(update_fields=["cantidad_disponible"])

    



    
