import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from cliente.models import Categoria, Pedido, Producto, Inventario, Insumo
from .models import ConfiguracionSistema
from django.db import transaction
from .forms import ProductoForm
from .forms import ProductoForm, CategoriaForm
from django.db import transaction



def dashboard(request):
    pedidos = Pedido.objects.prefetch_related('detalles__producto').all()

    categorias = Categoria.objects.all()

    insumos = Insumo.objects.all()

    insumos_data = [
        {
            'id': insumo.id,
            'nombre': insumo.nombre,
            'unidad_medida': insumo.unidad_medida,
            'cantidad_disponible': float(insumo.cantidad_disponible),
            'stock_minimo': float(insumo.stock_minimo),
            'activo': insumo.activo,
        }
        for insumo in insumos
    ]

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
            'insumos_data': json.dumps(insumos_data),
        }
    )


@require_POST
def actualizar_estado_pedido(request, codigo):
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

    estado_anterior = pedido.estado

    if estado_anterior == nuevo_estado:
        return JsonResponse({
            'status':'ok',
            'codigo': pedido.codigo_seguimiento,
            'estado': pedido.estado,
            'estado_display': pedido.get_estado_display(),
        })

    with transaction.atomic():
        if nuevo_estado == 'CANCELADO' and estado_anterior != 'CANCELADO':
            for detalle in pedido.detalles.select_related('producto__inventario').all():
                if detalle.producto and hasattr(detalle.producto, 'inventario'):
                    inventario = detalle.producto.inventario
                    inventario.cantidad_disponible += detalle.cantidad
                    inventario.save()

        elif estado_anterior == 'CANCELADO' and nuevo_estado != 'CANCELADO':
            for detalle in pedido.detalles.select_related('producto__inventario').all():
                if detalle.producto and hasattr(detalle.producto, 'inventario'):
                    if detalle.producto.inventario.cantidad_disponible < detalle.cantidad:
                        return JsonResponse({
                            'status': 'error',
                            'mensaje': f'Stock insuficiente de "{detalle.producto.nombre}" para reabrir el pedido.'
                        }, status=400)

            for detalle in pedido.detalles.select_related('producto__inventario').all():
                if detalle.producto and hasattr(detalle.producto, 'inventario'):
                    inventario = detalle.producto.inventario
                    inventario.cantidad_disponible -= detalle.cantidad
                    inventario.save()

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

@require_POST
def crear_categoria(request):
    form = CategoriaForm(request.POST)

    if not form.is_valid():
        return JsonResponse({
            "status": "error",
            "details": form.errors.get_json_data()
        }, status=400)

    categoria = form.save()

    return JsonResponse({
        "status": "ok",
        "categoria": {
            "id": categoria.id,
            "nombre": categoria.nombre,
            "slug": categoria.slug
        }
    })

@require_POST
def editar_categoria(request):
    categoria_id = request.POST.get("id")

    try:
        categoria_id = int(categoria_id)
    except (TypeError, ValueError):
        return JsonResponse({
            "status": "error",
            "mensaje": "El identificador de la categoría no es válido."
        }, status=400)

    categoria = get_object_or_404(Categoria, pk=categoria_id)

    form = CategoriaForm(request.POST, instance=categoria)

    if not form.is_valid():
        return JsonResponse({
            "status": "error",
            "details": form.errors.get_json_data()
        }, status=400)

    categoria = form.save()

    return JsonResponse({
        "status": "ok",
        "categoria": {
            "id": categoria.id,
            "nombre": categoria.nombre,
            "slug": categoria.slug
        }
    })

@require_POST
def eliminar_categoria(request):
    categoria_id = request.POST.get("id")

    try:
        categoria_id = int(categoria_id)
    except (TypeError, ValueError):
        return JsonResponse({
            "status": "error",
            "mensaje": "El identificador de la categoría no es válido."
        }, status=400)

    categoria = get_object_or_404(Categoria, pk=categoria_id)

    if categoria.productos.exists():
        return JsonResponse({
            "status": "error",
            "mensaje": f"No se puede eliminar la categoría '{categoria.nombre}' porque tiene productos asociados."
        }, status=400)
    
    categoria.delete()

    return JsonResponse({
        "status": "ok",
        "mensaje": f"Categoría '{categoria.nombre}' eliminada correctamente."
    })

@require_POST
def actualizar_inventario(request):
    producto_id = request.POST.get("producto_id")

    try:
        producto_id = int(producto_id)
    except (TypeError, ValueError):
        return JsonResponse({
            "status": "error",
            "mensaje": "El identificador del producto no es válido."
        }, status=400)

    producto = get_object_or_404(Producto, pk=producto_id)

    inventario, _ = Inventario.objects.get_or_create(producto=producto)

    cantidad = request.POST.get("cantidad_disponible")
    stock_min = request.POST.get("stock_minimo")

    try:
        if cantidad is not None:
            cantidad_int = int(cantidad)
            if cantidad_int < 0:
                raise ValueError
            inventario.cantidad_disponible = cantidad_int

        if stock_min is not None:
            stock_min_int = int(stock_min)
            if stock_min_int < 0:
                raise ValueError
            inventario.stock_minimo = stock_min_int

        inventario.save()

    except (ValueError, TypeError):
        return JsonResponse({
            "status": "error",
            "mensaje": "Las cantidades de inventario deben ser numeros enteros mayores o iguales a cero."
        }, status=400)

    return JsonResponse({
        "status": "ok",
        "inventario": {
            "producto_id": producto.id,
            "producto_nombre": producto.nombre,
            "cantidad_disponible": inventario.cantidad_disponible,
            "stock_minimo": inventario.stock_minimo,
            "es_stock_bajo": inventario.es_stock_bajo
        }
    })