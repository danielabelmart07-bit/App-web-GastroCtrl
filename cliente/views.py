from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction
from .models import Categoria, Producto, Pedido, DetallePedido
from .carrito import Carrito
from .forms import PedidoForm

def checkout(request):
    """Valida el carrito, crea el pedido y descuenta el stock de forma atómica."""
    carrito = Carrito(request)

    if len(carrito.carrito) == 0:
        return redirect('cliente:menu')

    if request.method == 'POST':
        form = PedidoForm(request.POST)

        if form.is_valid():
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
                    {'form': form, 'carrito': carrito}
                )

            with transaction.atomic():
                pedido = form.save(commit=False)
                pedido.monto_total = total
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
        {'form': form, 'carrito': carrito}
    )

def consultar_estado_pedido_api(request, codigo):
    """Endpoint AJAX que consulta el estado del pedido para la pestaña 'Seguir pedido' del drawer."""
    try:
        pedido = Pedido.objects.get(codigo_seguimiento__iexact=codigo.strip())
        detalles = [
            {'producto': d.producto.nombre if d.producto else 'Producto', 'cantidad': d.cantidad}
            for d in pedido.detalles.all()
        ]
        return JsonResponse({
            'status': 'ok',
            'codigo': pedido.codigo_seguimiento,
            'estado': pedido.get_estado_display(),
            'monto_total': float(pedido.monto_total),
            'detalles': detalles
        })
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

    return JsonResponse({
        'status': 'ok',
        'items': items,
        'total_unidades': carrito.obtener_total_unidades(),
        'precio_total': float(carrito.obtener_precio_total()),
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