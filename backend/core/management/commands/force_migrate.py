from django.core.management.base import BaseCommand
from django.db import connection
from django.core.management import call_command
import os


class Command(BaseCommand):
    help = 'Aplica migrações ignorando dependências problemáticas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirma a execução (obrigatório)',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.ERROR(
                    'ATENÇÃO: Este comando irá aplicar migrações forçadamente!\n'
                    'Use --confirm para executar.'
                )
            )
            return

        self.stdout.write('🚀 Aplicando migrações forçadamente...')
        
        # Lista de apps para aplicar migrações
        apps = ['contenttypes', 'auth', 'core', 'admin', 'location', 'network', 'plans', 'finance', 'notifications', 'contracts', 'contractor', 'sessions']
        
        for app in apps:
            try:
                self.stdout.write(f'📦 Aplicando migrações do app: {app}')
                call_command('migrate', app, verbosity=0)
                self.stdout.write(f'  ✅ {app} - OK')
            except Exception as e:
                self.stdout.write(f'  ⚠️  {app} - Erro: {str(e)[:100]}...')
                # Marcar migrações como aplicadas se houver erro
                try:
                    call_command('migrate', app, '--fake', verbosity=0)
                    self.stdout.write(f'  🔧 {app} - Marcado como aplicado (fake)')
                except:
                    pass

        # Tentar aplicar todas as migrações finais
        try:
            self.stdout.write('🔄 Aplicando migrações finais...')
            call_command('migrate', verbosity=0)
            self.stdout.write('✅ Migrações finais aplicadas com sucesso!')
        except Exception as e:
            self.stdout.write(f'⚠️  Erro nas migrações finais: {str(e)[:100]}...')

        # Verificar se conseguimos criar um superusuário
        try:
            self.stdout.write('👤 Testando criação de superusuário...')
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            if not User.objects.filter(username='admin').exists():
                User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
                self.stdout.write('✅ Superusuário criado: admin/admin123')
            else:
                self.stdout.write('ℹ️  Superusuário admin já existe')
                
        except Exception as e:
            self.stdout.write(f'⚠️  Erro ao criar superusuário: {str(e)[:100]}...')

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Processo concluído!\n'
                'Tente acessar o admin em: http://127.0.0.1:8000/admin/\n'
                'Usuário: admin | Senha: admin123'
            )
        )
