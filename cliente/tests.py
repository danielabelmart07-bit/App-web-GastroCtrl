from django.test import TestCase
from decimal import Decimal
from django.test import TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from .models import Categoria, Producto
from .carrito import Carrito
from django.urls import reverse
from .models import Inventario, Pedido, DetallePedido, Cliente, Insumo, RecetaInsumo, ConsumoInsumoPedido


class CarritoTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre="Panadería",
            slug="panaderia",
        )
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Medialuna",
            precio=Decimal("1200.00"),
        )

        request = HttpRequest()
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)
        request.session.save()

        self.carrito = Carrito(request)

    def test_agregar_producto_y_calcular_total(self):
        self.carrito.agregar(self.producto)

        self.assertEqual(self.carrito.obtener_total_unidades(), 1)
        self.assertEqual(
            self.carrito.obtener_precio_total(),
            Decimal("1200.00"),
        )

    def test_iterar_carrito_no_guarda_decimal_en_la_sesion(self):
        self.carrito.agregar(self.producto)
        list(self.carrito)
        # Simula el guardado de sesión que ocurre al finalizar una respuesta.
        self.carrito.session.save()
        self.assertEqual(self.carrito.obtener_precio_total(), Decimal('1200.00'))

    def test_no_agregar_cantidades_invalidas(self):
        with self.assertRaises(ValueError):
            self.carrito.agregar(self.producto, cantidad=0)

        with self.assertRaises(ValueError):
            self.carrito.agregar(self.producto, cantidad=-1)

    def test_restar_producto_hasta_eliminarlo(self):
        self.carrito.agregar(self.producto)
        self.carrito.restar(self.producto)

        self.assertEqual(self.carrito.obtener_total_unidades(), 0)
        self.assertEqual(self.carrito.obtener_precio_total(), Decimal("0"))

    def test_eliminar_producto_del_carrito(self):
        self.carrito.agregar(self.producto)
        self.carrito.eliminar(self.producto)

        self.assertEqual(self.carrito.obtener_total_unidades(), 0)
        self.assertEqual(self.carrito.obtener_precio_total(), Decimal("0"))

class CheckoutTests(TestCase):
    def setUp(self):
        self.categoria = Categoria.objects.create(
            nombre="Pastelería",
            slug="pasteleria",
        )
        self.producto = Producto.objects.create(
            categoria=self.categoria,
            nombre="Torta",
            precio=Decimal("5000.00"),
        )
        self.inventario = Inventario.objects.create(
            producto=self.producto,
            cantidad_disponible=5,
        )

        session = self.client.session
        session["carrito"] = {
            str(self.producto.id): {
                "producto_id": self.producto.id,
                "nombre": self.producto.nombre,
                "precio": str(self.producto.precio),
                "cantidad": 2,
                "imagen": "/static/cliente/img/placeholder.jpg",
            }
        }
        session.save()

    def test_checkout_descuenta_stock_y_crea_pedido(self):
        respuesta = self.client.post(
            reverse("cliente:checkout"),
            {
                "nombre_cliente": "Juan Pérez",
                "telefono": "1122334455",
                "direccion": "",
                "notas": "",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 1)
        self.assertEqual(DetallePedido.objects.count(), 1)
        pedido = Pedido.objects.get()
        self.assertIsNotNone(pedido.cliente)
        self.assertEqual(pedido.cliente.telefono, '1122334455')
        self.assertEqual(pedido.cliente.direccion_habitual, '')

        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 3)

    def test_checkout_rechaza_cantidad_superior_al_stock(self):
        session = self.client.session
        carrito = session["carrito"]
        carrito[str(self.producto.id)]["cantidad"] = 6
        session["carrito"] = carrito
        session.save()

        respuesta = self.client.post(
            reverse("cliente:checkout"),
            {
                "nombre_cliente": "Juan Pérez",
                "telefono": "1122334455",
                "direccion": "",
                "notas": "",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 0)

        self.inventario.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 5)

    def test_checkout_muestra_precio_actualizado_desde_base_de_datos(self):
        self.producto.precio = Decimal('6000.00')
        self.producto.save(update_fields=['precio'])
        respuesta = self.client.get(reverse('cliente:checkout'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['subtotal'], Decimal('12000.00'))

    def test_checkout_informa_si_producto_dejo_de_estar_activo(self):
        self.producto.activo = False
        self.producto.save(update_fields=['activo'])
        respuesta = self.client.post(
            reverse('cliente:checkout'),
            {
                'nombre_cliente': 'Juan Pérez',
                'telefono': '1122334455',
                'direccion': '',
                'notas': '',
            },
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertTrue(respuesta.context['form'].non_field_errors())

    def test_checkout_rechaza_producto_sin_inventario(self):
        self.inventario.delete()

        respuesta = self.client.post(
            reverse("cliente:checkout"),
            {
                "nombre_cliente": "Juan Pérez",
                "telefono": "1122334455",
                "direccion": "",
                "notas": "",
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 0)

    def test_checkout_descuenta_insumos_segun_receta_y_guarda_historial(self):
        insumo = Insumo.objects.create(
            nombre='Harina para receta',
            unidad_medida='kg',
            cantidad_disponible=Decimal('2.500'),
            stock_minimo=Decimal('0.500'),
        )
        RecetaInsumo.objects.create(
            producto=self.producto,
            insumo=insumo,
            cantidad_por_unidad=Decimal('0.250'),
        )

        respuesta = self.client.post(
            reverse('cliente:checkout'),
            {
                'nombre_cliente': 'Juan Pérez',
                'telefono': '1122334455',
                'direccion': '',
                'notas': '',
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 1)
        insumo.refresh_from_db()
        self.assertEqual(insumo.cantidad_disponible, Decimal('2.000'))
        consumo = ConsumoInsumoPedido.objects.get(pedido=Pedido.objects.get())
        self.assertEqual(consumo.cantidad, Decimal('0.500'))
        self.assertFalse(consumo.reintegrado)

    def test_checkout_rechaza_receta_sin_insumos_suficientes(self):
        insumo = Insumo.objects.create(
            nombre='Harina insuficiente',
            unidad_medida='kg',
            cantidad_disponible=Decimal('0.400'),
            stock_minimo=Decimal('0.500'),
        )
        RecetaInsumo.objects.create(
            producto=self.producto,
            insumo=insumo,
            cantidad_por_unidad=Decimal('0.250'),
        )

        respuesta = self.client.post(
            reverse('cliente:checkout'),
            {
                'nombre_cliente': 'Juan Pérez',
                'telefono': '1122334455',
                'direccion': '',
                'notas': '',
            },
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Pedido.objects.count(), 0)
        self.assertTrue(respuesta.context['form'].non_field_errors())
        self.inventario.refresh_from_db()
        insumo.refresh_from_db()
        self.assertEqual(self.inventario.cantidad_disponible, 5)
        self.assertEqual(insumo.cantidad_disponible, Decimal('0.400'))

    def test_nuevo_pedido_usa_codigo_de_seguimiento_no_predecible(self):
        pedido = Pedido.objects.create(
            nombre_cliente='Cliente token',
            telefono='1100000000',
            direccion='Retiro en local',
            monto_total=Decimal('100.00'),
        )
        self.assertEqual(len(pedido.codigo_seguimiento), 32)
        self.assertTrue(all(caracter in '0123456789ABCDEF' for caracter in pedido.codigo_seguimiento))

    def test_seguimiento_publico_no_acepta_post(self):
        pedido = Pedido.objects.create(
            nombre_cliente='Cliente seguimiento',
            telefono='1100000001',
            direccion='Retiro en local',
            monto_total=Decimal('100.00'),
        )
        respuesta = self.client.post(
            reverse('cliente:api_seguimiento_pedido', kwargs={'codigo': pedido.codigo_seguimiento})
        )
        self.assertEqual(respuesta.status_code, 405)
