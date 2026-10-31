# GastroCtrl

Aplicación web de gestión gastronómica desarrollada con **Python y Django**, pensada para pequeños y medianos negocios del rubro gastronómico, como panaderías y cafeterías.

GastroCtrl tiene un sitio público para clientes y un panel privado para administrar el negocio.

## Funcionalidades

### Sitio público — Clientes

- Página de inicio y catálogo de productos.
- Visualización de productos por categorías y búsqueda en el menú.
- Registro, inicio de sesión y perfil de cliente.
- Carrito de compras: agregar, restar y quitar productos.
- Checkout y generación de pedidos.
- Selección de modalidad de entrega (retiro o delivery).
- Consulta del estado del pedido mediante código de seguimiento.

### Panel de administración

- Inicio de sesión para administradores.
- Dashboard de gestión.
- Alta, consulta, edición y eliminación de productos.
- Administración de categorías.
- Gestión de inventario de productos y niveles mínimos de stock.
- Registro y control de insumos.
- Consulta y actualización del estado de los pedidos.
- Archivo y restauración de pedidos.
- Consulta de clientes.
- Configuración del costo de envío y del perfil administrativo.

## Tecnologías

- **Python**
- **Django 6.1.2**
- **SQLite**
- **HTML, CSS y JavaScript**
- **Pillow** para el manejo de imágenes.
- **python-dotenv** para cargar variables de entorno desde un archivo `.env`.

Las dependencias del proyecto estan declaradas en `requirements.txt`.

## Requisitos previos

- Python instalado.
- Git.
- pip (administrador de paquetes de Python).

## Instalación y ejecución local

### 1. Clonar el repositorio

```bash
git clone https://github.com/danielabelmart07-bit/App-web-GastroCtrl.git
cd App-web-GastroCtrl
```

### 2. Crear y activar un entorno virtual

**Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell o CMD):**

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar las dependencias

Con el entorno virtual activado:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

En la carpeta raíz del proyecto, crear un archivo llamado `.env`.

Debe contener estas variables:

```env
DJANGO_SECRET_KEY=pegar_aqui_una_clave_secreta
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Para generar una clave secreta, ejecutar:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiar el valor generado y colocarlo en `DJANGO_SECRET_KEY` dentro del archivo `.env`.

### 5. Ejecutar las migraciones de la base de datos

El repositorio incluye las migraciones del proyecto. Para crear o actualizar la base de datos local, ejecutar:

```bash
python manage.py migrate
```

Si en el futuro se modifican los modelos durante el desarrollo, primero generar las migraciones correspondientes y luego aplicarlas:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear un usuario administrador

Para acceder al panel administrativo, crear un superusuario:

```bash
python manage.py createsuperuser
```

Seguir las indicaciones de la terminal para definir nombre de usuario, correo electrónico (si corresponde) y contraseña.

### 7. Iniciar el servidor de desarrollo

```bash
python manage.py runserver
```

Abrir el navegador en:

- Sitio público: http://127.0.0.1:8000/
- Inicio de sesión del panel GastroCtrl: http://127.0.0.1:8000/gestion/login/
- Administración nativa de Django: http://127.0.0.1:8000/admin/

## Ejecutar las pruebas

Para ejecutar las pruebas automatizadas del proyecto:

```bash
python manage.py test
```

## Estructura general

```text
App-web-GastroCtrl/
├── administrador/       # Panel y lógica de administración
├── cliente/              # Sitio público, clientes, carrito y pedidos
├── gastroctrl/           # Configuración principal de Django
├── static/               # Archivos estáticos
├── templates/            # Plantillas HTML compartidas
├── requirements.txt      # Dependencias del proyecto
├── manage.py             # Utilidad de administración de Django
└── .env                  # Variables locales (no se versiona)
```

Los archivos multimedia cargados por la aplicación se almacenan en `media/`. Las carpetas `venv/` y `.venv/`, el archivo `.env` y la base de datos local `db.sqlite3` están excluidos del control de versiones.

## Autor

Desarrollado como proyecto de aplicación web para la gestión integral de un negocio gastronómico.
