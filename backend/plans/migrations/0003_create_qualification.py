from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_operator_city_fields'),
        ('plans', '0002_alter_plan_bonus_level_1_alter_plan_bonus_level_2_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Qualification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),                
                ('licensed', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qualifications', to='core.licensed', verbose_name='Licenciado')),
                ('plan_career', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qualifications', to='plans.plancareer', verbose_name='Plano de Carreira')),
                ('dtt_qualification', models.DateTimeField(auto_now_add=True, verbose_name='Data Qualificação')),
            ],
            options={
                'verbose_name': 'Qualificação',
                'verbose_name_plural': 'Qualificações',
                'db_table': 'Qualification',
            },
        ),
        migrations.AddConstraint(
            model_name='qualification',
            constraint=models.UniqueConstraint(fields=('licensed', 'plan_career'), name='uq_qualification_licensed_career'),
        ),
        migrations.AddIndex(
            model_name='qualification',
            index=models.Index(fields=['licensed'], name='plans_quali_licensed_idx'),
        ),
        migrations.AddIndex(
            model_name='qualification',
            index=models.Index(fields=['plan_career'], name='plans_quali_career_idx'),
        ),
    ]
