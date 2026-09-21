from django.contrib import admin
from .models import BitacoraAccion

@admin.register(BitacoraAccion)
class BitacoraAccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'fecha_hora')
    list_filter = ('fecha_hora', 'usuario')
    search_fields = ('accion', 'detalles')