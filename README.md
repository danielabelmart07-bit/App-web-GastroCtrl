# GastroCtrl

Aplicación web Django para gestionar una tienda gastronómica (panadería, cafetería o negocio similar). El proyecto está en desarrollo: el flujo público, catálogo, carrito, checkout y panel administrativo están en construcción por etapas.

## Requisitos

- Python compatible con la versión de Django indicada en `requirements.txt`.
- Git.
- Un entorno virtual de Python.

## Instalación local

Desde la carpeta del proyecto:

```bash
python -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Editá `.env` y reemplazá `DJANGO_SECRET_KEY` por una clave aleatoria local. No subas el archivo `.env` a Git.

Aplicá migraciones y creá un usuario administrador:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Tienda pública: `http://127.0.0.1:8000/`
- Panel de gestión: `http://127.0.0.1:8000/gestion/`
- Administración de Django: `http://127.0.0.1:8000/admin/`

El acceso al panel `/gestion/` requiere un usuario activo con permiso de personal (`is_staff=True`). Para el entorno local, podés crear un superusuario o marcar un usuario existente como personal desde el admin de Django.

## Pruebas

Ejecutá toda la suite de pruebas con:

```bash
python manage.py test
```

Comprobación general de Django:

```bash
python manage.py check
```

## Variables de entorno

| Variable | Uso |
|---|---|
| `DJANGO_SECRET_KEY` | Clave secreta de Django; obligatoria |
| `DJANGO_DEBUG` | `True` solo para desarrollo local; por defecto `False` |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos separados por comas |

## Estado del proyecto

GastroCtrl todavía no está listo para producción. Antes de desplegarlo, deben validarse las pruebas, configurarse una base de datos de producción y revisar HTTPS, archivos estáticos/media, copias de seguridad, monitorización y el resto de la lista de despliegue.
