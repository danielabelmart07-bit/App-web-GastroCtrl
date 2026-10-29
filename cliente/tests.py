from django.test import TestCase
from decimal import Decimal
from django.test import TestCase
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpRequest
from .models import Categoria, Producto, Cliente
from .carrito import Carrito
from django.urls import reverse
from .models import Inventario, Pedido, DetallePedido


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
        from django.contrib.auth.models import User
        usuario = User.objects.create_user(username="cliente_checkout", password="ClaveSegura2026")
        Cliente.objects.create(user=usuario, nombre="Cliente Checkout", telefono="1199001122")
        self.client.force_login(usuario)

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

    def test_checkout_sin_sesion_redirige_a_registro(self):
        self.client.logout()
        session = self.client.session
        session["carrito"] = {str(self.producto.id): {"producto_id": self.producto.id, "nombre": self.producto.nombre, "precio": str(self.producto.precio), "cantidad": 1, "imagen": ""}}
        session.save()
        respuesta = self.client.get(reverse("cliente:checkout"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("cliente:registro"), respuesta.url)
        self.assertIn("next=", respuesta.url)

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

class CuentaClienteTests(TestCase):
    def test_registro_crea_usuario_y_perfil_relacionado(self):
        response = self.client.post(reverse("cliente:registro"), {
            "username": "cliente_nuevo",
            "email": "cliente@example.com",
            "nombre": "Cliente Nuevo",
            "telefono": "1133445566",
            "direccion_habitual": "Calle 123",
            "ciudad": "Hurlingham",
            "password1": "UnaClaveSegura2026!",
            "password2": "UnaClaveSegura2026!",
        })
        self.assertRedirects(response, reverse("cliente:home"))
        from django.contrib.auth.models import User
        usuario = User.objects.get(username="cliente_nuevo")
        self.assertEqual(usuario.perfil_cliente.nombre, "Cliente Nuevo")
        self.assertEqual(usuario.perfil_cliente.telefono, "1133445566")
        self.assertEqual(usuario.perfil_cliente.ciudad, "Hurlingham")

    def test_perfil_requiere_autenticacion(self):
        response = self.client.get(reverse("cliente:perfil"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("cliente:login"), response.url)

    def test_cliente_puede_iniciar_sesion_y_ver_perfil(self):
        from django.contrib.auth.models import User
        from .models import Cliente
        usuario = User.objects.create_user(username="cliente_existente", password="UnaClaveSegura2026!")
        Cliente.objects.create(user=usuario, nombre="Cliente Existente", telefono="1198765432")
        response = self.client.post(reverse("cliente:login"), {
            "username": "cliente_existente",
            "password": "UnaClaveSegura2026!",
            "next": reverse("cliente:checkout"),
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("cliente:checkout"))
        self.assertEqual(self.client.get(reverse("cliente:perfil")).status_code, 200)
