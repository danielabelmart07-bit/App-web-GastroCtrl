import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from cliente.models import Pedido
from .models import ConfiguracionSistema


def dashboard(request):
    pedidos = Pedido.objects.prefetch_related('detalles__producto').all()

    pedidos_data = [
        {
            'id': f'#{pedido.codigo_seguimiento}',
            'codigo': pedido.codigo_seguimiento,
            'customer': pedido.nombre_cliente,
            'items': ', '.join(
                f'{detalle.cantidad}x {detalle.producto.nombre if detalle.producto else "Producto eliminado"}'
                for detalle in pedido.detalles.all()
            ) or 'Sin detalle',
            'total': float(pedido.monto_total),
            'status': pedido.estado.lower(),
            'time': pedido.creado_en.strftime('%d/%m/%Y %H:%M'),
        }
        for pedido in pedidos
    ]

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)

    return render(
        request,
        'administrador/index.html',
        {
            'pedidos_json': json.dumps(pedidos_data),
            'costo_envio': configuracion.costo_envio,
        }
    )


@require_POST
def actualizar_estado_pedido(request, codigo):
    """Actualiza el estado real del pedido desde el panel de administración."""
    pedido = get_object_or_404(Pedido, codigo_seguimiento__iexact=codigo.strip())

    try:
        data = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse(
            {'status': 'error', 'mensaje': 'Solicitud inválida.'},
            status=400
        )

    nuevo_estado = data.get('estado')

    estados_validos = {valor for valor, _ in Pedido.ESTADOS}

    if nuevo_estado not in estados_validos:
        return JsonResponse(
            {'status': 'error', 'mensaje': 'Estado de pedido inválido.'},
            status=400
        )

    pedido.estado = nuevo_estado
    pedido.save(update_fields=['estado'])

    return JsonResponse({
        'status': 'ok',
        'codigo': pedido.codigo_seguimiento,
        'estado': pedido.estado,
        'estado_display': pedido.get_estado_display(),
    })


@require_POST
def actualizar_configuracion_envio(request):
    try:
        data = json.loads(request.body or '{}')
        costo = float(data.get('costo_envio', 800))
        if costo < 0:
            raise ValueError
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({'status': 'error', 'mensaje': 'Costo de envío inválido.'}, status=400)

    configuracion, _ = ConfiguracionSistema.objects.get_or_create(pk=1)
    configuracion.costo_envio = costo
    configuracion.save(update_fields=['costo_envio'])

    return JsonResponse({
        'status': 'ok',
        'costo_envio': float(configuracion.costo_envio),
    })
