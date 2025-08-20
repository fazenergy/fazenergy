from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0003_remove_contractconfig_signer_company_email_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='ContractLog',
        ),
    ]


