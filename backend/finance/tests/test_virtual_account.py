from django.test import TestCase
from django.utils import timezone

from core.models.User import User
from core.models.Licensed import Licensed
from plans.models import Plan, PlanAdesion
from finance.models import VirtualAccount, VirtualAccountTransaction

# execute python manage.py test finance para testar
# ou python manage.py test finance.tests.test_virtual_account.VirtualAccountTestCase

class VirtualAccountTestCase(TestCase):

    def setUp(self):
        # Usuário + Licenciado
        self.user = User.objects.create_user(username="licenciado1", password="1234")
        self.licensed = Licensed.objects.create(user=self.user, cpf_cnpj="12345678901")

        # Plano
        self.plan = Plan.objects.create(
            name="Plano Teste",
            price=300.00,
            points=300,
            bonus_level_1=50.00
        )

    def test_virtual_account_transaction_created(self):
        # Antes: virtual account não existe
        self.assertFalse(hasattr(self.licensed, 'virtual_account'))

        # Simula pagamento confirmado
        adesion = PlanAdesion.objects.create(
            plan=self.plan,
            licensed=self.user,
            ind_payment_status='confirmed'
        )

        # Recarrega licenciado e conta virtual
        self.licensed.refresh_from_db()
        virtual_account = VirtualAccount.objects.get(licensed=self.licensed)

        # Verifica se conta virtual criada
        self.assertIsNotNone(virtual_account)

        # Verifica saldo bloqueado atualizado
        self.assertEqual(virtual_account.blocked_balance, self.plan.bonus_level_1)

        # Verifica transação criada
        transaction = VirtualAccountTransaction.objects.filter(virtual_account=virtual_account).first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.status, 'blocked')
        self.assertEqual(transaction.operation, 'credit')
        self.assertTrue(transaction.is_processed)
