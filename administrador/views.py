from django.shortcuts import render

def dashboard(request):
    return render(request, 'administrador/index.html')              #Vista principal del panel administrativo de GastroCtrl.
