import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Producto
from .carrito import Carrito

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