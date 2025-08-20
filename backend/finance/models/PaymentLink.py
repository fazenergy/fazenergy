from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models.Licensed import Licensed  # ajuste para o seu app
# Generic relations para ScoreReference
from django.contrib.contenttypes.models import ContentType
#from products.models import Product  # ou onde estiver o seu model de produto

# ########################################################################################
# PaymentGateway e PaymentStatus - Dicionarios de options para gateways e status de pagamento
# ########################################################################################
class PaymentGateway(models.TextChoices):
    PAGARME = 'pagarme', 'Pagarme'
    PAGSEGURO = 'pagseguro', 'PagSeguro'

class PaymentStatus(models.TextChoices):
    PENDING     = 'pending', _('Pending')
    PAID        = 'paid', _('Paid')
    AUTHORIZED  = 'authorized', _('Authorized')
    CANCELED    = 'canceled', _('Canceled')
    FAILED      = 'failed', _('Failed')
    REFUNDED    = 'refunded', _('Refunded')

# deixando fixo por enquanto, depois pode ser dinâmico com fk
class Product(models.TextChoices):
    ADESION = 'Adesão Anual', _('Plano de Adesão Anual'),
    USINA   = 'Usina Fotovoltaica', _('Usina Fotovoltaica')


# ########################################################################################
# TABELA: PAYMENTLINK - Define o modelo PaymentLink, nome claro e direto.
# ########################################################################################
class PaymentLink(models.Model):
    class Meta:
        db_table = 'PaymentLink'
        verbose_name = _('Link de Cobrança')
        verbose_name_plural = _('Links de Cobranças')

    licensed = models.ForeignKey(
        Licensed, on_delete=models.CASCADE, related_name='payment_links', null=True, blank=True
    )

    # criei essa fk só pra garantir que o link de pagamento esteja associado a uma adesão
    adesion = models.ForeignKey(
        'plans.PlanAdesion',
        on_delete=models.CASCADE,
        related_name='payment_links',
        null=True,  # se true, flexível para outros tipos de pagamento
        blank=True
    )

    product         = models.CharField(_('Product'), max_length=50, choices=Product.choices, default=Product.ADESION)   

#   futuramente quando virar loja virtual, talvez seja necessário:  product = models.ForeignKey( Product, on_delete=models.CASCADE, related_name='payment_links'  )
    gateway         = models.CharField(_('Gateway'),max_length=50, choices=PaymentGateway.choices, default=PaymentGateway.PAGARME
    )
    order_id        = models.CharField(_('Order ID'), max_length=256, blank=True, null=True)
    code            = models.CharField(_(u'Code'), max_length=256, null=True, blank=True)
    charge_id       = models.CharField(_('Charge ID'), max_length=256, blank=True, null=True)
    payment_method  = models.CharField(_('Payment Method'), max_length=50, blank=True, null=True)

    amount          = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    paid_amount     = models.DecimalField(_('Paid Amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    installments    = models.PositiveSmallIntegerField(_('Installments'), blank=True, null=True)

    status          = models.CharField(_('Status'), max_length=50, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    url             = models.URLField(_('Payment Link URL'), max_length=512, blank=True, null=True)
    barcode         = models.CharField(_('Barcode'), max_length=256, blank=True, null=True)
    qrcode          = models.CharField(_('QR Code'), max_length=512, blank=True, null=True)

    request_payload = models.TextField(_('Request Payload'), blank=True, null=True)
    response_payload = models.TextField(_('Response Payload'), blank=True, null=True)
    observation      = models.CharField(_('Observação'), max_length=255, blank=True, null=True)

    is_captured     = models.BooleanField(_('Captured?'), default=False)
    is_canceled     = models.BooleanField(_('Canceled?'), default=False)

    created_at      = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at      = models.DateTimeField(_('Updated At'), auto_now=True)
    closed_at       = models.DateTimeField(_('Closed At'), blank=True, null=True)
    canceled_at     = models.DateTimeField(_('Canceled At'), blank=True, null=True)

    def __str__(self):
        return f'PaymentLink {self.order_id or self.pk}'

    def approve_payment(self):
        """Aprova pagamento se status for pago/autorizado."""
        print("Chamando approve_payment")

        if self.status in [PaymentStatus.PAID, PaymentStatus.AUTHORIZED] and not self.is_captured:
            print("✅ Pagamento será aprovado...")

            self.is_captured = True
            if not self.closed_at:
                self.closed_at = timezone.now()
            self.save(update_fields=['is_captured', 'closed_at'])

            if self.adesion:
                # Sincroniza com PlanAdesion (status textual do app)
                adesion = self.adesion
                try:
                    # Campos compatíveis com o modelo PlanAdesion atual
                    adesion.ind_payment_status = 'confirmed'
                    adesion.dtt_payment = self.closed_at
                    # mapeia método do gateway para choices do PlanAdesion
                    method_map = {'credit_card': 'creditCard', 'pix': 'pix', 'boleto': 'money'}
                    adesion.typ_payment = method_map.get(self.payment_method, adesion.typ_payment)
                    adesion.save(update_fields=['ind_payment_status', 'dtt_payment', 'typ_payment'])
                except Exception as e:
                    print(f"Aviso: não foi possível sincronizar PlanAdesion: {e}")

                # Atualiza licenciado (modelo core.Licensed)
                try:
                    licensed = Licensed.objects.get(user=adesion.licensed)
                    licensed.dtt_payment_received = self.closed_at
                    licensed.is_in_network = True if licensed.is_in_network is False else licensed.is_in_network
                    licensed.save(update_fields=['dtt_payment_received', 'is_in_network'])
                except Exception as e:
                    print(f"Aviso: não foi possível atualizar Licensed: {e}")

                # Garante criação na Unilevel e pontos (idempotente)
                try:
                    from network.models import UnilevelNetwork, ScoreReference
                    from decimal import Decimal

                    # Unilevel (nível 1..5)
                    if licensed.original_indicator:
                        current = licensed.original_indicator
                        lvl = 1
                        while current and lvl <= 5:
                            UnilevelNetwork.objects.get_or_create(
                                upline_licensed=current,
                                downline_licensed=licensed,
                                level=lvl,
                            )
                            current = current.original_indicator
                            lvl += 1

                    # Pontos de adesão via ScoreReference (idempotente por origem + recebedor)
                    ct = ContentType.objects.get(app_label='plans', model='planadesion')
                    ScoreReference.objects.get_or_create(
                        receiver_licensed=licensed,
                        content_type=ct,
                        object_id=adesion.id,
                        defaults={
                            'points_amount': int(adesion.plan.points),
                            'status': 'valid',
                            'triggering_licensed': licensed,
                        }
                    )
                    # Marca flag na adesão
                    try:
                        from plans.models import PlanAdesion as PA
                        PA.objects.filter(pk=adesion.pk, points_generated=False).update(points_generated=True)
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Aviso: não foi possível garantir Unilevel/Pontos: {e}")

            else:
                print("Sem adesão vinculada a este PaymentLink.")

        else:
            print("Pagamento já estava aprovado ou status não é válido.")
