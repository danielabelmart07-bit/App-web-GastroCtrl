from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrador', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConfiguracionSistema',
            fields=[
                ('id', models.PositiveSmallIntegerField(default=1, editable=False, primary_key=True, serialize=False)),
                ('costo_envio', models.DecimalField(decimal_places=2, default=800, max_digits=10, verbose_name='Costo de envío delivery ($)')),
            ],
            options={
                'verbose_name': 'Configuración del Sistema',
                'verbose_name_plural': 'Configuración del Sistema',
            },
        ),
    ]
