from datetime import date, timedelta

from django.db.models import Avg, Count, F, Sum
from django.utils import timezone

from cliente.models import Categoria, DetallePedido, Pedido


def _inicio_mes(fecha, meses_atras=0):
    """Devuelve el primer día del mes desplazado una cantidad de meses."""
    indice = fecha.year * 12 + fecha.month - 1 - meses_atras
    return date(indice // 12, indice % 12 + 1, 1)


def generar_datos_dashboard():
    hoy = timezone.localdate()
    pedidos_validos = Pedido.objects.exclude(estado="CANCELADO")
    inicio_mes = _inicio_mes(hoy)

    ingresos_totales = pedidos_validos.aggregate(total=Sum("monto_total"))["total"] or 0
    cantidad_pedidos = pedidos_validos.count()
    ticket_promedio = pedidos_validos.aggregate(promedio=Avg("monto_total"))["promedio"] or 0
    pedidos_pendientes = Pedido.objects.filter(
        estado__in=["PENDIENTE", "EN_PREPARACION"]
    ).count()
    ingresos_mes = pedidos_validos.filter(
        creado_en__date__gte=inicio_mes,
        creado_en__date__lte=hoy,
    ).aggregate(total=Sum("monto_total"))["total"] or 0

    dias_semana_map = {0: "Lun", 1: "Mar", 2: "Mié", 3: "Jue", 4: "Vie", 5: "Sáb", 6: "Dom"}
    semana_labels, semana_data = [], []
    for desplazamiento in range(6, -1, -1):
        fecha = hoy - timedelta(days=desplazamiento)
        semana_labels.append(dias_semana_map[fecha.weekday()])
        total = pedidos_validos.filter(creado_en__date=fecha).aggregate(total=Sum("monto_total"))["total"] or 0
        semana_data.append(float(total))

    trend_days = {"labels": semana_labels, "data": semana_data}

    weeks_labels, weeks_data = [], []
    for numero in range(3, -1, -1):
        fin = hoy - timedelta(days=numero * 7)
        inicio = fin - timedelta(days=6)
        total = pedidos_validos.filter(
            creado_en__date__gte=inicio,
            creado_en__date__lte=fin,
        ).aggregate(total=Sum("monto_total"))["total"] or 0
        weeks_labels.append(f"{inicio.strftime('%d/%m')}-{fin.strftime('%d/%m')}")
        weeks_data.append(float(total))
    trend_weeks = {"labels": weeks_labels, "data": weeks_data}

    meses_nombres = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    months_labels, months_data = [], []
    for meses_atras in range(5, -1, -1):
        primer_dia = _inicio_mes(hoy, meses_atras)
        if meses_atras == 0:
            ultimo_dia = hoy
        else:
            ultimo_dia = _inicio_mes(hoy, meses_atras - 1) - timedelta(days=1)
        total = pedidos_validos.filter(
            creado_en__date__gte=primer_dia,
            creado_en__date__lte=ultimo_dia,
        ).aggregate(total=Sum("monto_total"))["total"] or 0
        months_labels.append(f"{meses_nombres[primer_dia.month - 1]} {primer_dia.year}")
        months_data.append(float(total))
    trend_months = {"labels": months_labels, "data": months_data}
    trend_data = {"days": trend_days, "weeks": trend_weeks, "months": trend_months}

    categorias = Categoria.objects.order_by("nombre")
    detalles_base = DetallePedido.objects.filter(pedido__in=pedidos_validos, producto__isnull=False)

    def obtener_pie(inicio, fin=hoy):
        detalles = detalles_base.filter(
            pedido__creado_en__date__gte=inicio,
            pedido__creado_en__date__lte=fin,
        )
        resultados = detalles.values("producto__categoria_id", "producto__categoria__nombre").annotate(
            total=Sum(F("precio_unitario") * F("cantidad"))
        )
        por_categoria = {fila["producto__categoria_id"]: float(fila["total"] or 0) for fila in resultados}
        return {
            "labels": [categoria.nombre for categoria in categorias],
            "data": [por_categoria.get(categoria.id, 0) for categoria in categorias],
        }

    inicio_semana = hoy - timedelta(days=6)
    inicio_periodo_semanas = hoy - timedelta(days=27)
    pie_data = {
        "days": obtener_pie(inicio_semana),
        "weeks": obtener_pie(inicio_periodo_semanas),
        "months": obtener_pie(_inicio_mes(hoy, 5)),
    }

    top_productos = list(
        detalles_base.values("producto__nombre")
        .annotate(unidades=Sum("cantidad"), ingresos=Sum(F("precio_unitario") * F("cantidad")))
        .order_by("-unidades", "producto__nombre")[:5]
    )

    return {
        "kpis": {
            "ingresos_totales": float(ingresos_totales),
            "ingresos_mes": float(ingresos_mes),
            "cantidad_pedidos": cantidad_pedidos,
            "ticket_promedio": float(ticket_promedio),
            "pedidos_pendientes": pedidos_pendientes,
        },
        "semana_labels": semana_labels,
        "semana_data": semana_data,
        "trend_data": trend_data,
        "pie_data": pie_data,
        "top_productos": top_productos,
    }
