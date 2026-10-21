from django import forms 
from django.utils.text import slugify
from cliente.models import Producto, Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = [
            'nombre',
            'slug',
        ]
        widgets = {
            'slug': forms.TextInput(attrs={'placeholder': 'Opcional (se genera automaticamente )'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False

    def clean(self):
        cleaned_data = super().clean()
        nombre = cleaned_data.get('nombre')
        slug = cleaned_data.get('slug')

        if not slug and nombre:
            cleaned_data['slug'] = slugify(nombre)

        return cleaned_data

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