from django.db import models
from django.contrib.auth.models import User

class BitacoraAccion(models.Model):
    """
    Modelo en la app Administrador para registrar las acciones 
    realizadas dentro del panel de gestión.
    """
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario Admin")
    accion = models.CharField(max_length=255, verbose_name="Acción realizada")
    detalles = models.TextField(blank=True, null=True, verbose_name="Detalles de la acción")
    fecha_hora = models.DateTimeField(auto_now_add=True, verbose_name="Fecha y hora")

    class Meta:
        verbose_name = "Bitácora de Acción"
        verbose_name_plural = "Bitácora de Acciones"
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.usuario.username} - {self.accion} ({self.fecha_hora.strftime('%d/%m/%Y %H:%M')})"

class ConfiguracionSistema(models.Model):
    """Configuración general utilizada por la tienda pública."""
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    costo_envio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=800,
        verbose_name="Costo de envío delivery ($)"
    )

    class Meta:
        verbose_name = "Configuración del Sistema"
        verbose_name_plural = "Configuración del Sistema"

    def __str__(self):
        return "Configuración de GastroCtrl"
