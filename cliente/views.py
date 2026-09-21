from django.shortcuts import render

def home(request):
    return render(request, 'cliente/index.html')       #Vista principal de la parte pública de GastroCtrl (Home / Menú).

def menu(request):
    return render(request, 'cliente/menu.html')        # Vista del catálogo / menú de productos.