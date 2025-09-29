from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from core.models import Licensed
from plans.models import Plan, PlanAdesion
from finance.models import VirtualAccount, Transaction, BankAccount
from network.models import UnilevelNetwork


class Command(BaseCommand):
    help = "Cria um plano e uma rede de licenciados fake com adesões pagas, saldo disponível e rede unilevel. NÃO evolui carreira."

    def add_arguments(self, parser):
        parser.add_argument('--root', default='rootseed', help='Username do licenciado raiz (default: rootseed)')
        parser.add_argument('--levels', type=int, default=2, help='Níveis de rede a criar (default: 2)')
        parser.add_argument('--perlevel', type=int, default=3, help='Quantidade de diretos por nível (default: 3)')

    def handle(self, *args, **options):
        User = get_user_model()
        now = timezone.now()
        paid_at = now - timedelta(days=30)

        # 1) Plano base
        plan, _ = Plan.objects.get_or_create(
            name='Plano Seed Demo',
            defaults={
                'price': Decimal('1000.00'),
                'points': 300,
                'validity_months': 12,
                'bonus_level_1': Decimal('100.00'),
                'bonus_level_2': Decimal('50.00'),
                'bonus_level_3': Decimal('30.00'),
                'bonus_level_4': Decimal('20.00'),
                'bonus_level_5': Decimal('10.00'),
                'stt_record': True,
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Plano: {plan.name} (id={plan.id})"))

        # 2) Usuário/License raiz
        root_username = options['root']
        root_user, _ = User.objects.get_or_create(
            username=root_username,
            defaults={'email': f'{root_username}@seed.local'}
        )
        if not root_user.password:
            root_user.set_password('123456')
            root_user.save()

        root_lic, _ = Licensed.objects.get_or_create(
            user=root_user,
            defaults={
                'person_type': 'pf',
                'cpf_cnpj': '00000000001',
                'plan': plan,
                'is_root': True,
                'root_network_name': 'SeedDemo',
            }
        )

        self.stdout.write(self.style.SUCCESS(f"Licenciado raiz: {root_lic}"))

        # 3) Rede: níveis e diretos
        created_licensed = [root_lic]
        current_level = [root_lic]

        for lvl in range(1, options['levels'] + 1):
            next_level = []
            for parent in current_level:
                for i in range(1, options['perlevel'] + 1):
                    username = f"{parent.user.username}_L{lvl}N{i}"
                    user, _ = User.objects.get_or_create(
                        username=username,
                        defaults={'email': f'{username}@seed.local'}
                    )
                    if not user.password:
                        user.set_password('123456')
                        user.save()

                    cpf = f"{lvl}{i:02d}{parent.id:06d}"[:11].ljust(11, '0')
                    lic, _ = Licensed.objects.get_or_create(
                        user=user,
                        defaults={
                            'person_type': 'pf',
                            'cpf_cnpj': cpf,
                            'plan': plan,
                            'original_indicator': parent,
                        }
                    )

                    UnilevelNetwork.objects.get_or_create(
                        upline_licensed=parent,
                        downline_licensed=lic,
                        defaults={'level': lvl}
                    )

                    created_licensed.append(lic)
                    next_level.append(lic)
            current_level = next_level

        self.stdout.write(self.style.SUCCESS(f"Licenciados criados: {len(created_licensed)}"))

        # 4) Adesões pagas (simula pagamento confirmado há 30 dias)
        for lic in created_licensed:
            user = lic.user
            adesion, _ = PlanAdesion.objects.get_or_create(
                plan=plan,
                licensed=user,
                defaults={
                    'ind_payment_status': 'confirmed',
                    'typ_payment': 'pix',
                    'dtt_payment': paid_at,
                }
            )
            if adesion.ind_payment_status != 'confirmed':
                adesion.ind_payment_status = 'confirmed'
                adesion.typ_payment = 'pix'
                adesion.dtt_payment = paid_at
                adesion.save(update_fields=['ind_payment_status', 'typ_payment', 'dtt_payment'])

        self.stdout.write(self.style.SUCCESS("Adesões confirmadas."))

        # 5) Liberação do saldo (converte bloqueado -> disponível)
        for lic in created_licensed:
            va, _ = VirtualAccount.objects.get_or_create(licensed=lic, defaults={'name_licensed': lic.user.username})
            txs = Transaction.objects.filter(virtual_account=va, status='blocked', operation='credit')
            for tx in txs:
                # libera
                tx.status = 'released'
                tx.save(update_fields=['status'])
                va.balance_blocked = (va.balance_blocked or Decimal('0')) - tx.amount
                va.balance_available = (va.balance_available or Decimal('0')) + tx.amount
                va.save(update_fields=['balance_blocked', 'balance_available', 'dtt_update'])

        self.stdout.write(self.style.SUCCESS("Saldos liberados para saque."))

        # 6) Conta bancária de teste para o primeiro direto do raiz
        if len(created_licensed) > 1:
            test_lic = created_licensed[1]
            BankAccount.objects.get_or_create(
                licensed=test_lic,
                defaults={
                    'owner_type': 'pf',
                    'bank_code': '756',
                    'bank_name': 'Sicoob',
                    'account_type': 'corrente',
                    'agency_number': '0001',
                    'agency_digit': '0',
                    'account_number': '123456',
                    'account_digit': '0',
                    'account_holder_name': test_lic.user.username,
                    'account_holder_cpf_cnpj': test_lic.cpf_cnpj,
                    'is_default': True,
                }
            )

        self.stdout.write(self.style.SUCCESS("Seed concluído. Você pode testar saques e evolução de carreira manualmente."))


