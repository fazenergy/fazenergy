from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Nome do Produto')),
                ('dtt_record', models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')),
                ('dtt_update', models.DateTimeField(auto_now=True, verbose_name='Data Atualização')),
            ],
            options={
                'verbose_name': 'Produto',
                'verbose_name_plural': 'Produtos',
                'db_table': 'Product',
            },
        ),
    ]

