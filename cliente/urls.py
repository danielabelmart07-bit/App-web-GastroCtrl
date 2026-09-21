from django.urls import path
from . import views

app_name = 'cliente'

urlpatterns = [
    # Páginas principales
    path('', views.home, name='home'),
    path('menu/', views.menu, name='menu'),

    # Carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/restar/<int:producto_id>/', views.restar_del_carrito, name='restar_del_carrito'),
    path('carrito/eliminar/<int:producto_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),

    # API del carrito
    path('api/carrito/', views.estado_carrito_api, name='api_carrito'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    # Seguimiento de pedido
    path(
        'api/pedido/seguimiento/<str:codigo>/',
        views.consultar_estado_pedido_api,
        name='api_seguimiento_pedido'
    ),
]