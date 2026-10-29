from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cliente", "0006_cliente_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="pedido",
            name="archivado",
            field=models.BooleanField(
                db_index=True,
                default=False,
                verbose_name="Archivado en administración",
            ),
        ),
    ]
