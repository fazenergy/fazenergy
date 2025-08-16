from django.contrib import admin
from .models import Prospect, Proposal, ProposalResult


@admin.register(Prospect)
class ProspectAdmin(admin.ModelAdmin):
    list_display = ('id', 'lead_name', 'email', 'cellphone', 'licensed', 'status', 'dtt_record')
    search_fields = ('lead_name', 'email', 'cellphone', 'reference_code')
    list_filter = ('status', 'person_type', 'dtt_record')
    readonly_fields = ('dtt_record', 'dtt_update')
    autocomplete_fields = ('licensed',)


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'prospect', 'product', 'reference_code', 'city', 'state', 'status', 'dtt_record')
    search_fields = ('reference_code', 'city', 'state', 'prospect__lead_name', 'product__name')
    list_filter = ('status', 'state', 'dtt_record')
    readonly_fields = ('dtt_record', 'dtt_update')
    autocomplete_fields = ('prospect', 'product')


@admin.register(ProposalResult)
class ProposalResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'proposal', 'contract_type', 'total_installments', 'total_amount', 'status', 'dtt_record')
    search_fields = ('proposal__reference_code', 'contract_type')
    list_filter = ('status', 'dtt_record')
    readonly_fields = ('dtt_record',)
    autocomplete_fields = ('proposal',)
