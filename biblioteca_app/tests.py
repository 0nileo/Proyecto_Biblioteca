from django.test import TestCase
from biblioteca_app.models import Libro, Socio, Reserva


class SolicitarReservaTests(TestCase):

    def setUp(self):
        # Crear aquí el socio inactivo y el libro con 3 ejemplares
        socio_prueba = Socio("1", "Jose", "Gonzalez", "37645681", "jgonzalez@gmail.com")
        libro1 = Libro("Dune", "Autor", "123" , "1993", 3, 3)
        

    def test_socio_inactivo_no_puede_reservar(self):
        # Registrar la cantidad de reservas y el stock inicial
        # Intentar la reserva y comprobar la excepción
        # Verificar que ni las reservas ni el stock hayan cambiado
        pass