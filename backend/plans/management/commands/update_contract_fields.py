from django.core.management.base import BaseCommand
from plans.models import PlanAdesion
from contracts.models import ContractLog


class Command(BaseCommand):
    help = 'Atualiza os campos contract_status e contract_token nos PlanAdesion baseado no ContractLog'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando atualização dos campos de contrato...')
        
        # Busca todos os PlanAdesion que não têm contract_status ou contract_token
        plan_adesions = PlanAdesion.objects.filter(
            contract_status__isnull=True
        ).select_related('licensed')
        
        updated_count = 0
        not_found_count = 0
        
        for plan_adesion in plan_adesions:
            try:
                # Busca o ContractLog mais recente para este licensed
                contract_log = ContractLog.objects.filter(
                    licensed__user=plan_adesion.licensed
                ).order_by('-id').first()
                
                if contract_log:
                    plan_adesion.contract_status = contract_log.status
                    plan_adesion.contract_token = contract_log.document_token
                    plan_adesion.save()
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✅ PlanAdesion {plan_adesion.id} atualizado - Status: {contract_log.status}'
                        )
                    )
                else:
                    not_found_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️  ContractLog não encontrado para PlanAdesion {plan_adesion.id}'
                        )
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'❌ Erro ao processar PlanAdesion {plan_adesion.id}: {e}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 Resumo:\n'
                f'- Registros atualizados: {updated_count}\n'
                f'- Registros sem ContractLog: {not_found_count}\n'
                f'- Total processado: {len(plan_adesions)}'
            )
        )
