# Sistema de Biblioteca — Python y Django

Sistema de gestión de biblioteca ejecutado **íntegramente desde la consola**, desarrollado como trabajo práctico de **Diseño de Sistemas Orientado a Objetos**.

El proyecto utiliza Django como soporte para el modelado de entidades, las relaciones, las reglas de negocio y la persistencia mediante su ORM. **No utiliza interfaz web.**

## Funcionalidades

- Registrar libros y socios.
- Buscar libros por **ISBN**, **título** o **autor** (coincidencias parciales por título y autor).
- Listar libros, socios y reservas.
- Solicitar una reserva de un libro disponible.
- Cancelar reservas pendientes.
- Registrar el retiro de un libro reservado.
- Registrar la devolución y finalizar la reserva.
- Controlar los estados de reserva y actualizar la disponibilidad de ejemplares.
- Validar datos de entrada y manejar errores habituales de forma controlada.

## Tecnologías y conceptos

- **Python** y **Django**
- **SQLite** y **Django ORM**
- **Programación orientada a objetos (POO)**
- **Relaciones entre modelos** mediante `ForeignKey`
- **Servicios** para separar la interacción por consola de las operaciones del sistema
- **Transacciones atómicas**, restricciones de integridad y validaciones de modelos
- **Pruebas automatizadas** con `django.test.TestCase`
- **Git y GitHub** para control de versiones

## Reglas de negocio

- Un socio inactivo no puede realizar nuevas reservas.
- Una reserva requiere ejemplares disponibles.
- Un socio no puede tener simultáneamente dos reservas activas del **mismo libro**.
- Solicitar una reserva disminuye la cantidad disponible en una unidad.
- Solo se puede cancelar una reserva **pendiente**; al cancelarla se recupera el ejemplar.
- Retirar un libro cambia la reserva de **pendiente** a **retirada**, sin descontar stock nuevamente.
- Devolver un libro cambia la reserva de **retirada** a **finalizada** y recupera el ejemplar disponible.
- Los ejemplares disponibles no pueden ser negativos ni superar la cantidad total.

## Requisitos

- Python compatible con la versión de Django indicada en `requirements.txt`.
- `pip` y un entorno virtual de Python.

## Instalación y ejecución

**1. Clonar el repositorio**

```bash
git clone https://github.com/0nileo/Proyecto_Biblioteca.git
cd Proyecto_Biblioteca
```

**2. Crear y activar un entorno virtual**

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Instalar dependencias**

```bash
python -m pip install -r requirements.txt
```

**4. Configurar variables de entorno**

Crear un archivo `.env` en la raíz del proyecto con una clave local de desarrollo:

```dotenv
DJANGO_SECRET_KEY=coloca-aqui-una-clave-secreta-de-desarrollo
```

Podés generar una clave con Python y Django instalados:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**No subir el archivo `.env` ni claves reales a Git.**

**5. Preparar la base de datos**

```bash
python manage.py migrate
```

**6. Iniciar la aplicación**

```bash
python manage.py biblioteca
```

La aplicación mostrará un menú interactivo para realizar las operaciones desde la consola. La base de datos SQLite se crea localmente; los registros de cada instalación no se sincronizan mediante Git.

## Pruebas automatizadas

```bash
python manage.py test biblioteca_app
```

Se incluyen pruebas de las principales reglas de reserva, transiciones de estado y restricciones de disponibilidad.

## Organización del código

```text
Proyecto_Biblioteca/
├── biblioteca/                 # Configuración del proyecto Django
├── biblioteca_app/
│   ├── models.py               # Libro, Socio y Reserva
│   ├── services.py             # Operaciones utilizadas por la consola
│   ├── tests.py                # Pruebas automatizadas
│   └── management/
│       └── commands/
│           └── biblioteca.py   # Comando y menú interactivo
├── manage.py
└── requirements.txt
```

## Estado del proyecto

**Proyecto académico en desarrollo.** El circuito principal de libros, socios y reservas está implementado. Entre las mejoras previstas se encuentran consultas y filtros adicionales del ORM, validaciones más completas, documentación de clases y funcionalidades opcionales como estadísticas y exportación CSV.

## Repositorio

[GitHub — Proyecto_Biblioteca](https://github.com/0nileo/Proyecto_Biblioteca)
