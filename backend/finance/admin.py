# finance/admin.py
from django.contrib import admin
from .models import VirtualAccount, Transaction, PaymentLink
from .models.GatewayConfig import GatewayConfig

@admin.register(VirtualAccount)
class VirtualAccountAdmin(admin.ModelAdmin):
    list_display = ('id','licensed', 'name_licensed', 'balance_available', 'balance_blocked', 'dtt_record', 'dtt_update') # grid de exibição
    search_fields = ('name_licensed', 'licensed__user__username')
    readonly_fields = ('dtt_record', 'dtt_update')
    

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('virtual_account', 'product', 'operation', 'amount', 'status', 'is_processed', 'reference_date', 'dtt_record')
    search_fields = ('virtual_account__name_licensed', 'product', 'description')
    list_filter = ('status', 'operation', 'is_processed', 'reference_date')
    readonly_fields = ('dtt_record',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('virtual_account')
    

# RECEBIMENTO: LINKS DE PAGAMENTO PAGARME
@admin.register(PaymentLink)
class PaymentLinkAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'licensed',
        'product',
        'code',
        'amount',
        'status',
        'gateway',
        'observation',
        'is_captured',
        'is_canceled',
        'created_at',
    )
    list_filter = ('status', 'is_captured', 'is_canceled')
    search_fields = ('order_id', 'charge_id', 'licensed__user__username')  

    def save_model(self, request, obj, form, change):
        """Quando status é alterado manualmente para pago/autorizado, registra observação com o usuário."""
        was_paid = False
        if change:
            try:
                old = PaymentLink.objects.get(pk=obj.pk)
                was_paid = old.status in ('paid', 'authorized')
            except PaymentLink.DoesNotExist:
                was_paid = False
        super().save_model(request, obj, form, change)

        if obj.status in ('paid', 'authorized') and not was_paid:
            note = f"Pagamento manual via edição de link de pagamento pelo usuário {request.user.username}"
            try:
                # Anexa/define observação
                obj.observation = f"{obj.observation} | {note}" if obj.observation else note
                obj.save(update_fields=['observation'])
            except Exception:
                pass


# finance/admin.py
@admin.register(GatewayConfig)
class GatewayConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'api_url', 'dev_url_hint', 'postback_url', 'redirect_url', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'api_url', 'postback_url')

    fieldsets = (
        (None,           {'fields': ('name', 'active')}),
        ('API Settings', {'fields': ('api_token', 'api_url', 'dev_url_hint')}),
        ('URLs',         {'fields': ('postback_url', 'redirect_url')}),
        ("Webhook",      {'fields': ('webhook_token', 'webhook_user', 'webhook_password', 'webhook_secret') }),
    )

    def has_add_permission(self, request):
        """Permite só um registro se quiser forçar singleton"""
        count = GatewayConfig.objects.count()
        if count >= 1:
            return False
        return True
