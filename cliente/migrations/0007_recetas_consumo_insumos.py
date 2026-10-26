import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0006_pedido_archivado'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedido',
            name='codigo_seguimiento',
            field=models.CharField(
                editable=False,
                max_length=32,
                unique=True,
                verbose_name='Código de Seguimiento',
            ),
        ),
        migrations.CreateModel(
            name='RecetaInsumo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad_por_unidad', models.DecimalField(decimal_places=3, max_digits=10)),
                ('insumo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='recetas', to='cliente.insumo')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receta_insumos', to='cliente.producto')),
            ],
            options={
                'verbose_name': 'Ingrediente de receta',
                'verbose_name_plural': 'Ingredientes de recetas',
                'ordering': ['producto__nombre', 'insumo__nombre'],
            },
        ),
        migrations.CreateModel(
            name='ConsumoInsumoPedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.DecimalField(decimal_places=3, max_digits=12)),
                ('insumo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='consumos_pedidos', to='cliente.insumo')),
                ('pedido', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='consumos_insumos', to='cliente.pedido')),
            ],
            options={
                'verbose_name': 'Consumo de insumo por pedido',
                'verbose_name_plural': 'Consumos de insumos por pedido',
            },
        ),
        migrations.AddConstraint(
            model_name='recetainsumo',
            constraint=models.UniqueConstraint(fields=('producto', 'insumo'), name='unique_insumo_por_producto'),
        ),
        migrations.AddConstraint(
            model_name='recetainsumo',
            constraint=models.CheckConstraint(condition=models.Q(('cantidad_por_unidad__gt', 0)), name='receta_cantidad_positiva'),
        ),
        migrations.AddConstraint(
            model_name='consumoinsumopedido',
            constraint=models.UniqueConstraint(fields=('pedido', 'insumo'), name='unique_consumo_insumo_pedido'),
        ),
        migrations.AddConstraint(
            model_name='consumoinsumopedido',
            constraint=models.CheckConstraint(condition=models.Q(('cantidad__gt', 0)), name='consumo_insumo_cantidad_positiva'),
        ),
    ]
