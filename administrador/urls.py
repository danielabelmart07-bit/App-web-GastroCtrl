from django.urls import path
from . import views

app_name = 'administrador'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('productos/<int:producto_id>/eliminar/confirmar/', views.confirmar_eliminar_producto, name='confirmar_eliminar_producto'),
    path('categorias/<int:categoria_id>/eliminar/confirmar/', views.confirmar_eliminar_categoria, name='confirmar_eliminar_categoria'),
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
    ),
    path(
        'api/clientes/',
        views.listar_clientes,
        name='listar_clientes',
    ),
    path(
        'api/clientes/<int:cliente_id>',
        views.detalle_cliente,
        name='detalle_cliente',
    ),
    path(
        'login/', 
        views.login_view, 
        name='login',
    ),
    path(
        'logout/', 
        views.logout_view, 
        name='logout',
    ),
]
