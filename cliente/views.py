from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from django.db.models import Q
from django.db import transaction
from .models import Categoria, Producto, Pedido, DetallePedido
from administrador.models import ConfiguracionSistema
from .carrito import Carrito
from .forms import PedidoForm

def checkout(request):
    """Valida el carrito, crea el pedido y descuenta el stock de forma atómica."""
    carrito = Carrito(request)

    if len(carrito.carrito) == 0:
        return redirect('cliente:menu')

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

                if hasattr(producto, 'inventario') and cantidad > producto.inventario.cantidad_disponible:
                    form.add_error(
                        None,
                        f'No hay stock suficiente de "{producto.nombre}". '
                        f'Disponibles: {producto.inventario.cantidad_disponible}.'
                    )

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
                        'total': total,
                        'modalidad_entrega': modalidad,
                    }
                )

            with transaction.atomic():
                configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
                modalidad = carrito.obtener_modalidad_entrega()
                costo_envio = configuracion.costo_envio if modalidad == 'DELIVERY' else 0

                pedido = form.save(commit=False)
                if modalidad == 'RETIRO':
                    pedido.direccion = 'Retiro en el local'
                pedido.monto_total = total + costo_envio
                pedido.modalidad_entrega = modalidad
                pedido.costo_envio = costo_envio
                pedido.save()

                for producto, cantidad in productos_pedido:
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        precio_unitario=producto.precio,
                        cantidad=cantidad
                    )

                    if hasattr(producto, 'inventario'):
                        producto.inventario.cantidad_disponible -= cantidad
                        producto.inventario.save(update_fields=['cantidad_disponible'])

                carrito.limpiar()
            request.session.pop('modalidad_entrega', None)

            return render(
                request,
                'cliente/pedido_confirmado.html',
                {'pedido': pedido}
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
    """
    Vista AJAX para agregar productos al carrito.
    """
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
    """
    Vista AJAX para reducir la cantidad de un producto.
    """
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
    """
    Vista AJAX para eliminar un producto del carrito.
    """
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
    """
    Vista para renderizar la página dedicada al resumen del carrito de compras.
    """
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
    """
    Vista pública del catálogo que consulta productos y categorías
    desde la base de datos y permite filtrar por búsqueda o categoría.
    """
    # 1. Obtener parámetros de búsqueda o filtrado de la URL (ej. ?q=cafe&categoria=panaderia)
    query = request.GET.get('q', '')
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

    # 5. Obtener todas las categorías para pintar la barra de filtros
    categorias = Categoria.objects.all()

    contexto = {
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
