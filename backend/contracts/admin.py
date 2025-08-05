# contracts/admin.py
from django.contrib import admin
from .models import ContractConfig, ContractTemplate, ContractLog

@admin.register(ContractConfig)
class ContractConfigAdmin(admin.ModelAdmin):
    list_display = ('lexio_url', 'signer_name_partner', 'signer_mail_partner','signer_name_testmon', 'signer_mail_testmon', 'lexio_token')
    fieldsets = (
        (None, {
            'fields': ('lexio_url', 'lexio_token')
        }),
        ('Signatário Parte Empresa', {
            'fields': ('signer_name_partner', 'signer_mail_partner', 'signer_name_testmon', 'signer_mail_testmon')
        }),
    )

@admin.register(ContractLog)
class ContractLogAdmin(admin.ModelAdmin):
    list_display = ('licensed', 'contract_template', 'document_token', 'status', 'created_at')
    search_fields = ('licensed__cpf_cnpj', 'document_token', 'status')
    list_filter = ('status', 'created_at')
    readonly_fields = ('licensed', 'contract_template', 'document_token', 'status', 'created_at')



@admin.register(ContractTemplate)
class ContractTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'active')
    search_fields = ('name',)
    readonly_fields = ('show_mapping_info', )
    fieldsets = (
        (None, {'fields': ('name', 'description', 'active')}),
        ('Conteúdo', {'fields': ('show_mapping_info', 'body')}),
    )

    # puxa o mapeamento de chaves do template
    def show_mapping_info(self, obj):
     return obj.mapping_info or "Nenhuma instrução disponível."

    show_mapping_info.short_description = "Mapa de Chaves"
    show_mapping_info.allow_tags = True  # Para HTML (em Django moderno não é necessário, mas não faz mal)