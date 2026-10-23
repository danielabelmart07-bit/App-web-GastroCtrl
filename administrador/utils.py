import json
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from cliente.models import Pedido, DetallePedido, Categoria

def generar_datos_dashboard():
    hoy = timezone.now().date()
    pedidos_validos = Pedido.objects.exclude(estado='CANCELADO')

    # 1. KPIs Generales
    ingresos_totales = pedidos_validos.aggregate(total=Sum('monto_total'))['total'] or 0.00
    cantidad_pedidos = pedidos_validos.count()
    ticket_promedio = pedidos_validos.aggregate(promedio=Avg('monto_total'))['promedio'] or 0.00
    pedidos_pendientes = Pedido.objects.filter(estado__in=['PENDIENTE', 'EN_PREPARACION']).count()

    # 2. Gráfico de 7 Días (Weekly Chart)
    dias_semana_map = {0: 'Lun', 1: 'Mar', 2: 'Mié', 3: 'Jue', 4: 'Vie', 5: 'Sáb', 6: 'Dom'}
    semana_labels = []
    semana_data = []

    for i in range(6, -1, -1):
        fecha_dia = hoy - timedelta(days=i)
        semana_labels.append(dias_semana_map[fecha_dia.weekday()])
        total_dia = pedidos_validos.filter(creado_en__date=fecha_dia).aggregate(total=Sum('monto_total'))['total'] or 0.00
        semana_data.append(float(total_dia))

    # 3. Tendencia de Ventas (Trend Data)
    trend_days = {'labels': semana_labels, 'data': semana_data}

    weeks_labels, weeks_data = [], []
    for w in range(3, -1, -1):
        inicio = hoy - timedelta(days=hoy.weekday() + (w * 7))
        fin = inicio + timedelta(days=6)
        weeks_labels.append(f"Sem {4 - w}")
        total_semana = pedidos_validos.filter(creado_en__date__gte=inicio, creado_en__date__lte=fin).aggregate(total=Sum('monto_total'))['total'] or 0.00
        weeks_data.append(float(total_semana))
    trend_weeks = {'labels': weeks_labels, 'data': weeks_data}

    months_labels, months_data = [], []
    meses_nombres = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    for m in range(5, -1, -1):
        primer_dia = (hoy.replace(day=1) - timedelta(days=m * 30)).replace(day=1)
        months_labels.append(meses_nombres[primer_dia.month - 1])
        total_mes = pedidos_validos.filter(creado_en__year=primer_dia.year, creado_en__month=primer_dia.month).aggregate(total=Sum('monto_total'))['total'] or 0.00
        months_data.append(float(total_mes))
    trend_months = {'labels': months_labels, 'data': months_data}

    trend_data = {'days': trend_days, 'weeks': trend_weeks, 'months': trend_months}

    # 4. Distribución por Categorías (Pie Data)
    categorias = Categoria.objects.all()

    def obtener_pie(desde=None):
        labels, data = [], []
        detalles = DetallePedido.objects.filter(pedido__in=pedidos_validos)
        if desde:
            detalles = detalles.filter(pedido__creado_en__gte=desde)
        for cat in categorias:
            total_cat = detalles.filter(producto__categoria=cat).aggregate(total=Sum('precio_unitario') * Sum('cantidad'))['total'] or 0.00
            labels.append(cat.nombre)
            data.append(float(total_cat))
        return {'labels': labels, 'data': data if sum(data) > 0 else [0] * len(labels)}

    pie_data = {
        'days': obtener_pie(hoy - timedelta(days=7)),
        'weeks': obtener_pie(hoy - timedelta(days=30)),
        'months': obtener_pie(hoy - timedelta(days=365))
    }

    # 5. Top 5 Productos Más Vendidos
    top_productos = list(
        DetallePedido.objects.filter(pedido__in=pedidos_validos)
        .values('producto__nombre')
        .annotate(unidades=Sum('cantidad'))
        .order_by('-unidades')[:5]
    )

    return {
        'kpis': {
            'ingresos_totales': float(ingresos_totales),
            'cantidad_pedidos': cantidad_pedidos,
            'ticket_promedio': float(ticket_promedio),
            'pedidos_pendientes': pedidos_pendientes,
        },
        'semana_labels': semana_labels,
        'semana_data': semana_data,
        'trend_data': trend_data,
        'pie_data': pie_data,
        'top_productos': top_productos,
    }