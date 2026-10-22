from cliente.models import Cliente

def vincular_o_crear_cliente(nombre, telefono, direccion=None):
    telefono_limpio = telefono.strip()
    if not telefono_limpio:
        return None

    cliente, creado = Cliente.objects.get_or_create(
        telefono=telefono_limpio,
        defaults={
            'nombre': nombre.strip(),
            'direccion_habitual': direccion.strip() if direccion else ''
        }
    )

    if not creado:
        cliente.nombre = nombre.strip()
        if direccion:
            cliente.direccion_habitual = direccion.strip()
        cliente.save(update_fields=['nombre', 'direccion_habitual'])

    return cliente