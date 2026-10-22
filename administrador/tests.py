import json
from cliente.models import Cliente
from cliente.utils import vincular_o_crear_cliente
from django.test import TestCase
from django.urls import reverse
from cliente.models import Categoria, Producto, Inventario
from cliente.models import Pedido, DetallePedido

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

class InventarioTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre='Panaderia' , slug='panaderia')
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre='Pan de Campo',
            precio=1200.00,
            activo=True
        )
        self.inventario = Inventario.objects.create(
            producto=self.producto,
            cantidad_disponible=10,
            stock_minimo=5
        )

    def test_propiedad_es_stock_bajo(self):
        self.assertFalse(self.inventario.es_stock_bajo)

        self.inventario.cantidad_disponible = 5
        self.inventario.save()
        self.assertTrue(self.inventario.es_stock_bajo)

        self.inventario.cantidad_disponible = 2
        self.inventario.save()
        self.assertTrue(self.inventario.es_stock_bajo)

    def test_actualizar_inventario_exitoso(self):
        url = reverse('administrador:actualizar_inventario')
        datos = {
            'producto_id': self.producto.id,
            'cantidad_disponible': 20,
            'stock_minimo': 8
        }

        response = self.client.post(url, datos)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 20)
        self.assertEqual(self.inventario.stock_minimo, 8)

    def test_rechazar_inventario_negativo(self):
        url = reverse('administrador:actualizar_inventario')
        datos = {
            'producto_id': self.producto.id,
            'cantidad_disponible': -5,
            'stock_minimo': 5
        }

        response = self.client.post(url, datos)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 10)

class GestionPedidosTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(nombre="Pastelería", slug="pasteleria")
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Tarta de Frutilla",
            precio=2000.00,
            activo=True
        )
        self.inventario = Inventario.objects.create(
            producto=self.producto,
            cantidad_disponible=10,
            stock_minimo=2
        )
        self.pedido = Pedido.objects.create(
            nombre_cliente="Cliente Pruebas",
            telefono="1122334455",
            codigo_seguimiento="TEST1234",
            estado="PENDIENTE",
            monto_total=2000.00
        )
        self.detalle = DetallePedido.objects.create(
            pedido=self.pedido,
            producto=self.producto,
            precio_unitario=2000.00,
            cantidad=3
        )

    def test_cambiar_estado_pedido_exitoso(self):
        url = reverse('administrador:actualizar_estado_pedido', kwargs={'codigo': self.pedido.codigo_seguimiento})
        datos = json.dumps({'estado': 'EN_PREPARACION'})

        response = self.client.post(url, datos, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.estado, 'EN_PREPARACION')

    def test_cancelar_pedido_restaura_stock(self):
        url = reverse('administrador:actualizar_estado_pedido', kwargs={'codigo': self.pedido.codigo_seguimiento})
        datos = json.dumps({'estado': 'CANCELADO'})

        # Stock inicial es 10. Al cancelar un pedido de 3 unidades, el stock debe subir a 13.
        response = self.client.post(url, datos, content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'ok')

        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 13)

    def test_cancelar_pedido_dos_veces_no_duplica_stock(self):
        url = reverse('administrador:actualizar_estado_pedido', kwargs={'codigo': self.pedido.codigo_seguimiento})
        datos = json.dumps({'estado': 'CANCELADO'})


        self.client.post(url, datos, content_type='application/json')

        self.client.post(url, datos, content_type='application/json')

        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 13)

    def test_filtrar_pedidos_por_estado(self):

        Pedido.objects.create(
            nombre_cliente="Cliente 2",
            telefono="1100000000",
            codigo_seguimiento="TEST5678",
            estado="EN_PREPARACION",
            monto_total=1500.00
        )

        url = reverse('administrador:dashboard') + '?estado=EN_PREPARACION'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        pedidos_contexto = response.context['pedidos']
        self.assertTrue(all(p.estado == 'EN_PREPARACION' for p in pedidos_contexto))

    def test_buscar_pedidos_por_codigo_o_cliente(self):
        url = reverse('administrador:dashboard') + '?q=TEST1234'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        pedidos_contexto = response.context['pedidos']
        self.assertEqual(len(pedidos_contexto), 1)
        self.assertEqual(pedidos_contexto[0].codigo_seguimiento, "TEST1234")

class GestionClientesTests(TestCase):
    def setUp(self):
        self.cliente = Cliente.objects.create(
            nombre="Laura Gómez",
            telefono="1199887766",
            direccion_habitual="Av. Rivadavia 1234"
        )
        self.pedido = Pedido.objects.create(
            cliente=self.cliente,
            nombre_cliente=self.cliente.nombre,
            telefono=self.cliente.telefono,
            codigo_seguimiento="CLIE1234",
            estado="ENTREGADO",
            monto_total=4500.00
        )

    def test_vincular_o_crear_cliente_existente_actualiza_datos(self):
        cliente_actualizado = vincular_o_crear_cliente(
            nombre="Laura G. Gómez",
            telefono="1199887766",
            direccion="Av. Belgrano 5678"
        )

        self.assertEqual(cliente_actualizado.id, self.cliente.id)
        self.assertEqual(cliente_actualizado.nombre, "Laura G. Gómez")
        self.assertEqual(cliente_actualizado.direccion_habitual, "Av. Belgrano 5678")

    def test_vincular_o_crear_cliente_nuevo(self):
        nuevo_cliente = vincular_o_crear_cliente(
            nombre="Carlos Pérez",
            telefono="1133445566",
            direccion="Calle Falsa 123"
        )

        self.assertIsNotNone(nuevo_cliente)
        self.assertEqual(nuevo_cliente.telefono, "1133445566")
        self.assertTrue(Cliente.objects.filter(telefono="1133445566").exists())

    def test_listar_clientes_api(self):
        url = reverse('administrador:listar_clientes') + '?q=Laura'
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        datos = response.json()
        self.assertEqual(datos['status'], 'ok')
        self.assertEqual(len(datos['clientes']), 1)
        self.assertEqual(datos['clientes'][0]['telefono'], "1199887766")
        self.assertEqual(datos['clientes'][0]['total_gastado'], 4500.0)

    def test_detalle_cliente_api(self):
        url = reverse('administrador:detalle_cliente', kwargs={'cliente_id': self.cliente.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        datos = response.json()
        self.assertEqual(datos['status'], 'ok')
        self.assertEqual(datos['cliente']['nombre'], "Laura Gómez")
        self.assertEqual(len(datos['cliente']['pedidos']), 1)
        self.assertEqual(datos['cliente']['pedidos'][0]['codigo'], "CLIE1234")