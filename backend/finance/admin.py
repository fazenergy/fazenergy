# finance/admin.py
from django.contrib import admin
from .models import VirtualAccount, VirtualAccountTransaction

@admin.register(VirtualAccount)
class VirtualAccountAdmin(admin.ModelAdmin):
    list_display = ('id','affiliate', 'name_affiliate', 'balance_available', 'balance_blocked', 'dtt_record', 'dtt_update') # grid de exibição
    search_fields = ('name_affiliate', 'affiliate__user__username')
    readonly_fields = ('dtt_record', 'dtt_update')
    

@admin.register(VirtualAccountTransaction)
class VirtualAccountTransactionAdmin(admin.ModelAdmin):
    list_display = ('virtual_account', 'product', 'operation', 'amount', 'status', 'is_processed', 'reference_date', 'dtt_record')
    search_fields = ('virtual_account__name_affiliate', 'product', 'description')
    list_filter = ('status', 'operation', 'is_processed', 'reference_date')
    readonly_fields = ('dtt_record',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('virtual_account')