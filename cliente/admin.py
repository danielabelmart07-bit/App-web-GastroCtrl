from django.contrib import admin
from .models import Categoria, Producto, Inventario, Insumo, Pedido, DetallePedido, RecetaInsumo, ConsumoInsumoPedido

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}  # Genera el slug automáticamente al escribir el nombre


class InventarioInline(admin.StackedInline):
    """Permite editar el stock directamente desde la pantalla del Producto"""
    model = Inventario
    can_delete = False
    verbose_name_plural = 'Control de Inventario'


class RecetaInsumoInline(admin.TabularInline):
    model = RecetaInsumo
    extra = 1
    autocomplete_fields = ('insumo',)
    fields = ('insumo', 'cantidad_por_unidad')
    verbose_name = 'Ingrediente de la receta'
    verbose_name_plural = 'Receta e insumos por unidad'


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'es_destacado', 'activo', 'creado_en')
    list_filter = ('categoria', 'es_destacado', 'activo')
    search_fields = ('nombre', 'descripcion')
    inlines = [InventarioInline, RecetaInsumoInline]  # Stock terminado y materias primas por unidad


@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad_disponible', 'stock_minimo')
    list_editable = ('cantidad_disponible', 'stock_minimo')

@admin.register(Insumo)
class InsumoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'unidad_medida', 'cantidad_disponible', 'stock_minimo', 'activo')
    list_filter = ('activo', 'unidad_medida')
    search_fields = ('nombre',)
    list_editable = ('cantidad_disponible', 'stock_minimo', 'activo')

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



@admin.register(ConsumoInsumoPedido)
class ConsumoInsumoPedidoAdmin(admin.ModelAdmin):
    list_display = ('pedido', 'insumo', 'cantidad', 'reintegrado')
    list_filter = ('reintegrado',)
    search_fields = ('pedido__codigo_seguimiento', 'insumo__nombre')
    readonly_fields = ('pedido', 'insumo', 'cantidad', 'reintegrado')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
