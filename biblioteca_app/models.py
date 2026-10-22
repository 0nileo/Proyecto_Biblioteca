from django.db import models
from django.utils import timezone

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    isbn = models.CharField(max_length=13, unique=True)
    anio_publicacion = models.IntegerField()
    cantidad_disponible = models.IntegerField()
    cantidad_ejemplares = models.IntegerField()

    def __str__(self):
        return f"""
Libro:{self.titulo}
Autor:{self.autor}
ISBN: {self.isbn}
Año de publicacion:{self.anio_publicacion}
Ejemplares disponibles:{self.cantidad_disponible}
"""


class Socio(models.Model):
    numero_socio = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)
    apellido = models.CharField(max_length=70)
    dni = models.CharField(max_length=10, unique=True)
    email = models.EmailField(max_length=254)
    estado = models.CharField(choices= [('activo', 'Activo'),
                                         ('inactivo', 'Inactivo')],
                                           default='activo', max_length=10)

    def __str__(self):
        return f"{self.nombre} {self.apellido}, socio numero:{self.numero_socio}."


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
Reserva a nombre de:
Socio:{self.socio}
{self.libro}
Estado reserva:{self.estado_reserva}
Fecha de reserva:{self.fecha_reserva}
"""
