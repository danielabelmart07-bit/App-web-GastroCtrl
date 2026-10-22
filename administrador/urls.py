from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path(
        'api/pedidos/<str:codigo>/estado/',
        views.actualizar_estado_pedido,
        name='actualizar_estado_pedido',
    ),
    path(
        'api/configuracion/envio/',
        views.actualizar_configuracion_envio,
        name='actualizar_configuracion_envio',
    ),
    path(
        'api/productos/crear/',
        views.crear_producto,
        name='crear_producto',
    ),
    path(
        'api/productos/editar/',
        views.editar_producto,
        name='editar_producto'
    ),
    path(
        'api/productos/eliminar/',
        views.eliminar_producto,
        name='eliminar_producto'
    ),
    path(
        'api/categorias/crear/',
        views.crear_categoria,
        name='crear_categoria',
    ),
    path(
        'api/categorias/editar/',
        views.editar_categoria,
        name='editar_categoria',
    ),
    path(
        'api/categorias/eliminar/',
        views.eliminar_categoria,
        name='eliminar_categoria',
    ),
    path(
        'api/inventario/actualizar/',
        views.actualizar_inventario,
        name='actualizar_inventario',
    )
]
