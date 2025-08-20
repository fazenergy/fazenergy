from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_add_status_to_scorereference'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LicensedPoints',
        ),
    ]


