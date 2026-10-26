import json
from cliente.models import Cliente
from cliente.utils import vincular_o_crear_cliente
from django.test import TestCase
from django.urls import reverse
from cliente.models import Categoria, Producto, Inventario
from cliente.models import Pedido, DetallePedido
from administrador.utils import generar_datos_dashboard
from django.utils import timezone
from cliente.models import Pedido, DetallePedido, Categoria, Producto, Inventario, Insumo
from django.contrib.auth.models import User

class CRUDProductosTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='crud_productos_admin', password='Password123!', is_staff=True)
        self.client.login(username='crud_productos_admin', password='Password123!')
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
    def setUp(self):
        User.objects.create_user(username='crud_categorias_admin', password='Password123!', is_staff=True)
        self.client.login(username='crud_categorias_admin', password='Password123!')

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
        User.objects.create_user(username='inventario_admin', password='Password123!', is_staff=True)
        self.client.login(username='inventario_admin', password='Password123!')
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

    def test_inventario_invalido_no_crea_registro(self):
        producto = Producto.objects.create(
            categoria=self.categoria,
            nombre='Producto sin stock inicial',
            precio=1000.00,
            activo=True,
        )
        response = self.client.post(
            reverse('administrador:actualizar_inventario'),
            {'producto_id': producto.id, 'cantidad_disponible': '-1'},
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(Inventario.objects.filter(producto=producto).exists())

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

class InsumoRestockTests(TestCase):
    def setUp(self):
        User.objects.create_user(username='insumos_admin', password='Password123!', is_staff=True)
        self.client.login(username='insumos_admin', password='Password123!')
        self.insumo = Insumo.objects.create(
            nombre='Harina',
            unidad_medida='kg',
            cantidad_disponible='2.500',
            stock_minimo='1.000',
        )

    def test_reponer_insumo_persiste_cantidad_decimal(self):
        response = self.client.post(
            reverse('administrador:reponer_insumo'),
            {'insumo_id': self.insumo.id, 'cantidad_reponer': '1.250'},
        )
        self.assertEqual(response.status_code, 200)
        self.insumo.refresh_from_db()
        self.assertEqual(str(self.insumo.cantidad_disponible), '3.750')

    def test_rechaza_reposicion_cero_o_precision_excesiva(self):
        for cantidad in ('0', '-1', '0.0001'):
            with self.subTest(cantidad=cantidad):
                response = self.client.post(
                    reverse('administrador:reponer_insumo'),
                    {'insumo_id': self.insumo.id, 'cantidad_reponer': cantidad},
                )
                self.assertEqual(response.status_code, 400)
        self.insumo.refresh_from_db()
        self.assertEqual(str(self.insumo.cantidad_disponible), '2.500')


class GestionPedidosTests(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='admin_pedidos', password='password123', is_staff=True)
        self.client.login(username='admin_pedidos', password='password123')

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

    def test_no_permite_cancelar_pedido_ya_entregado(self):
        self.pedido.estado = 'ENTREGADO'
        self.pedido.save(update_fields=['estado'])
        url = reverse('administrador:actualizar_estado_pedido', kwargs={'codigo': self.pedido.codigo_seguimiento})
        response = self.client.post(url, json.dumps({'estado': 'CANCELADO'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 10)

    def test_no_permite_reabrir_pedido_cancelado(self):
        url = reverse('administrador:actualizar_estado_pedido', kwargs={'codigo': self.pedido.codigo_seguimiento})
        self.client.post(url, json.dumps({'estado': 'CANCELADO'}), content_type='application/json')
        response = self.client.post(url, json.dumps({'estado': 'PENDIENTE'}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 13)

    def test_archivar_pedido_entregado_lo_conserva_en_base_y_lo_oculta_de_activos(self):
        self.pedido.estado = 'ENTREGADO'
        self.pedido.save(update_fields=['estado'])
        url = reverse('administrador:archivar_pedido', kwargs={'codigo': self.pedido.codigo_seguimiento})
        response = self.client.post(url, json.dumps({'archivado': True}), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.pedido.refresh_from_db()
        self.assertTrue(self.pedido.archivado)
        self.assertTrue(Pedido.objects.filter(pk=self.pedido.pk).exists())
        dashboard = self.client.get(reverse('administrador:dashboard'))
        self.assertFalse(dashboard.context['pedidos'].filter(pk=self.pedido.pk).exists())
        self.assertEqual(len(dashboard.context['pedidos_archivados_data']), 1)
        self.assertEqual(dashboard.context['pedidos_archivados_data'][0]['codigo'], self.pedido.codigo_seguimiento)
        self.assertEqual(generar_datos_dashboard()['kpis']['ingresos_totales'], 2000.0)

    def test_no_permite_archivar_pedido_pendiente(self):
        url = reverse('administrador:archivar_pedido', kwargs={'codigo': self.pedido.codigo_seguimiento})
        response = self.client.post(url, json.dumps({'archivado': True}), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.pedido.refresh_from_db()
        self.assertFalse(self.pedido.archivado)

    def test_restaurar_pedido_archivado_lo_devuelve_a_activos(self):
        self.pedido.estado = 'ENTREGADO'
        self.pedido.archivado = True
        self.pedido.save(update_fields=['estado', 'archivado'])
        url = reverse('administrador:archivar_pedido', kwargs={'codigo': self.pedido.codigo_seguimiento})
        response = self.client.post(url, json.dumps({'archivado': False}), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.pedido.refresh_from_db()
        self.assertFalse(self.pedido.archivado)
        self.assertTrue(self.client.get(reverse('administrador:dashboard')).context['pedidos'].filter(pk=self.pedido.pk).exists())

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
        User.objects.create_user(username='clientes_admin', password='Password123!', is_staff=True)
        self.client.login(username='clientes_admin', password='Password123!')
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

class DashboardMetricasTests(TestCase):
    def setUp(self):

        self.user = User.objects.create_user(username='admin_metricas', password='password123', is_staff=True)
        self.client.login(username='admin_metricas', password='password123')

        self.categoria = Categoria.objects.create(
            nombre="Cafetería",
            slug="cafeteria"
        )
        self.producto = Producto.objects.create(
            nombre="Café Doble",
            categoria=self.categoria,
            precio=1200.00,
            activo=True
        )
        # Crear el objeto de inventario relacionado con el producto
        self.inventario = Inventario.objects.create(
            producto=self.producto,
            cantidad_disponible=50
        )
        self.pedido_completado = Pedido.objects.create(
            nombre_cliente="Cliente Test Metrics",
            telefono="1100110011",
            codigo_seguimiento="METR1234",
            estado="ENTREGADO",
            monto_total=2400.00
        )
        DetallePedido.objects.create(
            pedido=self.pedido_completado,
            producto=self.producto,
            cantidad=2,
            precio_unitario=1200.00
        )
        self.pedido_cancelado = Pedido.objects.create(
            nombre_cliente="Cliente Cancelado",
            telefono="1199999999",
            codigo_seguimiento="CANC1234",
            estado="CANCELADO",
            monto_total=1200.00
        )

    def test_generar_datos_dashboard_excluye_cancelados(self):
        datos = generar_datos_dashboard()

        # KPIs
        self.assertEqual(datos['kpis']['ingresos_totales'], 2400.00)
        self.assertEqual(datos['kpis']['cantidad_pedidos'], 1)
        self.assertEqual(datos['kpis']['ticket_promedio'], 2400.00)
        self.assertEqual(datos['kpis']['ventas_hoy'], 2400.00)
        self.assertEqual(datos['kpis']['pedidos_hoy'], 1)
        self.assertEqual(datos['kpis']['unidades_hoy'], 2)
        self.assertEqual(datos['kpis']['ingresos_7_dias'], 2400.00)

        # Estructura de gráficos
        self.assertIn('days', datos['trend_data'])
        self.assertIn('weeks', datos['trend_data'])
        self.assertIn('months', datos['trend_data'])
        self.assertIn('days', datos['pie_data'])

        # Top productos
        self.assertEqual(len(datos['top_productos']), 1)
        self.assertEqual(datos['top_productos'][0]['producto__nombre'], "Café Doble")

    def test_ingresos_dashboard_no_cuenta_pedidos_pendientes(self):
        Pedido.objects.create(
            nombre_cliente="Cliente pendiente", telefono="1100220099",
            codigo_seguimiento="PEND1234", estado="PENDIENTE", monto_total=9900.00
        )
        datos = generar_datos_dashboard()
        self.assertEqual(datos['kpis']['ingresos_totales'], 2400.00)
        self.assertEqual(datos['kpis']['cantidad_pedidos'], 1)

    def test_grafico_categoria_suma_subtotales_reales(self):
        otro_producto = Producto.objects.create(
            nombre="Té", categoria=self.categoria, precio=500.00, activo=True
        )
        pedido = Pedido.objects.create(
            nombre_cliente="Cliente categoría", telefono="1100220033",
            codigo_seguimiento="CATG1234", estado="ENTREGADO", monto_total=3900.00
        )
        DetallePedido.objects.create(
            pedido=pedido, producto=self.producto, cantidad=2, precio_unitario=1200.00
        )
        DetallePedido.objects.create(
            pedido=pedido, producto=otro_producto, cantidad=3, precio_unitario=500.00
        )
        datos = generar_datos_dashboard()
        self.assertEqual(datos['pie_data']['days']['data'][0], 6300.0)

    def test_dashboard_no_falla_si_producto_no_tiene_inventario(self):
        Producto.objects.create(
            nombre="Producto sin inventario", categoria=self.categoria,
            precio=800.00, activo=True
        )
        response = self.client.get(reverse('administrador:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_vista_dashboard_incluye_contexto_metricas(self):
        url = reverse('administrador:dashboard')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('kpis', response.context)
        self.assertIn('trend_data', response.context)
        self.assertIn('pie_data', response.context)

class AutenticacionSeguridadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin_test',
            password='Password123!',
            is_staff=True
        )

    def test_dashboard_requiere_login(self):
        url = reverse('administrador:dashboard')
        response = self.client.get(url)

        # Debe redirigir al login
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_endpoint_de_escritura_requiere_autenticacion(self):
        response = self.client.post(reverse('administrador:crear_categoria'), {'nombre': 'Sin permiso'})
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('administrador:login'), response.url)
        self.assertFalse(Categoria.objects.filter(nombre='Sin permiso').exists())

    def test_usuario_no_staff_no_puede_iniciar_sesion_admin(self):
        User.objects.create_user(username='cliente_comun', password='Password123!')
        response = self.client.post(reverse('administrador:login'), {
            'username': 'cliente_comun', 'password': 'Password123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_rechaza_redireccion_externa(self):
        response = self.client.post(reverse('administrador:login'), {
            'username': 'admin_test', 'password': 'Password123!',
            'next': 'https://sitio-malicioso.example'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administrador:dashboard'))

    def test_login_exitoso_redirige_al_dashboard(self):
        url = reverse('administrador:login')
        response = self.client.post(url, {
            'username': 'admin_test',
            'password': 'Password123!'
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administrador:dashboard'))

    def test_login_fallido_muestra_error(self):
        url = reverse('administrador:login')
        response = self.client.post(url, {
            'username': 'admin_test',
            'password': 'ClaveIncorrecta'
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn('error', response.context)
        self.assertEqual(response.context['error'], "Usuario o contraseña incorrectos.")

    def test_logout_cierra_sesion(self):
        self.client.login(username='admin_test', password='Password123!')
        url = reverse('administrador:logout')
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('administrador:login'))