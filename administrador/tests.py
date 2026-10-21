from django.test import TestCase
from django.urls import reverse
from cliente.models import Categoria, Producto, Inventario

class CRUDProductosTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre='Cafeteria',
            slug='cafeteria'
        )

    def test_crear_producto_exitoso(self):
        url = reverse('administrador:crear_producto')
        datos = {
            'categoria': self.categoria.id,
            'nombre' : 'Cafe Espresso',
            'descripcion' : 'Cafe concentrado',
            'precio' : 2500.00,
            'stock' : 15,
            'activo' : True,
            'es_destacado' : False,
        }

        response = self.client.post(url, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

        producto = Producto.objects.get(nombre='Cafe Espresso')
        self.assertEqual(producto.precio, 2500.00)

        self.assertTrue(hasattr(producto, 'inventario'))
        self.assertEqual(producto.inventario.cantidad_disponible, 15)

    def test_editar_producto_exitoso(self):
        producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Medialuna de Manteca",
            descripcion="Clasica medialuna de manteca",
            precio=1500.00,
            activo=True,
        )
        Inventario.objects.create(
            producto=producto,
            cantidad_disponible=10
        )

        url = reverse('administrador:editar_producto')
        datos = {
            'id': producto.id,
            'categoria': self.categoria.id,
            'nombre': 'Medialuna de Manteca Rellena',
            'descripcion': 'Medialuna rellena de dulce de leche',
            'precio': 1200.00,
            'stock': 25,
            'activo': True,
            'es_destacado': True,
        }

        response = self.client.post(url, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

        producto.refresh_from_db()
        self.assertEqual(producto.nombre, 'Medialuna de Manteca Rellena')
        self.assertEqual(producto.precio, 1200.00)
        self.assertTrue(producto.es_destacado)
        self.assertEqual(producto.inventario.cantidad_disponible, 25)

    def test_eliminar_producto_exitoso(self):
        producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Torta de Limon",
            precio=3000.00,
            activo=True,
        )

        url = reverse('administrador:eliminar_producto')
        response = self.client.post(url, {'id': producto.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertFalse(Producto.objects.filter(id=producto.id).exists())

class CRUDCategoriasTests(TestCase):
    def test_crear_categoria_con_slug_autogenerado(self):
        url = reverse('administrador:crear_categoria')
        datos = {'nombre': 'Bebidas Calientes'}

        response = self.client.post(url, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

        categoria = Categoria.objects.get(nombre='Bebidas Calientes')
        self.assertEqual(categoria.slug, 'bebidas-calientes')

    def test_editar_categoria_exitoso(self):
        categoria = Categoria.objects.create(nombre='Panes', slug='panes')

        url = reverse('administrador:editar_categoria')
        datos = {
            'id': categoria.id,
            'nombre': 'Panes Artesanales',
            'slug': 'panes-artesanales'
        }

        response = self.client.post(url, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

        categoria.refresh_from_db()
        self.assertEqual(categoria.nombre, 'Panes Artesanales')
        self.assertEqual(categoria.slug, 'panes-artesanales')

    def test_eliminar_categoria_sin_productos(self):
        categoria = Categoria.objects.create(nombre='Especiales', slug='especiales')

        url = reverse('administrador:eliminar_categoria')
        response = self.client.post(url, {'id': categoria.id})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.assertFalse(Categoria.objects.filter(id=categoria.id).exists())

    def test_impedir_eliminar_categoria_con_productos(self):
        categoria = Categoria.objects.create(nombre='Postres', slug='postres')
        Producto.objects.create(
            categoria=categoria,
            nombre='Flan Casero',
            precio=1500.00,
            activo=True
        )

        url = reverse('administrador:eliminar_categoria')
        response = self.client.post(url, {'id': categoria.id})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')
        self.assertTrue(Categoria.objects.filter(id=categoria.id).exists())