from decimal import Decimal
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from core.models import Affiliate  # ajuste para o seu app
#from products.models import Product  # ou onde estiver o seu model de produto

# Choices de Gateways
class PaymentGateway(models.TextChoices):
    PAGARME = 'pagarme', 'Pagarme'
    PAGSEGURO = 'pagseguro', 'PagSeguro'

# Choices para status de pagamento
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

class PaymentLink(models.Model):
    class Meta:
        verbose_name = _('Link de Cobrança')
        verbose_name_plural = _('Links de Cobranças')

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name='payment_links'
    )

    # criei essa fk só pra garantir que o link de pagamento esteja associado a uma adesão
    adesion = models.ForeignKey(
        'plans.PlanAdesion',
        on_delete=models.CASCADE,
        related_name='payment_links',
        null=True,  # se true, flexível para outros tipos de pagamento
        blank=True
    )

    product = models.CharField(_('Product'), max_length=50, choices=Product.choices, default=Product.ADESION)   

#   futuramente quando virar loja virtual, talvez seja necessário:  product = models.ForeignKey( Product, on_delete=models.CASCADE, related_name='payment_links'  )
    gateway = models.CharField(_('Gateway'),max_length=50, choices=PaymentGateway.choices, default=PaymentGateway.PAGARME
    )
    order_id = models.CharField(_('Order ID'), max_length=256, blank=True, null=True)
    charge_id = models.CharField(_('Charge ID'), max_length=256, blank=True, null=True)
    payment_method = models.CharField(_('Payment Method'), max_length=50, blank=True, null=True)

    amount = models.DecimalField(_('Amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    paid_amount = models.DecimalField(_('Paid Amount'), max_digits=10, decimal_places=2, blank=True, null=True)
    installments = models.PositiveSmallIntegerField(_('Installments'), blank=True, null=True)

    status = models.CharField(_('Status'), max_length=50, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)

    url = models.URLField(_('Payment Link URL'), max_length=512, blank=True, null=True)
    barcode = models.CharField(_('Barcode'), max_length=256, blank=True, null=True)
    qrcode = models.CharField(_('QR Code'), max_length=512, blank=True, null=True)

    request_payload = models.TextField(_('Request Payload'), blank=True, null=True)
    response_payload = models.TextField(_('Response Payload'), blank=True, null=True)

    is_captured = models.BooleanField(_('Captured?'), default=False)
    is_canceled = models.BooleanField(_('Canceled?'), default=False)

    created_at = models.DateTimeField(_('Created At'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated At'), auto_now=True)
    closed_at = models.DateTimeField(_('Closed At'), blank=True, null=True)
    canceled_at = models.DateTimeField(_('Canceled At'), blank=True, null=True)

    def __str__(self):
        return f'PaymentLink {self.order_id or self.pk}'

    def approve_payment(self):
        """Aprova pagamento se status for pago/autorizado."""
        if self.status in [PaymentStatus.PAID, PaymentStatus.AUTHORIZED] and not self.is_captured:
            self.is_captured = True
            self.closed_at = timezone.now()
            self.save(update_fields=['is_captured', 'closed_at'])
            # Aqui pode adicionar lógica para atualizar o afiliado/plano.
