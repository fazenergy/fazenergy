from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        # Ajustado para depender do último migration existente em core
        ('core', '0010_alter_licenseddocument_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='twofa_enabled',
            field=models.BooleanField(default=False, verbose_name='2FA Habilitado?'),
        ),
        migrations.AddField(
            model_name='user',
            name='twofa_secret',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='Segredo TOTP'),
        ),
    ]


