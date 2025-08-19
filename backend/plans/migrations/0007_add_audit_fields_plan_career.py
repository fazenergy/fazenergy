from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0006_merge_20250816_1551'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='plancareer',
            name='usr_record',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plan_careers_created', to=settings.AUTH_USER_MODEL, verbose_name='User Record'),
        ),
        migrations.AddField(
            model_name='plancareer',
            name='usr_update',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='plan_careers_updated', to=settings.AUTH_USER_MODEL, verbose_name='User Update'),
        ),
    ]


