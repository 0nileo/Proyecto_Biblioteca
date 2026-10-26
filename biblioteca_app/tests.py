from django.test import TestCase
from django.db import IntegrityError
from biblioteca_app.models import Libro, Socio, Reserva


class SolicitarReservaTests(TestCase):

    def setUp(self):
        self.socio_prueba = Socio.objects.create(
            numero_socio="SOC001",
            nombre="Jose",
            apellido="Gonzalez",
            dni="37645681",
            email="jgonzalez@gmail.com",
            estado="inactivo"
        )

        self.libro1 = Libro.objects.create(
            titulo="Dune",
            autor="Frank Herbert",
            isbn="9780441172719",
            anio_publicacion=1965,
            cantidad_ejemplares=3,
            cantidad_disponible=3
        )
        

    def test_socio_inactivo_no_puede_reservar(self):

        # 1. Guardamos el estado inicial
        reservas_antes = Reserva.objects.count()
        stock_antes = self.libro1.cantidad_disponible

        # 2. Intentamos reservar y esperamos una excepción
        with self.assertRaisesMessage(ValueError, "El socio está inactivo"):
            self.socio_prueba.solicitar_reserva(self.libro1)

        # 3. Volvemos a consultar el libro en la base de datos
        self.libro1.refresh_from_db()

        # 4. Verificamos que nada haya cambiado
        self.assertEqual(Reserva.objects.count(), reservas_antes)
        self.assertEqual(self.libro1.cantidad_disponible, stock_antes)

    def test_libro_sin_stock_no_puede_reservarse(self):

        self.socio_prueba.estado = "activo"
        self.socio_prueba.save()

        self.libro1.cantidad_disponible = 0
        self.libro1.save()

        reservas_antes = Reserva.objects.count()
        stock_antes = self.libro1.cantidad_disponible

        with self.assertRaisesMessage(ValueError, "No hay ejemplares disponibles"):
            self.socio_prueba.solicitar_reserva(self.libro1)

        self.libro1.refresh_from_db()

        self.assertEqual(Reserva.objects.count(), reservas_antes)
        self.assertEqual(self.libro1.cantidad_disponible, stock_antes)


    def test_reserva_duplicada_no_permitida(self):

        self.socio_prueba.estado = "activo"
        self.socio_prueba.save()

        Reserva.objects.create(
            socio=self.socio_prueba,
            libro=self.libro1,
            estado_reserva="pendiente"
        )

        reservas_antes = self.socio_prueba.reservas.count()
        stock_antes = self.libro1.cantidad_disponible

        with self.assertRaisesMessage(ValueError, "El socio ya tiene una reserva activa para este libro"):
            self.socio_prueba.solicitar_reserva(self.libro1)

        self.libro1.refresh_from_db()

        self.assertEqual(Reserva.objects.count(), reservas_antes)
        self.assertEqual(self.libro1.cantidad_disponible, stock_antes)


    def test_reserva_retirada_no_permite_duplicados(self):

        self.socio_prueba.estado = "activo"
        self.socio_prueba.save()

        Reserva.objects.create(
            socio=self.socio_prueba,
            libro=self.libro1,
            estado_reserva="retirada"
        )

        reservas_antes = self.socio_prueba.reservas.count()
        stock_antes = self.libro1.cantidad_disponible

        with self.assertRaisesMessage(ValueError, "El socio ya tiene una reserva activa para este libro"):
            self.socio_prueba.solicitar_reserva(self.libro1)

        self.libro1.refresh_from_db()

        self.assertEqual(Reserva.objects.count(), reservas_antes)
        self.assertEqual(self.libro1.cantidad_disponible, stock_antes)


    def test_reserva_exitosa(self):

        self.socio_prueba.estado = "activo"
        self.socio_prueba.save()

        reservas_antes = self.socio_prueba.reservas.count()
        stock_antes = self.libro1.cantidad_disponible
        stock_ejemplares = self.libro1.cantidad_ejemplares

        self.socio_prueba.solicitar_reserva(self.libro1)

        reserva_creada = self.socio_prueba.reservas.get(libro=self.libro1)

        self.libro1.refresh_from_db()

        self.assertEqual(self.socio_prueba.reservas.count(), reservas_antes+1)
        self.assertEqual(self.libro1.cantidad_disponible, stock_antes-1)
        self.assertEqual(self.libro1.cantidad_ejemplares, stock_ejemplares)
        self.assertEqual(reserva_creada.libro, self.libro1)
        self.assertEqual(reserva_creada.estado_reserva, "pendiente")


    def test_reserva_cancelada(self):

        self.socio_prueba.estado = "activo"
        self.socio_prueba.save()
        self.libro1.cantidad_disponible = 2
        self.libro1.save()

        reserva = Reserva.objects.create(
            socio=self.socio_prueba,
            libro=self.libro1,
            estado_reserva="pendiente"
        )

        stock_antes = self.libro1.cantidad_disponible
        stock_ejemplares = self.libro1.cantidad_ejemplares

        reserva.cancelar()

        reserva.refresh_from_db()
        self.libro1.refresh_from_db()

        self.assertEqual(self.libro1.cantidad_disponible, stock_antes+1)
        self.assertEqual(self.libro1.cantidad_ejemplares, stock_ejemplares)
        self.assertEqual(reserva.estado_reserva, "cancelada")


    def test_reserva_retirada_no_se_puede_cancelar(self):

        self.libro1.cantidad_disponible = 2
        self.libro1.save()

        reserva = Reserva.objects.create(
            socio=self.socio_prueba,
            libro=self.libro1,
            estado_reserva="retirada"
        )

        stock_antes = self.libro1.cantidad_disponible
        stock_ejemplares = self.libro1.cantidad_ejemplares

        with self.assertRaisesMessage(ValueError, f"No se puede cancelar una reserva en estado: {reserva.estado_reserva}"):
            reserva.cancelar()

        reserva.refresh_from_db()
        self.libro1.refresh_from_db()

        self.assertEqual(self.libro1.cantidad_disponible, stock_antes)
        self.assertEqual(self.libro1.cantidad_ejemplares, stock_ejemplares)
        self.assertEqual(reserva.estado_reserva, "retirada")


    def test_retirar_reserva_pendiente(self):
        self.libro1.cantidad_disponible = 2
        self.libro1.save()

        reserva = Reserva.objects.create(
            socio=self.socio_prueba,
            libro=self.libro1,
            estado_reserva="pendiente"
        )

        stock_antes = self.libro1.cantidad_disponible
        stock_ejemplares = self.libro1.cantidad_ejemplares

        reserva.retirar()
        reserva.refresh_from_db()
        self.libro1.refresh_from_db()

        self.assertEqual(self.libro1.cantidad_disponible, stock_antes)
        self.assertEqual(self.libro1.cantidad_ejemplares, stock_ejemplares)
        self.assertEqual(reserva.estado_reserva, "retirada")


    def test_reserva_retirada_no_puede_retirarse_nuevamente(self):
        self.libro1.cantidad_disponible = 2
        self.libro1.save()

        reserva = Reserva.objects.create(
            socio=self.socio_prueba,
            libro=self.libro1,
            estado_reserva="retirada"
        )

        stock_antes = self.libro1.cantidad_disponible
        stock_ejemplares = self.libro1.cantidad_ejemplares

        with self.assertRaisesMessage(ValueError, f"No se puede retirar una reserva en estado: retirada"):
            reserva.retirar()

        reserva.refresh_from_db()
        self.libro1.refresh_from_db()

        self.assertEqual(self.libro1.cantidad_disponible, stock_antes)
        self.assertEqual(self.libro1.cantidad_ejemplares, stock_ejemplares)
        self.assertEqual(reserva.estado_reserva, "retirada")


    def test_devolver_libro_retirado(self):
        self.libro1.cantidad_disponible = 2
        self.libro1.save()

        reserva = Reserva.objects.create(
            socio=self.socio_prueba,
            libro=self.libro1,
            estado_reserva="retirada"
        )

        stock_antes = self.libro1.cantidad_disponible
        stock_ejemplares = self.libro1.cantidad_ejemplares

        reserva.devolver()
        reserva.refresh_from_db()
        self.libro1.refresh_from_db()

        self.assertEqual(self.libro1.cantidad_disponible, stock_antes+1)
        self.assertEqual(self.libro1.cantidad_ejemplares, stock_ejemplares)
        self.assertEqual(reserva.estado_reserva, "finalizada")


    def test_reserva_finalizada_no_puede_devolverse_nuevamente(self):

        reserva = Reserva.objects.create(
            socio=self.socio_prueba,
            libro=self.libro1,
            estado_reserva="finalizada"
        )

        stock_antes = self.libro1.cantidad_disponible
        stock_ejemplares = self.libro1.cantidad_ejemplares

        with self.assertRaisesMessage(ValueError, "No se puede devolver una reserva en estado: finalizada"):
            reserva.devolver()
            
        reserva.refresh_from_db()
        self.libro1.refresh_from_db()

        self.assertEqual(self.libro1.cantidad_disponible, stock_antes)
        self.assertEqual(self.libro1.cantidad_ejemplares, stock_ejemplares)
        self.assertEqual(reserva.estado_reserva, "finalizada")


    def test_libro_no_permite_disponibles_mayores_al_total(self):
        self.libro1.cantidad_disponible = 5
        with self.assertRaises(IntegrityError):
            self.libro1.save()

    def test_libro_no_permite_stock_negativo(self):
        self.libro1.cantidad_disponible = -1
        with self.assertRaises(IntegrityError):
            self.libro1.save()
