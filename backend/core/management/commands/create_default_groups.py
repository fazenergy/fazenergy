# core/management/commands/create_default_groups.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = 'Cria grupos padrão para o sistema FazEnergy'

    def handle(self, *args, **options):
        # Grupos padrão do sistema
        groups_data = [
            {
                'name': 'Administrador',
                'description': 'Acesso total ao sistema'
            },
            {
                'name': 'Operador',
                'description': 'Operadores do sistema'
            },
            {
                'name': 'Afiliado',
                'description': 'Usuários afiliados'
            },
            {
                'name': 'Supervisor',
                'description': 'Supervisores de rede'
            },
            {
                'name': 'Financeiro',
                'description': 'Acesso ao módulo financeiro'
            }
        ]

        created_count = 0
        for group_data in groups_data:
            group, created = Group.objects.get_or_create(
                name=group_data['name']
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Grupo "{group.name}" criado com sucesso!')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ Grupo "{group.name}" já existe.')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Processo concluído! {created_count} grupos criados.')
        )
