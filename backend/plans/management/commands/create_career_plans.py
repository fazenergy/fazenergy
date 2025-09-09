from django.core.management.base import BaseCommand
from plans.models.PlanCareer import PlanCareer


class Command(BaseCommand):
    help = 'Cria planos de carreira de exemplo'

    def handle(self, *args, **options):
        # Dados dos planos de carreira
        career_plans = [
            {
                'stage_name': 'Bronze',
                'reward_description': 'Certificado Bronze + Bônus de R$ 50,00',
                'required_points': 0,
                'required_directs': 0,
                'required_direct_sales': 0,
                'max_pml_per_line': 1000,
            },
            {
                'stage_name': 'Prata',
                'reward_description': 'Certificado Prata + Bônus de R$ 150,00',
                'required_points': 1000,
                'required_directs': 2,
                'required_direct_sales': 1,
                'max_pml_per_line': 2000,
            },
            {
                'stage_name': 'Ouro',
                'reward_description': 'Certificado Ouro + Bônus de R$ 300,00',
                'required_points': 5000,
                'required_directs': 5,
                'required_direct_sales': 3,
                'max_pml_per_line': 5000,
            },
            {
                'stage_name': 'Platina',
                'reward_description': 'Certificado Platina + Bônus de R$ 500,00',
                'required_points': 15000,
                'required_directs': 10,
                'required_direct_sales': 5,
                'max_pml_per_line': 10000,
            },
            {
                'stage_name': 'Diamante',
                'reward_description': 'Certificado Diamante + Bônus de R$ 1000,00',
                'required_points': 50000,
                'required_directs': 20,
                'required_direct_sales': 10,
                'max_pml_per_line': 20000,
            },
        ]

        created_count = 0
        for plan_data in career_plans:
            plan, created = PlanCareer.objects.get_or_create(
                stage_name=plan_data['stage_name'],
                defaults=plan_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Criado plano: {plan.stage_name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plano já existe: {plan.stage_name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Processo concluído. {created_count} planos criados.')
        )
