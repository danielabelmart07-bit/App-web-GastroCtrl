from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cliente", "0007_pedido_archivado"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="ciudad",
            field=models.CharField(blank=True, default="", max_length=100, verbose_name="Ciudad"),
        ),
    ]
