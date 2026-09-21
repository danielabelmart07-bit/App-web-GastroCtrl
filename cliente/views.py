from django.shortcuts import render
from django.db.models import Q
from .models import Categoria, Producto

def home(request):
    return render(request, 'cliente/index.html')       #Vista principal de la parte pública de GastroCtrl (Home / Menú).

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