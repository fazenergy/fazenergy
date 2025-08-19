from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0005_scorereference'),
    ]

    operations = [
        migrations.AddField(
            model_name='scorereference',
            name='status',
            field=models.CharField(choices=[('valid', 'Válido'), ('pending', 'Pendente'), ('canceled', 'Cancelado')], default='pending', max_length=20, verbose_name='Status'),
        ),
        migrations.AddIndex(
            model_name='scorereference',
            index=models.Index(fields=['status'], name='network_sc_status_idx'),
        ),
    ]


