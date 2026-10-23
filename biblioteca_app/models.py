from django.db import models
from django.utils import timezone
from django.db import transaction

class Libro(models.Model):
    titulo = models.CharField(max_length=200)
    autor = models.CharField(max_length=150)
    isbn = models.CharField(max_length=13, unique=True)
    anio_publicacion = models.IntegerField()
    cantidad_disponible = models.IntegerField()
    cantidad_ejemplares = models.IntegerField()

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

    def solicitar_reserva(self, libro):
        #Si self.estado es "inactivo", el método solicitar_reserva(libro) debe lanzar un ValueError".
        if self.estado == 'inactivo':
            raise ValueError("El socio está inactivo")

        #si libro.cantidad_disponible es igual a cero debe lanzar el ValueError esperado.
        if libro.cantidad_disponible <= 0:
            raise ValueError("No hay ejemplares disponibles")

        #si el socio ya tiene una reserva del mismo libro en estado "pendiente" o "retirada" lanza el ValueError esperado.
        #self.reservas - .filter() - .exists()
        if self.reservas.filter(libro=libro, estado_reserva__in=["pendiente", "retirada"]).exists():
            raise ValueError("El socio ya tiene una reserva activa para este libro")

        #caso exitoso de crear una reserva
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
Reserva a nombre de:
Socio:{self.socio}
{self.libro}
Estado reserva:{self.estado_reserva}
Fecha de reserva:{self.fecha_reserva}
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
            raise ValueError(f"No se puede cancelar una reserva en estado: {self.estado_reserva}")

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

    



    
