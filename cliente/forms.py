from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, Pedido

class PedidoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['direccion'].required = False

    class Meta:
        model = Pedido
        fields = ['nombre_cliente', 'telefono', 'direccion', 'notas']
        widgets = {
            'nombre_cliente': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Juan Pérez'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 1122334455'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Av. Mayo 1234'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Ej. Timbre B, sin mayonesa...'}),
        }

class RegistroClienteForm(UserCreationForm):
    nombre = forms.CharField(max_length=100, label="Nombre completo", widget=forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "name"}))
    telefono = forms.CharField(max_length=20, label="Teléfono / WhatsApp", widget=forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "tel"}))
    direccion_habitual = forms.CharField(max_length=255, required=False, label="Dirección habitual", widget=forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "street-address"}))
    ciudad = forms.CharField(max_length=100, required=False, label="Ciudad", widget=forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "address-level2", "placeholder": "Ej. Hurlingham"}))
    email = forms.EmailField(label="Correo electrónico", widget=forms.EmailInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "email"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Contraseña"
        self.fields["password1"].help_text = "Mínimo 8 caracteres."
        self.fields["password2"].label = "Repetir contraseña"
        self.fields["password2"].help_text = "Ingresá la misma contraseña nuevamente."
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "w-full rounded-xl border border-cream-300 px-4 py-3 focus:border-coffee-500 focus:outline-none")
        self.fields["password1"].widget.attrs.update({"autocomplete": "new-password", "placeholder": "Mínimo 8 caracteres"})
        self.fields["password2"].widget.attrs.update({"autocomplete": "new-password", "placeholder": "Repetí tu contraseña"})

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")
        widgets = {"username": forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "username"})}

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if Cliente.objects.filter(telefono=telefono).exists():
            raise forms.ValidationError("Ya existe una cuenta con ese teléfono.")
        return telefono


class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ("nombre", "telefono", "direccion_habitual", "ciudad", "email")
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "name"}),
            "telefono": forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "tel"}),
            "direccion_habitual": forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "street-address"}),
            "ciudad": forms.TextInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "address-level2", "placeholder": "Ej. Hurlingham"}),
            "email": forms.EmailInput(attrs={"class": "w-full rounded-xl border border-cream-300 px-4 py-3", "autocomplete": "email"}),
        }

    def clean_telefono(self):
        telefono = self.cleaned_data["telefono"].strip()
        if Cliente.objects.filter(telefono=telefono).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Ya existe un cliente registrado con ese teléfono.")
        return telefono
