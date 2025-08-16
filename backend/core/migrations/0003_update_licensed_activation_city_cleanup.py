from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='licensed',
            name='city_name',
        ),
        migrations.RemoveField(
            model_name='licensed',
            name='state_abbr',
        ),
        migrations.AddField(
            model_name='licensed',
            name='dtt_activation',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='Data Ativação'),
            preserve_default=True,
        ),
    ]


