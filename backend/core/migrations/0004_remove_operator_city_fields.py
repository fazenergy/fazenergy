from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_update_licensed_activation_city_cleanup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='operator',
            name='city_name',
        ),
        migrations.RemoveField(
            model_name='operator',
            name='state_abbr',
        ),
    ]


