import json

from django.http import JsonResponse, request
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from cliente.models import Categoria, Pedido, Producto
from .models import ConfiguracionSistema
from django.db import transaction
from .forms import ProductoForm
from cliente.models import Inventario, Producto


def dashboard(request):
    pedidos = Pedido.objects.prefetch_related('detalles__producto').all()

    categorias = Categoria.objects.all()

    productos = Producto.objects.select_related('categoria').all()

    productos_data = [
        {
            'id': producto.id,
            'name': producto.nombre,
            'category': producto.categoria.slug,
            'category_id': producto.categoria_id,
            'price': float(producto.precio),
            'stock': producto.inventario.cantidad_disponible,
            'status': 'active' if producto.activo else 'inactive',
            'image': producto.imagen.url if producto.imagen else '',
        }
        for producto in productos
    ]

    pedidos_data = [
        {
            'id': f'#{pedido.codigo_seguimiento}',
            'codigo': pedido.codigo_seguimiento,
            'customer': pedido.nombre_cliente,
            'items': ', '.join(
                f'{detalle.cantidad}x {detalle.producto.nombre if detalle.producto else "Producto eliminado"}'
                for detalle in pedido.detalles.all()
            ) or 'Sin detalle',
            'total': float(pedido.monto_total),
            'status': pedido.estado.lower(),
            'time': pedido.creado_en.strftime('%d/%m/%Y %H:%M'),
        }
        for pedido in pedidos
    ]

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)

    return render(
        request,
        'administrador/index.html',
        {
            'pedidos_json': json.dumps(pedidos_data),
            'productos_data': productos_data,
            'costo_envio': configuracion.costo_envio,
            'categorias': categorias,
        }
    )


@require_POST
def actualizar_estado_pedido(request, codigo):
    """Actualiza el estado real del pedido desde el panel de administración."""
    pedido = get_object_or_404(Pedido, codigo_seguimiento__iexact=codigo.strip())

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse(
            {'status': 'error', 'mensaje': 'Solicitud inválida.'},
            status=400
        )

    nuevo_estado = data.get('estado')

    estados_validos = {valor for valor, _ in Pedido.ESTADOS}

    if nuevo_estado not in estados_validos:
        return JsonResponse(
            {'status': 'error', 'mensaje': 'Estado de pedido inválido.'},
            status=400
        )

    pedido.estado = nuevo_estado
    pedido.save(update_fields=['estado'])

    return JsonResponse({
        'status': 'ok',
        'codigo': pedido.codigo_seguimiento,
        'estado': pedido.estado,
        'estado_display': pedido.get_estado_display(),
    })


@require_POST
def actualizar_configuracion_envio(request):
    try:
        data = json.loads(request.body or '{}')
        costo = float(data.get('costo_envio', 800))
        if costo < 0:
            raise ValueError
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'status': 'error', 'mensaje': 'Costo de envío inválido.'}, status=400)

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
    configuracion.costo_envio = costo
    configuracion.save(update_fields=['costo_envio'])

    return JsonResponse({
        'status': 'ok',
        'costo_envio': float(configuracion.costo_envio),
    })

@require_POST
def crear_producto(request):
    form = ProductoForm(request.POST, request.FILES)

    if not form.is_valid():
        return JsonResponse({
            "status": "error",
            "details": form.errors.get_json_data()
        }, status=400)

    try:
        stock = int(request.POST.get("stock", 0))
        if stock < 0:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({
        "status": "error",
        "mensaje": "El stock debe ser un entero igual o mayor que cero."
    }, status=400)

    try:
        with transaction.atomic():
            producto = form.save()

            stock = int(request.POST.get("stock", 0))

            if stock < 0:
                return JsonResponse({
                    "status": "error",
                    "mensaje": "El stock no puede ser negativo."
                }, status=400)

            Inventario.objects.create(
                producto=producto,
                cantidad_disponible=stock
            )

    except (ValueError, TypeError):
        return JsonResponse({
            "status": "error",
            "mensaje": "El stock debe ser un número entero válido."
        }, status=400)

    return JsonResponse({
        "status": "ok",
        "producto": {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": float(producto.precio),
            "stock": stock
        }
    })

@require_POST
def editar_producto(request):
    producto_id = request.POST.get("id")

    try:
        producto_id = int(producto_id)
    except (TypeError, ValueError):
        return JsonResponse({
            "status": "error",
            "mensaje": "El identificador del producto no es valido"
        }, status=400)

    producto = get_object_or_404(Producto, pk=producto_id)

    stock = None

    if "stock" in request.POST:
        try:
            stock = int(request.POST.get("stock"))

            if stock < 0:
                raise ValueError

        except (TypeError, ValueError):
            return JsonResponse({
                "status": "error",
                "mensaje": "El stock debe ser un número entero igual o mayor que cero."
            }, status=400)

    form = ProductoForm(
        request.POST,
        request.FILES,
        instance=producto
    )

    if not form.is_valid():
        return JsonResponse({
            "status": "error",
            "details": form.errors.get_json_data()
        }, status=400)

    with transaction.atomic():
        producto = form.save()

        if stock is not None:
            inventario, creado = Inventario.objects.get_or_create(
                producto=producto,
                defaults={'cantidad_disponible': stock}
            )

            if not creado:
                inventario.cantidad_disponible = stock
                inventario.save(update_fields=['cantidad_disponible'])

    return JsonResponse({
        "status": "ok",
        "producto": {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": float(producto.precio),
            "stock": stock
            }
    })

@require_POST
def eliminar_producto(request):
    producto_id = request.POST.get("id")

    try:
        producto_id = int(producto_id)
    except (TypeError, ValueError):
        return JsonResponse({
            "status": "error",
            "mensaje": "El identificador del producto no es valido"
        }, status=400)

    producto = get_object_or_404(Producto, pk=producto_id)

    producto.delete()

    return JsonResponse({
        "status": "ok",
        "mensaje": f"Producto '{producto.nombre}' eliminado correctamente."
    })