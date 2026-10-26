from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0005_cliente_pedido_cliente'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedido',
            name='archivado',
            field=models.BooleanField(db_index=True, default=False, verbose_name='Archivado'),
        ),
    ]
