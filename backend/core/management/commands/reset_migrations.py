from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import os


class Command(BaseCommand):
    help = 'Limpa o histórico de migrações e recria as tabelas'

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
                    'ATENÇÃO: Este comando irá APAGAR todas as tabelas do banco de dados!\n'
                    'Use --confirm para executar.'
                )
            )
            return

        self.stdout.write('🗑️  Limpando histórico de migrações...')
        
        with connection.cursor() as cursor:
            # Limpar tabela de migrações
            cursor.execute("DELETE FROM django_migrations;")
            self.stdout.write('✅ Histórico de migrações limpo')
            
            # Listar todas as tabelas do projeto
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public' 
                AND tablename NOT LIKE 'pg_%'
                AND tablename NOT LIKE 'sql_%'
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            
            if tables:
                self.stdout.write(f'🗑️  Removendo {len(tables)} tabelas...')
                
                # Desabilitar constraints temporariamente
                cursor.execute("SET session_replication_role = replica;")
                
                # Remover todas as tabelas
                for table in tables:
                    cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE;')
                    self.stdout.write(f'  ✅ Removida: {table}')
                
                # Reabilitar constraints
                cursor.execute("SET session_replication_role = DEFAULT;")
                
                self.stdout.write('✅ Todas as tabelas removidas')
            else:
                self.stdout.write('ℹ️  Nenhuma tabela encontrada')

        self.stdout.write(
            self.style.SUCCESS(
                '\n🎉 Banco de dados limpo com sucesso!\n'
                'Agora você pode executar: python manage.py migrate'
            )
        )
