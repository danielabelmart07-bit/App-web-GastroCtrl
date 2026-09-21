from django.db import models

class Categoria(models.Model):
    """
    Modelo para clasificar los productos del menú (Panadería, Cafetería, Pastelería, etc.)
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de la categoría")
    slug = models.SlugField(max_length=100, unique=True, help_text="Identificador único para URLs (ej. panaderia)")

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Modelo principal para representar cada ítem del catálogo de GastroCtrl.
    """
    categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        related_name='productos',
        verbose_name="Categoría"
    )
    nombre = models.CharField(max_length=150, verbose_name="Nombre del producto")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción del producto")
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio ($)")
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name="Imagen del producto")
    es_destacado = models.BooleanField(default=False, verbose_name="¿Es producto destacado?")
    activo = models.BooleanField(default=True, verbose_name="¿Está disponible en el menú?")
    creado_en = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última actualización")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Inventario(models.Model):
    """
    Modelo para gestionar las existencias y alertas de stock de cada producto.
    """
    producto = models.OneToOneField(
        Producto, 
        on_delete=models.CASCADE, 
        related_name='inventario',
        verbose_name="Producto"
    )
    cantidad_disponible = models.PositiveIntegerField(default=0, verbose_name="Cantidad disponible")
    stock_minimo = models.PositiveIntegerField(default=5, verbose_name="Stock mínimo de alerta")

    class Meta:
        verbose_name = "Inventario"
        verbose_name_plural = "Inventarios"

    def __str__(self):
        return f"Stock de {self.producto.nombre}: {self.cantidad_disponible} unidades"