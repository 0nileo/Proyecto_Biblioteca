"""Carga datos ficticios para probar Proyecto Biblioteca.

Ejecutar desde la raíz del proyecto:

python manage.py cargar_datos

No borra ni modifica registros existentes. Si una clave ya existe,
se omite ese registro. Los ISBN y DNI son identificadores ficticios.
"""

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from biblioteca_app.models import Libro, Socio


# ISBN ficticios de 13 dígitos, solamente para datos de demostración.
# No deben interpretarse como ISBN reales de las obras.
LIBROS = [
    {"titulo": "Dune", "autor": "Frank Herbert", "isbn": "9900000000001", "anio_publicacion": 1965, "ejemplares": 5},
    {"titulo": "El Principito", "autor": "Antoine de Saint-Exupéry", "isbn": "9900000000002", "anio_publicacion": 1943, "ejemplares": 3},
    {"titulo": "El Hobbit", "autor": "J. R. R. Tolkien", "isbn": "9900000000003", "anio_publicacion": 1937, "ejemplares": 4},
    {"titulo": "La comunidad del anillo", "autor": "J. R. R. Tolkien", "isbn": "9900000000004", "anio_publicacion": 1954, "ejemplares": 2},
    {"titulo": "1984", "autor": "George Orwell", "isbn": "9900000000005", "anio_publicacion": 1949, "ejemplares": 6},
    {"titulo": "Fundación", "autor": "Isaac Asimov", "isbn": "9900000000006", "anio_publicacion": 1951, "ejemplares": 0},
    {"titulo": "Fahrenheit 451", "autor": "Ray Bradbury", "isbn": "9900000000007", "anio_publicacion": 1953, "ejemplares": 3},
    {"titulo": "Drácula", "autor": "Bram Stoker", "isbn": "9900000000008", "anio_publicacion": 1897, "ejemplares": 2},
    {"titulo": "Frankenstein", "autor": "Mary Shelley", "isbn": "9900000000009", "anio_publicacion": 1818, "ejemplares": 0},
    {"titulo": "Orgullo y prejuicio", "autor": "Jane Austen", "isbn": "9900000000010", "anio_publicacion": 1813, "ejemplares": 5},
]

SOCIOS = [
    {"numero_socio": "SOC001", "nombre": "Ana", "apellido": "García", "dni": "90000001", "email": "ana.garcia@example.com", "estado": "activo"},
    {"numero_socio": "SOC002", "nombre": "Bruno", "apellido": "López", "dni": "90000002", "email": "bruno.lopez@example.com", "estado": "activo"},
    {"numero_socio": "SOC003", "nombre": "Carla", "apellido": "Fernández", "dni": "90000003", "email": "carla.fernandez@example.com", "estado": "activo"},
    {"numero_socio": "SOC004", "nombre": "Diego", "apellido": "Pérez", "dni": "90000004", "email": "diego.perez@example.com", "estado": "activo"},
    {"numero_socio": "SOC005", "nombre": "Elena", "apellido": "Martínez", "dni": "90000005", "email": "elena.martinez@example.com", "estado": "activo"},
    {"numero_socio": "SOC006", "nombre": "Facundo", "apellido": "Ruiz", "dni": "90000006", "email": "facundo.ruiz@example.com", "estado": "activo"},
    {"numero_socio": "SOC007", "nombre": "Gabriela", "apellido": "Torres", "dni": "90000007", "email": "gabriela.torres@example.com", "estado": "activo"},
    {"numero_socio": "SOC008", "nombre": "Hugo", "apellido": "Romero", "dni": "90000008", "email": "hugo.romero@example.com", "estado": "activo"},
    {"numero_socio": "SOC009", "nombre": "Inés", "apellido": "Castro", "dni": "90000009", "email": "ines.castro@example.com", "estado": "inactivo"},
    {"numero_socio": "SOC010", "nombre": "Julián", "apellido": "Morales", "dni": "90000010", "email": "julian.morales@example.com", "estado": "inactivo"},
]


class Command(BaseCommand):
    help = "Carga 10 libros y 10 socios ficticios sin duplicar registros existentes"

    def handle(self, *args, **options):
        libros_creados = 0
        socios_creados = 0

        # Todo el lote es una transacción: si un registro falla,
        # no queda una carga a medias.
        try:
            with transaction.atomic():
                for datos in LIBROS:
                    # Verificamos la clave única. No cambiamos libros ya cargados.
                    if Libro.objects.filter(isbn=datos["isbn"]).exists():
                        continue

                    libro = Libro(
                        titulo=datos["titulo"],
                        autor=datos["autor"],
                        isbn=datos["isbn"],
                        anio_publicacion=datos["anio_publicacion"],
                        cantidad_ejemplares=datos["ejemplares"],
                        cantidad_disponible=datos["ejemplares"],
                    )
                    libro.full_clean()
                    libro.save()
                    libros_creados += 1

                for datos in SOCIOS:
                    if Socio.objects.filter(numero_socio=datos["numero_socio"]).exists():
                        continue

                    socio = Socio(**datos)
                    socio.full_clean()
                    socio.save()
                    socios_creados += 1
        except (ValidationError, IntegrityError) as error:
            raise CommandError(
                f"No se cargaron datos: {error}. "
                "Revisá si algún DNI o identificador ya está utilizado."
            ) from error

        self.stdout.write(self.style.SUCCESS(
            f"Carga completada: {libros_creados} libros nuevos y "
            f"{socios_creados} socios nuevos."
        ))
        self.stdout.write(
            "Los registros existentes se conservaron. "
            "Podés ejecutar este comando nuevamente sin duplicar estos datos."
        )
