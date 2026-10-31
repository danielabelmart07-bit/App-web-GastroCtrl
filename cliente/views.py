from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlencode
import json
from django.db.models import Q
from django.db import transaction
from .models import Categoria, Producto, Pedido, DetallePedido, Cliente
from administrador.models import ConfiguracionSistema
from .carrito import Carrito
from .forms import PedidoForm, RegistroClienteForm, PerfilClienteForm

def checkout(request):
    carrito = Carrito(request)

    if len(carrito.carrito) == 0:
        return redirect('cliente:menu')

    if not request.user.is_authenticated:
        destino = reverse('cliente:checkout')
        return redirect(f"{reverse('cliente:registro')}?{urlencode({'next': destino})}")

    cliente_actual = Cliente.objects.filter(user=request.user).first()
    if cliente_actual is None:
        messages.info(request, "Para finalizar una compra necesitás ingresar con una cuenta de cliente.")
        return redirect('cliente:home')

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
    modalidad = carrito.obtener_modalidad_entrega()
    costo_envio = configuracion.costo_envio if modalidad == 'DELIVERY' else 0
    subtotal = carrito.obtener_precio_total()
    total = subtotal + costo_envio

    if request.method == 'POST':
        form = PedidoForm(request.POST)

        if form.is_valid():
            if modalidad == 'DELIVERY' and not form.cleaned_data.get('direccion'):
                form.add_error('direccion', 'Ingresá una dirección para recibir el pedido.')
                return render(
                    request,
                    'cliente/checkout.html',
                    {
                        'form': form,
                        'carrito': carrito,
                        'subtotal': subtotal,
                        'costo_envio': costo_envio,
                        'total': total,
                        'modalidad_entrega': modalidad,
                    }
                )

            productos_pedido = []
            total = 0

            for item in carrito:
                producto = get_object_or_404(
                    Producto,
                    id=item['producto_id'],
                    activo=True
                )

                cantidad = item['cantidad']

                try:
                    inventario = producto.inventario
                except Producto.inventario.RelatedObjectDoesNotExist:
                    form.add_error(
                        None,
                        f'El producto "{producto.nombre}" no tiene inventario registrado.'
                    )
                    continue

                if cantidad > inventario.cantidad_disponible:
                    form.add_error(
                        None,
                        f'No hay stock suficiente de "{producto.nombre}". '
                        f'Disponibles: {inventario.cantidad_disponible}.'
                    )
                    continue

                productos_pedido.append((producto, cantidad))
                total += producto.precio * cantidad

            if form.errors:
                return render(
                    request,
                    'cliente/checkout.html',
                    {
                        'form': form,
                        'carrito': carrito,
                        'subtotal': subtotal,
                        'costo_envio': costo_envio,
                        'total': subtotal + costo_envio,
                        'modalidad_entrega': modalidad,
                    }
                )

            with transaction.atomic():
                configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)

                stock_insuficiente = False

                for producto, cantidad in productos_pedido:
                    inventario = producto.inventario
                    inventario.refresh_from_db()

                    if cantidad > inventario.cantidad_disponible:
                        form.add_error(
                            None,
                            f'El stock de "{producto.nombre}" cambió. '
                            f'Disponibles: {inventario.cantidad_disponible}.'
                        )
                        stock_insuficiente = True

                if stock_insuficiente:
                    return render(
                        request,
                        'cliente/checkout.html',
                        {
                            'form': form,
                            'carrito': carrito,
                            'subtotal': subtotal,
                            'costo_envio': costo_envio,
                            'total': subtotal + costo_envio,
                            'modalidad_entrega': modalidad,
                        }
                    )

                modalidad = carrito.obtener_modalidad_entrega()
                costo_envio = configuracion.costo_envio if modalidad == 'DELIVERY' else 0

                pedido = form.save(commit=False)
                pedido.cliente = cliente_actual
                if modalidad == 'RETIRO':
                    pedido.direccion = 'Retiro en local'
                pedido.monto_total = total + costo_envio
                pedido.modalidad_entrega = modalidad
                pedido.costo_envio = costo_envio
                pedido.save()

                for producto, cantidad in productos_pedido:
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio
                    )

                    inventario = producto.inventario
                    inventario.cantidad_disponible -= cantidad
                    inventario.save(update_fields=['cantidad_disponible'])

                carrito.limpiar()

            return render(
                request,
                'cliente/pedido_confirmado.html',
                {
                    'pedido': pedido,
                    'subtotal': pedido.monto_total - pedido.costo_envio,
                }
            )
    else:
        form = PedidoForm()

    return render(
        request,
        'cliente/checkout.html',
        {
            'form': form,
            'carrito': carrito,
            'subtotal': subtotal,
            'costo_envio': costo_envio,
            'total': total,
            'modalidad_entrega': modalidad,
        }
    )

def consultar_estado_pedido_api(request, codigo):
    """Endpoint AJAX que consulta el estado del pedido para la pestaña 'Seguir pedido' del drawer."""
    try:
        pedido = Pedido.objects.get(codigo_seguimiento__iexact=codigo.strip())
        detalles = [
            {'producto': d.producto.nombre if d.producto else 'Producto', 'cantidad': d.cantidad, 'subtotal': float(d.subtotal())}
            for d in pedido.detalles.all()
        ]
        response = JsonResponse({
            'status': 'ok',
            'codigo': pedido.codigo_seguimiento,
            'estado': pedido.get_estado_display(),
            'modalidad_entrega': pedido.get_modalidad_entrega_display(),
            'costo_envio': float(pedido.costo_envio),
            'subtotal': float(pedido.monto_total - pedido.costo_envio),
            'monto_total': float(pedido.monto_total),
            'detalles': detalles
        })
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        return response
    except Pedido.DoesNotExist:
        return JsonResponse({'status': 'error', 'mensaje': 'Código de pedido no encontrado.'}, status=404)

def agregar_al_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = Carrito(request)
        producto = get_object_or_404(Producto, id=producto_id, activo=True)
        carrito.agregar(producto=producto)
        
        return JsonResponse({
            'status': 'ok',
            'mensaje': f'{producto.nombre} agregado al carrito.',
            'total_unidades': carrito.obtener_total_unidades(),
            'precio_total': float(carrito.obtener_precio_total())
        })
    return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'}, status=405)


def restar_del_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = Carrito(request)
        producto = get_object_or_404(Producto, id=producto_id)
        carrito.restar(producto=producto)
        
        return JsonResponse({
            'status': 'ok',
            'total_unidades': carrito.obtener_total_unidades(),
            'precio_total': float(carrito.obtener_precio_total())
        })
    return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'}, status=405)


def eliminar_del_carrito(request, producto_id):
    if request.method == 'POST':
        carrito = Carrito(request)
        producto = get_object_or_404(Producto, id=producto_id)
        carrito.eliminar(producto=producto)
        
        return JsonResponse({
            'status': 'ok',
            'total_unidades': carrito.obtener_total_unidades(),
            'precio_total': float(carrito.obtener_precio_total())
        })
    return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'}, status=405)


def ver_carrito(request):
    carrito = Carrito(request)
    return render(request, 'cliente/carrito_detalle.html', {'carrito': carrito})

def estado_carrito_api(request):
    carrito = Carrito(request)

    items = []

    for item in carrito:
        items.append({
            'producto_id': item['producto_id'],
            'nombre': item['nombre'],
            'precio': float(item['precio_decimal']),
            'cantidad': item['cantidad'],
            'imagen': item['imagen'],
            'subtotal': float(item['subtotal']),
        })

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
    modalidad = carrito.obtener_modalidad_entrega()
    subtotal = carrito.obtener_precio_total()
    envio = configuracion.costo_envio if modalidad == 'DELIVERY' else 0

    return JsonResponse({
        'status': 'ok',
        'items': items,
        'total_unidades': carrito.obtener_total_unidades(),
        'modalidad': modalidad,
        'subtotal': float(subtotal),
        'envio': float(envio),
        'precio_total': float(subtotal + envio),
    })

def home(request):
    productos_destacados = Producto.objects.filter(
        activo=True,
        es_destacado=True
    ).select_related('categoria')

    return render(request, 'cliente/index.html', {
        'productos_destacados': productos_destacados,
    })

def menu(request):
    # 1. Obtener parámetros de búsqueda o filtrado de la URL (ej. ?q=cafe&categoria=panaderia)
    query = request.GET.get('q', '').strip()
    categoria_slug = request.GET.get('categoria', '')

    # 2. Consultar solo productos que estén marcados como activos
    # Usamos select_related para optimizar la consulta trayendo la categoría asociada
    productos = Producto.objects.filter(activo=True).select_related('categoria')

    # 3. Aplicar filtro por categoría si se seleccionó una
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)

    # 4. Aplicar filtro de búsqueda por texto en nombre o descripción
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )

    # Comprobar explícitamente si la búsqueda devolvió resultados.
    hay_resultados = productos.exists()

    # 5. Obtener todas las categorías para pintar la barra de filtros
    categorias = Categoria.objects.all()

    contexto = {
        'hay_resultados': hay_resultados,
        'productos': productos,
        'categorias': categorias,
        'query_actual': query,
        'categoria_actual': categoria_slug,
    }

    return render(request, 'cliente/menu.html', contexto)

def actualizar_modalidad_carrito(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido.'}, status=405)

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'mensaje': 'Solicitud inválida.'}, status=400)

    modalidad = data.get('modalidad')
    if modalidad not in ('RETIRO', 'DELIVERY'):
        return JsonResponse({'status': 'error', 'mensaje': 'Modalidad inválida.'}, status=400)

    carrito = Carrito(request)
    carrito.establecer_modalidad_entrega(modalidad)

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
    subtotal = carrito.obtener_precio_total()
    envio = configuracion.costo_envio if modalidad == 'DELIVERY' else 0

    return JsonResponse({
        'status': 'ok',
        'modalidad': modalidad,
        'subtotal': float(subtotal),
        'envio': float(envio),
        'total': float(subtotal + envio),
    })



def _destino_interno(request, destino):
    if destino and url_has_allowed_host_and_scheme(destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return destino
    return ""


def registro_cliente(request):
    if request.user.is_authenticated:
        if Cliente.objects.filter(user=request.user).exists():
            return redirect("cliente:perfil")
        messages.info(request, "Ya hay una sesión administrativa activa. Cerrala desde el panel antes de crear una cuenta de cliente.")
        return redirect("cliente:home")
    destino = _destino_interno(request, request.POST.get("next") or request.GET.get("next", ""))
    form = RegistroClienteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            user = form.save()
            Cliente.objects.create(
                user=user,
                nombre=form.cleaned_data["nombre"].strip(),
                telefono=form.cleaned_data["telefono"],
                direccion_habitual=form.cleaned_data.get("direccion_habitual", "").strip(),
                ciudad=form.cleaned_data.get("ciudad", "").strip(),
                email=user.email or None,
            )
        messages.success(request, "Tu cuenta fue creada. Ya podés iniciar sesión.")
        return redirect("cliente:home")
    return render(request, "cliente/registro.html", {"form": form, "next": destino})


def login_cliente(request):
    if request.user.is_authenticated:
        if Cliente.objects.filter(user=request.user).exists():
            return redirect("cliente:perfil")
        messages.info(request, "Ya hay una sesión administrativa activa. Cerrala desde el panel antes de ingresar como cliente.")
        return redirect("cliente:home")
    destino = _destino_interno(request, request.POST.get("next") or request.GET.get("next", ""))
    form = AuthenticationForm(request, data=request.POST or None)
    for name, field in form.fields.items():
        field.widget.attrs.update({"class": "w-full rounded-xl border border-cream-300 px-4 py-3 focus:border-coffee-500 focus:outline-none", "autocomplete": "username" if name == "username" else "current-password"})
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        if not Cliente.objects.filter(user=user).exists():
            form.add_error(None, "Esta cuenta no tiene un perfil de cliente asociado.")
        else:
            login(request, user)
            messages.success(request, "Iniciaste sesión correctamente.")
            return redirect(destino or "cliente:perfil")
    return render(request, "cliente/login.html", {"form": form, "next": destino})


@login_required(login_url="cliente:login")
def perfil_cliente(request):
    cliente = Cliente.objects.filter(user=request.user).first()
    if cliente is None:
        messages.info(request, "No hay un perfil de cliente asociado a esta cuenta.")
        return redirect("cliente:home")
    form = PerfilClienteForm(request.POST or None, instance=cliente)
    if request.method == "POST" and form.is_valid():
        cliente = form.save()
        request.user.email = cliente.email or ""
        request.user.save(update_fields=["email"])
        messages.success(request, "Tus datos fueron actualizados.")
        return redirect("cliente:perfil")
    return render(request, "cliente/perfil.html", {"form": form, "cliente": cliente})


@require_POST
def logout_cliente(request):
    if request.user.is_authenticated and Cliente.objects.filter(user=request.user).exists():
        logout(request)
        messages.info(request, "Cerraste sesión correctamente.")
    return redirect("cliente:home")
