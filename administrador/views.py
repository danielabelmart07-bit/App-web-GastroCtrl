import json
from functools import wraps

from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST, require_http_methods
from cliente.models import Categoria, Pedido, Producto, Inventario, Cliente, Insumo
from .models import BitacoraAccion, ConfiguracionSistema, PerfilAdministrador
from django.db import transaction
from .forms import ProductoForm, CategoriaForm, PerfilAdministradorForm
from django.db import transaction
from django.db.models import Count, Q
from django.db.models import Sum
from django.utils import timezone
from administrador.utils import generar_datos_dashboard



def registrar_accion(request, accion, detalles=""):
    """Guarda una acción operativa realizada por un administrador autenticado."""
    BitacoraAccion.objects.create(
        usuario=request.user,
        accion=accion,
        detalles=detalles,
    )


def admin_required(view_func):
    """Limita las vistas de gestión a usuarios autenticados con permiso de staff."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.path.startswith('/gestion/api/'):
                return JsonResponse({'status': 'error', 'mensaje': 'Debés iniciar sesión.'}, status=401)
            return redirect(f"{reverse('administrador:login')}?next={request.get_full_path()}")
        if not request.user.is_staff:
            if request.path.startswith('/gestion/api/'):
                return JsonResponse({'status': 'error', 'mensaje': 'No tenés permisos para esta operación.'}, status=403)
            return HttpResponseForbidden('No tenés permisos para acceder al panel administrativo.')
        return view_func(request, *args, **kwargs)
    return _wrapped

@admin_required
def dashboard(request):
    pedidos_qs = Pedido.objects.prefetch_related('detalles__producto').filter(archivado=False)

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
    pedidos_archivados = Pedido.objects.prefetch_related('detalles__producto').filter(archivado=True).order_by('-id')

    datos_dashboard = generar_datos_dashboard()

    # Métricas del día actual según la zona horaria de Argentina.
    hoy = timezone.localdate()

    pedidos_hoy = Pedido.objects.filter(
        creado_en__date=hoy
    ).exclude(estado="CANCELADO")

    ventas_hoy = pedidos_hoy.aggregate(
        total=Sum("monto_total")
    )["total"] or 0

    cantidad_pedidos_hoy = pedidos_hoy.count()

    unidades_hoy = pedidos_hoy.aggregate(
        total=Sum("detalles__cantidad")
    )["total"] or 0

    categorias = Categoria.objects.annotate(total_productos=Count('productos')).order_by('nombre')
    categorias_data = [
        {
            'id': categoria.id,
            'name': categoria.nombre,
            'slug': categoria.slug,
            'count': categoria.total_productos,
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

    productos = Producto.objects.select_related('categoria', 'inventario').all()

    productos_data = [
        {
            'id': producto.id,
            'name': producto.nombre,
            'category': producto.categoria.slug,
            'category_id': producto.categoria_id,
            'price': float(producto.precio),
            'stock': producto.inventario.cantidad_disponible if getattr(producto, 'inventario', None) else 0,
            'status': 'active' if producto.activo else 'inactive',
            'es_destacado': producto.es_destacado,
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
            'time': pedido.creado_en.strftime('%d/%m/%Y %H:%M'),
        }
        for pedido in pedidos_archivados
    ]

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
    perfil_admin, _ = PerfilAdministrador.objects.get_or_create(usuario=request.user)

    return render(
        request,
        'administrador/index.html',
        {
            'pedidos': pedidos,
            'pedidos_json': json.dumps(pedidos_data),
            'pedidos_archivados_json': json.dumps(pedidos_archivados_data),
            'ventas_hoy': ventas_hoy,
            'cantidad_pedidos_hoy': cantidad_pedidos_hoy,
            'unidades_hoy': unidades_hoy,
            'productos_data_json': json.dumps(productos_data, ensure_ascii=False),
            'costo_envio': configuracion.costo_envio,
            'perfil_admin': perfil_admin,
            'categorias': categorias,
            'categorias_data_json': json.dumps(categorias_data, ensure_ascii=False),
            'ingresos_mes': datos_dashboard['kpis']['ingresos_mes'],
            'ticket_promedio': datos_dashboard['kpis']['ticket_promedio'],
            'cantidad_pedidos': datos_dashboard['kpis']['cantidad_pedidos'],
            'producto_estrella': datos_dashboard['top_productos'][0] if datos_dashboard['top_productos'] else None,
            'insumos_data': json.dumps(insumos_data),
            'kpis': datos_dashboard['kpis'],
            'semana_labels_json': json.dumps(datos_dashboard['semana_labels']),
            'semana_data_json': json.dumps(datos_dashboard['semana_data']),
            'trend_data_json': json.dumps(datos_dashboard['trend_data']),
            'pie_data_json': json.dumps(datos_dashboard['pie_data']),
            'top_productos': datos_dashboard['top_productos'],
        }
    )


@require_POST
@admin_required
def archivar_pedido(request, codigo):
    pedido = get_object_or_404(Pedido, codigo_seguimiento__iexact=codigo.strip())
    if pedido.archivado:
        return JsonResponse({'status': 'ok', 'mensaje': 'El pedido ya estaba archivado.'})
    if pedido.estado not in ('ENTREGADO', 'CANCELADO'):
        return JsonResponse({
            'status': 'error',
            'mensaje': 'Solo se pueden archivar pedidos entregados o cancelados.'
        }, status=400)
    pedido.archivado = True
    pedido.save(update_fields=['archivado'])
    registrar_accion(request, "Archivo de pedido", pedido.codigo_seguimiento)
    return JsonResponse({'status': 'ok', 'mensaje': 'Pedido archivado. La venta y sus detalles se conservaron.'})


@require_POST
@admin_required
def restaurar_pedido(request, codigo):
    pedido = get_object_or_404(Pedido, codigo_seguimiento__iexact=codigo.strip())
    if not pedido.archivado:
        return JsonResponse({'status': 'ok', 'mensaje': 'El pedido ya está en la gestión activa.'})
    pedido.archivado = False
    pedido.save(update_fields=['archivado'])
    registrar_accion(request, "Restauración de pedido", pedido.codigo_seguimiento)
    return JsonResponse({'status': 'ok', 'mensaje': 'Pedido restaurado a la gestión activa.'})


@require_POST
@admin_required
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

    registrar_accion(
        request,
        "Cambio de estado de pedido",
        f"{pedido.codigo_seguimiento}: {estado_anterior} → {nuevo_estado}",
    )

    return JsonResponse({
        'status': 'ok',
        'codigo': pedido.codigo_seguimiento,
        'estado': pedido.estado,
        'estado_display': pedido.get_estado_display(),
    })


@require_POST
@admin_required
def actualizar_perfil_admin(request):
    perfil, _ = PerfilAdministrador.objects.get_or_create(usuario=request.user)
    form = PerfilAdministradorForm(request.POST, request.FILES, instance=perfil)
    if form.is_valid():
        form.save()
        messages.success(request, "Tu foto de perfil se guardó correctamente.")
    else:
        error = next(iter(form.errors.values()), ["No se pudo guardar la imagen."])[0]
        messages.error(request, error)
    return redirect(f"{reverse('administrador:dashboard')}?tab=settings")


@require_POST
@admin_required
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
@admin_required
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

        registrar_accion(request, "Creación de producto", producto.nombre)

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
@admin_required
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

    registrar_accion(request, "Edición de producto", producto.nombre)

    return JsonResponse({
        "status": "ok",
        "producto": {
            "id": producto.id,
            "nombre": producto.nombre,
            "precio": float(producto.precio),
            "stock": stock
            }
    })

@admin_required
@require_http_methods(["GET", "POST"])
def editar_producto_form(request, id):
    producto = get_object_or_404(Producto, pk=id)
    form = ProductoForm(
        request.POST or None,
        request.FILES or None,
        instance=producto,
    )

    if request.method == "POST" and form.is_valid():
        producto = form.save()
        registrar_accion(request, "Edición de producto", producto.nombre)
        messages.success(request, f"El producto «{producto.nombre}» fue actualizado correctamente.")
        return redirect("administrador:dashboard")

    return render(request, "administrador/editar_registro.html", {
        "form": form,
        "titulo": "Editar producto",
        "descripcion": producto.nombre,
    })


@require_POST
@admin_required
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

    nombre_producto = producto.nombre
    producto.delete()
    registrar_accion(request, "Eliminación de producto", nombre_producto)

    return JsonResponse({
        "status": "ok",
        "mensaje": f"Producto '{producto.nombre}' eliminado correctamente."
    })

@require_POST
@admin_required
def crear_categoria(request):
    form = CategoriaForm(request.POST)

    if not form.is_valid():
        return JsonResponse({
            "status": "error",
            "details": form.errors.get_json_data()
        }, status=400)

    categoria = form.save()
    registrar_accion(request, "Creación de categoría", categoria.nombre)

    return JsonResponse({
        "status": "ok",
        "categoria": {
            "id": categoria.id,
            "nombre": categoria.nombre,
            "slug": categoria.slug
        }
    })

@require_POST
@admin_required
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
    registrar_accion(request, "Edición de categoría", categoria.nombre)

    return JsonResponse({
        "status": "ok",
        "categoria": {
            "id": categoria.id,
            "nombre": categoria.nombre,
            "slug": categoria.slug
        }
    })

@admin_required
@require_http_methods(["GET", "POST"])
def editar_categoria_form(request, id):
    categoria = get_object_or_404(Categoria, pk=id)
    form = CategoriaForm(request.POST or None, instance=categoria)

    if request.method == "POST" and form.is_valid():
        categoria = form.save()
        registrar_accion(request, "Edición de categoría", categoria.nombre)
        messages.success(request, f"La categoría «{categoria.nombre}» fue actualizada correctamente.")
        return redirect("administrador:dashboard")

    return render(request, "administrador/editar_registro.html", {
        "form": form,
        "titulo": "Editar categoría",
        "descripcion": categoria.nombre,
    })


@require_POST
@admin_required
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
@admin_required
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
        registrar_accion(
            request,
            "Actualización de inventario",
            f"{producto.nombre}: disponible {inventario.cantidad_disponible}, mínimo {inventario.stock_minimo}",
        )

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

@admin_required
def listar_clientes(request):
    busqueda = request.GET.get('q', '').strip()
    clientes_qs = Cliente.objects.prefetch_related('pedidos').all()

    if busqueda:
        clientes_qs = clientes_qs.filter(
            Q(nombre__icontains=busqueda) |
            Q(telefono__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )

    # Comprobar si la búsqueda devolvió coincidencias antes de serializar los datos.
    hay_resultados = clientes_qs.exists()

    clientes_data = [
        {
            'id': c.id,
            'nombre': c.nombre,
            'telefono': c.telefono,
            'direccion_habitual': c.direccion_habitual,
            'ciudad': c.ciudad or '',
            'email': c.email or '',
            'total_pedidos': c.total_pedidos,
            'total_gastado': float(c.total_gastado),
            'fecha_registro': c.fecha_registro.strftime('%Y-%m-%d %H:%M')
        }
        for c in clientes_qs
    ]

    return JsonResponse({
        'status': 'ok',
        'clientes': clientes_data,
        'hay_resultados': hay_resultados,
        'mensaje': '' if hay_resultados else 'No se encontraron clientes que coincidan con la búsqueda.',
    })


@admin_required
def detalle_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    pedidos = Pedido.objects.filter(
        Q(cliente=cliente) | Q(cliente__isnull=True, telefono=cliente.telefono)
    ).order_by('-id')

    pedidos_data = [
        {
            'id': p.id,
            'codigo': p.codigo_seguimiento,
            'estado': p.estado,
            'estado_display': p.get_estado_display(),
            'monto_total': float(p.monto_total),
            'fecha': p.fecha_creacion.strftime('%Y-%m-%d %H:%M') if hasattr(p, 'fecha_creacion') else ''
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
            'ciudad': cliente.ciudad or '',
            'email': cliente.email or '',
            'notas': cliente.notas or '',
            'total_pedidos': cliente.total_pedidos,
            'total_gastado': float(cliente.total_gastado),
            'pedidos': pedidos_data
        }
    })

def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('administrador:dashboard')
        return HttpResponseForbidden('Esta cuenta no tiene acceso al panel administrativo.')

    error_message = None
    if request.method == 'POST':
        usuario = request.POST.get('username', '').strip()
        clave = request.POST.get('password', '')
        user = authenticate(request, username=usuario, password=clave)

        if user is not None and user.is_staff:
            login(request, user)
            next_url = request.GET.get('next', '')
            if next_url and url_has_allowed_host_and_scheme(
                next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)
            return redirect('administrador:dashboard')

        error_message = "Usuario o contraseña incorrectos."

    return render(request, 'administrador/login.html', {'error': error_message})


@admin_required
@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse({
        'status': 'ok',
        'redirect_url': reverse('administrador:login'),
    })


@admin_required
@require_http_methods(["GET", "POST"])
def confirmar_eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, pk=producto_id)
    if request.method == "POST":
        nombre = producto.nombre
        producto.delete()
        registrar_accion(request, "Eliminación de producto", nombre)
        messages.success(request, f"El producto «{nombre}» fue eliminado correctamente.")
        return redirect("administrador:dashboard")
    return render(request, "administrador/confirmar_eliminacion.html", {
        "tipo": "producto",
        "objeto": producto,
        "mensaje": "Se eliminará el producto. Los detalles históricos de pedidos conservarán el registro como producto eliminado.",
    })


@admin_required
@require_http_methods(["GET", "POST"])
def confirmar_eliminar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    if request.method == "POST":
        if categoria.productos.exists():
            messages.error(request, "No se puede eliminar una categoría que todavía tiene productos asociados.")
            return redirect("administrador:dashboard")
        nombre = categoria.nombre
        categoria.delete()
        registrar_accion(request, "Eliminación de categoría", nombre)
        messages.success(request, f"La categoría «{nombre}» fue eliminada correctamente.")
        return redirect("administrador:dashboard")
    return render(request, "administrador/confirmar_eliminacion.html", {
        "tipo": "categoría",
        "objeto": categoria,
        "mensaje": "Solo se podrá eliminar si no tiene productos asociados.",
        "bloqueado": categoria.productos.exists(),
    })
