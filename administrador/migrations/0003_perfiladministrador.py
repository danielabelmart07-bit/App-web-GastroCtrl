# Generated for administrator profile pictures.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("administrador", "0002_configuracionsistema"),
    ]

    operations = [
        migrations.CreateModel(
            name="PerfilAdministrador",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("foto", models.ImageField(blank=True, null=True, upload_to="perfiles_admin/", verbose_name="Foto de perfil")),
                ("usuario", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="perfil_admin", to=settings.AUTH_USER_MODEL, verbose_name="Administrador")),
            ],
            options={
                "verbose_name": "Perfil de administrador",
                "verbose_name_plural": "Perfiles de administradores",
            },
        ),
    ]
