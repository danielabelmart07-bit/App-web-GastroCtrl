import json
from decimal import Decimal, InvalidOperation

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from cliente.models import Categoria, Pedido, Producto, Inventario, Cliente, Insumo, ConsumoInsumoPedido
from .models import ConfiguracionSistema
from django.db import transaction
from .forms import ProductoForm, CategoriaForm
from django.db.models import Q, Count, Sum
from django.utils.http import url_has_allowed_host_and_scheme
from administrador.utils import generar_datos_dashboard

@staff_member_required(login_url='administrador:login')
def dashboard(request):
    pedidos_qs = Pedido.objects.filter(archivado=False).prefetch_related('detalles__producto').all()
    pedidos_archivados = Pedido.objects.filter(archivado=True).prefetch_related('detalles__producto').order_by('-creado_en')

    estado_filtro = request.GET.get('estado', '').strip()
    estados_validos = {valor for valor, _ in Pedido.ESTADOS}
    if estado_filtro in estados_validos:
        pedidos_qs = pedidos_qs.filter(estado=estado_filtro)

    busqueda = request.GET.get('q', '').strip()
    if busqueda:
        pedidos_qs = pedidos_qs.filter(
            Q(nombre_cliente__icontains=busqueda) |
            Q(telefono__icontains=busqueda) |
            Q(codigo_seguimiento__icontains=busqueda)
        )

    pedidos = pedidos_qs.order_by('-id')

    datos_dashboard = generar_datos_dashboard()

    categorias = Categoria.objects.annotate(cantidad_productos=Count('productos'))
    categorias_data = [
        {
            'id': categoria.id,
            'name': categoria.nombre,
            'slug': categoria.slug,
            'count': categoria.cantidad_productos,
            'icon': 'fa-tag',
            'desc': 'Categoría de productos',
        }
        for categoria in categorias
    ]

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
            'stock': producto.inventario.cantidad_disponible if hasattr(producto, 'inventario') else 0,
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
            'type': pedido.get_modalidad_entrega_display(),
            'time': pedido.creado_en.strftime('%d/%m/%Y %H:%M'),
        }
        for pedido in pedidos
    ]

    pedidos_archivados_data = [
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
            'type': pedido.get_modalidad_entrega_display(),
            'time': pedido.creado_en.strftime('%d/%m/%Y %H:%M'),
        }
        for pedido in pedidos_archivados
    ]

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)

    return render(
        request,
        'administrador/index.html',
        {
            'pedidos': pedidos,
            'pedidos_data': pedidos_data,
            'pedidos_archivados_data': pedidos_archivados_data,
            'productos_data': productos_data,
            'costo_envio': configuracion.costo_envio,
            'categorias': categorias,
            'categorias_data': categorias_data,
            'insumos_data': insumos_data,
            'kpis': datos_dashboard['kpis'],
            'semana_labels': datos_dashboard['semana_labels'],
            'semana_data': datos_dashboard['semana_data'],
            'trend_data': datos_dashboard['trend_data'],
            'pie_data': datos_dashboard['pie_data'],
            'top_productos': datos_dashboard['top_productos'],
        }
    )


@require_POST
@staff_member_required(login_url='administrador:login')
def actualizar_estado_pedido(request, codigo):
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'mensaje': 'Solicitud inválida.'}, status=400)

    nuevo_estado = data.get('estado')
    estados_validos = {valor for valor, _ in Pedido.ESTADOS}
    if nuevo_estado not in estados_validos:
        return JsonResponse({'status': 'error', 'mensaje': 'Estado de pedido inválido.'}, status=400)

    with transaction.atomic():
        # Bloquear el pedido evita que dos cancelaciones concurrentes repongan
        # dos veces el mismo stock.
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            codigo_seguimiento__iexact=codigo.strip(),
        )
        estado_anterior = pedido.estado
        transiciones_permitidas = {
            'PENDIENTE': {'EN_PREPARACION', 'CANCELADO'},
            'EN_PREPARACION': {'LISTO', 'CANCELADO'},
            'LISTO': {'ENTREGADO', 'CANCELADO'},
            'ENTREGADO': set(),
            'CANCELADO': set(),
        }

        if nuevo_estado == estado_anterior:
            return JsonResponse({
                'status': 'ok', 'codigo': pedido.codigo_seguimiento,
                'estado': pedido.estado, 'estado_display': pedido.get_estado_display(),
            })

        if nuevo_estado not in transiciones_permitidas.get(estado_anterior, set()):
            return JsonResponse({
                'status': 'error',
                'mensaje': f'No se puede cambiar un pedido de {pedido.get_estado_display()} a {dict(Pedido.ESTADOS).get(nuevo_estado, nuevo_estado)}.',
            }, status=400)

        if nuevo_estado == 'CANCELADO':
            detalles = list(pedido.detalles.all())
            producto_ids = sorted({detalle.producto_id for detalle in detalles if detalle.producto_id})
            inventarios = {
                inventario.producto_id: inventario
                for inventario in Inventario.objects.select_for_update()
                .filter(producto_id__in=producto_ids)
                .order_by('producto_id')
            }
            for detalle in detalles:
                inventario = inventarios.get(detalle.producto_id)
                if inventario:
                    inventario.cantidad_disponible += detalle.cantidad
                    inventario.save(update_fields=['cantidad_disponible'])

            # Reintegrar materias primas registradas al confirmar el pedido.
            # La marca evita duplicar devoluciones si el flujo se reintenta.
            consumos = list(
                ConsumoInsumoPedido.objects.filter(
                    pedido=pedido,
                    reintegrado=False,
                ).order_by('insumo_id')
            )
            insumo_ids = [consumo.insumo_id for consumo in consumos]
            insumos = {
                insumo.id: insumo
                for insumo in Insumo.objects.select_for_update()
                .filter(id__in=insumo_ids)
                .order_by('id')
            }
            for consumo in consumos:
                insumo = insumos.get(consumo.insumo_id)
                if insumo:
                    insumo.cantidad_disponible += consumo.cantidad
                    insumo.save(update_fields=['cantidad_disponible'])
                    consumo.reintegrado = True
                    consumo.save(update_fields=['reintegrado'])

        pedido.estado = nuevo_estado
        pedido.save(update_fields=['estado'])

    return JsonResponse({
        'status': 'ok',
        'codigo': pedido.codigo_seguimiento,
        'estado': pedido.estado,
        'estado_display': pedido.get_estado_display(),
    })

@require_POST
@staff_member_required(login_url='administrador:login')
def archivar_pedido(request, codigo):
    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'mensaje': 'Solicitud inválida.'}, status=400)

    archivado = data.get('archivado', True)
    if not isinstance(archivado, bool):
        return JsonResponse({'status': 'error', 'mensaje': 'La acción de archivado no es válida.'}, status=400)

    with transaction.atomic():
        pedido = get_object_or_404(
            Pedido.objects.select_for_update(),
            codigo_seguimiento__iexact=codigo.strip(),
        )
        if archivado and pedido.estado not in {'ENTREGADO', 'CANCELADO'}:
            return JsonResponse({
                'status': 'error',
                'mensaje': 'Solo se pueden archivar pedidos entregados o cancelados.',
            }, status=400)

        pedido.archivado = archivado
        pedido.save(update_fields=['archivado'])

    return JsonResponse({
        'status': 'ok',
        'codigo': pedido.codigo_seguimiento,
        'archivado': pedido.archivado,
        'mensaje': 'Pedido archivado.' if archivado else 'Pedido restaurado al listado activo.',
    })


@require_POST
@staff_member_required(login_url='administrador:login')
def actualizar_configuracion_envio(request):
    try:
        data = json.loads(request.body or '{}')
        costo = Decimal(str(data.get('costo_envio', '800')))
        if (
            not costo.is_finite()
            or costo < 0
            or costo.as_tuple().exponent < -2
            or costo > Decimal('99999999.99')
        ):
            raise ValueError
    except (json.JSONDecodeError, TypeError, ValueError, InvalidOperation):
        return JsonResponse({'status': 'error', 'mensaje': 'Costo de envío inválido.'}, status=400)

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
    configuracion.costo_envio = costo
    configuracion.save(update_fields=['costo_envio'])

    return JsonResponse({'status': 'ok', 'costo_envio': float(configuracion.costo_envio)})

@require_POST
@staff_member_required(login_url='administrador:login')
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
@staff_member_required(login_url='administrador:login')
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
@staff_member_required(login_url='administrador:login')
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
@staff_member_required(login_url='administrador:login')
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
@staff_member_required(login_url='administrador:login')
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
@staff_member_required(login_url='administrador:login')
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
@staff_member_required(login_url='administrador:login')
def actualizar_inventario(request):
    producto_id = request.POST.get('producto_id')
    try:
        producto_id = int(producto_id)
    except (TypeError, ValueError):
        return JsonResponse({'status': 'error', 'mensaje': 'El identificador del producto no es válido.'}, status=400)

    producto = get_object_or_404(Producto, pk=producto_id)
    cantidad_raw = request.POST.get('cantidad_disponible')
    stock_min_raw = request.POST.get('stock_minimo')
    cantidad_int = None
    stock_min_int = None

    # Validar todo antes de crear o modificar la fila de inventario.
    try:
        if cantidad_raw is not None:
            cantidad_int = int(cantidad_raw)
            if cantidad_int < 0:
                raise ValueError
        if stock_min_raw is not None:
            stock_min_int = int(stock_min_raw)
            if stock_min_int < 0:
                raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({
            'status': 'error',
            'mensaje': 'Las cantidades de inventario deben ser números enteros mayores o iguales a cero.'
        }, status=400)

    inventario, _ = Inventario.objects.get_or_create(producto=producto)
    if cantidad_int is not None:
        inventario.cantidad_disponible = cantidad_int
    if stock_min_int is not None:
        inventario.stock_minimo = stock_min_int
    inventario.save()

    return JsonResponse({
        'status': 'ok',
        'inventario': {
            'producto_id': producto.id,
            'producto_nombre': producto.nombre,
            'cantidad_disponible': inventario.cantidad_disponible,
            'stock_minimo': inventario.stock_minimo,
            'es_stock_bajo': inventario.es_stock_bajo
        }
    })

@require_POST
@staff_member_required(login_url='administrador:login')
def reponer_insumo(request):
    insumo_id = request.POST.get('insumo_id')
    cantidad_raw = request.POST.get('cantidad_reponer', '')

    try:
        insumo_id = int(insumo_id)
        cantidad = Decimal(cantidad_raw)
        if (
            not cantidad.is_finite()
            or cantidad <= 0
            or cantidad.as_tuple().exponent < -3
            or cantidad > Decimal('9999999.999')
        ):
            raise ValueError
    except (TypeError, ValueError, InvalidOperation):
        return JsonResponse({
            'status': 'error',
            'mensaje': 'Ingresá una cantidad de reposición válida y mayor que cero.'
        }, status=400)

    with transaction.atomic():
        insumo = get_object_or_404(Insumo.objects.select_for_update(), pk=insumo_id)
        nueva_cantidad = insumo.cantidad_disponible + cantidad
        if nueva_cantidad > Decimal('9999999.999'):
            return JsonResponse({
                'status': 'error',
                'mensaje': 'La cantidad resultante supera el máximo permitido.'
            }, status=400)
        insumo.cantidad_disponible = nueva_cantidad
        insumo.save(update_fields=['cantidad_disponible'])

    return JsonResponse({
        'status': 'ok',
        'insumo': {
            'id': insumo.id,
            'nombre': insumo.nombre,
            'cantidad_disponible': float(insumo.cantidad_disponible),
            'unidad_medida': insumo.unidad_medida,
            'stock_minimo': float(insumo.stock_minimo),
            'stock_bajo': insumo.cantidad_disponible <= insumo.stock_minimo,
        }
    })


@staff_member_required(login_url='administrador:login')
def listar_clientes(request):
    busqueda = request.GET.get('q', '').strip()
    clientes_qs = Cliente.objects.annotate(
        total_pedidos_db=Count('pedidos', distinct=True),
        total_gastado_db=Sum('pedidos__monto_total', filter=Q(pedidos__estado='ENTREGADO')),
    )

    if busqueda:
        clientes_qs = clientes_qs.filter(
            Q(nombre__icontains=busqueda) |
            Q(telefono__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    clientes_data = [
        {
            'id': c.id,
            'nombre': c.nombre,
            'telefono': c.telefono,
            'direccion_habitual': c.direccion_habitual,
            'email': c.email or '',
            'total_pedidos': c.total_pedidos_db,
            'total_gastado': float(c.total_gastado_db or 0),
            'fecha_registro': c.fecha_registro.strftime('%Y-%m-%d %H:%M')
        }
        for c in clientes_qs
    ]

    return JsonResponse({'status': 'ok', 'clientes': clientes_data})


@staff_member_required(login_url='administrador:login')
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    pedidos = cliente.pedidos.all().order_by('-id')

    pedidos_data = [
        {
            'id': p.id,
            'codigo': p.codigo_seguimiento,
            'estado': p.estado,
            'estado_display': p.get_estado_display(),
            'monto_total': float(p.monto_total),
            'fecha': p.creado_en.strftime('%Y-%m-%d %H:%M')
        }
        for p in pedidos
    ]

    return JsonResponse({
        'status': 'ok',
        'cliente': {
            'id': cliente.id,
            'nombre': cliente.nombre,
            'telefono': cliente.telefono,
            'direccion_habitual': cliente.direccion_habitual,
            'email': cliente.email or '',
            'notas': cliente.notas or '',
            'total_pedidos': cliente.total_pedidos,
            'total_gastado': float(cliente.total_gastado),
            'pedidos': pedidos_data
        }
    })

def login_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('administrador:dashboard')

    error_message = None
    if request.method == 'POST':
        usuario = request.POST.get('username', '').strip()
        clave = request.POST.get('password', '')

        user = authenticate(request, username=usuario, password=clave)
        if user is not None and user.is_active and user.is_staff:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next', '')
            if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
                next_url = ''
            return redirect(next_url or 'administrador:dashboard')
        else:
            error_message = "Usuario o contraseña incorrectos."

    return render(request, 'administrador/login.html', {'error': error_message})


@staff_member_required(login_url='administrador:login')
@require_POST
def logout_view(request):
    logout(request)
    return redirect('administrador:login')