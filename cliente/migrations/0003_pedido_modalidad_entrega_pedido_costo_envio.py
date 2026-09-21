from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0002_pedido_detallepedido'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='modalidad_entrega',
            field=models.CharField(
                choices=[('RETIRO', 'Retiro en el local'), ('DELIVERY', 'Delivery a domicilio')],
                default='RETIRO',
                max_length=10,
                verbose_name='Modalidad de entrega',
            ),
        ),
        migrations.AddField(
            model_name='pedido',
            name='costo_envio',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name='Costo de envío ($)',
            ),
        ),
    ]
