from django import forms 
from cliente.models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'categoria',
            'nombre',
            'descripcion',
            'precio',
            'imagen',
            'es_destacado',
            'activo',
        ]