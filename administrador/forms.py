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
        labels = {'nombre': 'Nombre de la categoría', 'slug': 'Identificador (slug)'}
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'w-full rounded-xl border border-cream-300 px-4 py-3', 'placeholder': 'Ej. Panadería'}),
            'slug': forms.TextInput(attrs={'class': 'w-full rounded-xl border border-cream-300 px-4 py-3', 'placeholder': 'Opcional; se genera automáticamente'}),
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
        labels = {'categoria': 'Categoría', 'nombre': 'Nombre del producto', 'descripcion': 'Descripción', 'precio': 'Precio ($)', 'imagen': 'Imagen del producto', 'es_destacado': 'Mostrar como destacado', 'activo': 'Disponible en el menú'}
        widgets = {
            'categoria': forms.Select(attrs={'class': 'w-full rounded-xl border border-cream-300 px-4 py-3'}),
            'nombre': forms.TextInput(attrs={'class': 'w-full rounded-xl border border-cream-300 px-4 py-3', 'placeholder': 'Ej. Medialuna de manteca'}),
            'descripcion': forms.Textarea(attrs={'class': 'w-full rounded-xl border border-cream-300 px-4 py-3', 'placeholder': 'Describí brevemente el producto', 'rows': 3}),
            'precio': forms.NumberInput(attrs={'class': 'w-full rounded-xl border border-cream-300 px-4 py-3', 'placeholder': 'Ej. 1500.00', 'min': '0', 'step': '0.01'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'w-full rounded-xl border border-cream-300 px-4 py-3'}),
            'es_destacado': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-cream-300 text-coffee-600 focus:ring-coffee-500'}),
            'activo': forms.CheckboxInput(attrs={'class': 'h-4 w-4 rounded border-cream-300 text-coffee-600 focus:ring-coffee-500'}),
        }

from .models import PerfilAdministrador


class PerfilAdministradorForm(forms.ModelForm):
    class Meta:
        model = PerfilAdministrador
        fields = ["foto"]
        labels = {"foto": "Foto de perfil"}
        widgets = {
            "foto": forms.ClearableFileInput(attrs={
                "accept": "image/jpeg,image/png,image/webp",
                "class": "w-full rounded-xl border border-cream-300 bg-white px-4 py-3 text-sm",
            }),
        }

    def clean_foto(self):
        foto = self.cleaned_data.get("foto")
        if foto and foto.size > 2 * 1024 * 1024:
            raise forms.ValidationError("La imagen no puede superar los 2 MB.")
        return foto
