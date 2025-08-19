from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='licensed',
            name='previous_career',
        ),
        migrations.RemoveField(
            model_name='licensed',
            name='dtt_previous_career',
        ),
    ]


