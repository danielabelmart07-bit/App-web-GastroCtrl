from django.contrib import admin
from .models import Categoria, Producto, Inventario, Pedido, DetallePedido

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}  # Genera el slug automáticamente al escribir el nombre


class InventarioInline(admin.StackedInline):
    """Permite editar el stock directamente desde la pantalla del Producto"""
    model = Inventario
    can_delete = False
    verbose_name_plural = 'Control de Inventario'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'es_destacado', 'activo', 'creado_en')
    list_filter = ('categoria', 'es_destacado', 'activo')
    search_fields = ('nombre', 'descripcion')
    inlines = [InventarioInline]  # Integra el formulario de inventario en el producto


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad_disponible', 'stock_minimo')
    list_editable = ('cantidad_disponible', 'stock_minimo')

class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('precio_unitario', 'cantidad')


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_seguimiento',
        'nombre_cliente',
        'telefono',
        'monto_total',
        'estado',
        'creado_en',
    )
    list_filter = ('estado', 'creado_en')
    search_fields = ('codigo_seguimiento', 'nombre_cliente', 'telefono')
    readonly_fields = ('codigo_seguimiento', 'monto_total', 'creado_en')
    inlines = [DetallePedidoInline]
