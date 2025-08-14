# core/admin.py ou plans/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Plan
from .models import PlanAdesion
from .models import PlanCareer
from .models import Qualification

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','contract_template', 'price', 'points', 'stt_record', 'dtt_record']
    list_filter = ['stt_record']
    search_fields = ['name']
    readonly_fields = ('usr_update', 'dtt_update', 'dtt_record')

@admin.register(PlanAdesion)
class PlanAdesionAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'licensed', 'ind_payment_status', 'typ_payment', 'is_courtesy', 'points_generated', 'ind_processing', 'contract_status')
    search_fields = ('licensed__username', 'plan__name')
    list_filter = ('ind_payment_status', 'typ_payment', 'ind_processing', 'contract_status')
    readonly_fields = ('dtt_update', 'dtt_record', 'contract_token')
    actions = ['update_contract_fields']
    
    def update_contract_fields(self, request, queryset):
        """Action para atualizar campos de contrato baseado no ContractLog"""
        from contracts.models import ContractLog
        updated_count = 0
        
        for plan_adesion in queryset:
            try:
                contract_log = ContractLog.objects.filter(
                    licensed__user=plan_adesion.licensed
                ).order_by('-id').first()
                
                if contract_log:
                    plan_adesion.contract_status = contract_log.status
                    plan_adesion.contract_token = contract_log.document_token
                    plan_adesion.save()
                    updated_count += 1
                    
            except Exception as e:
                self.message_user(request, f"Erro ao atualizar PlanAdesion {plan_adesion.id}: {e}", level='ERROR')
        
        if updated_count > 0:
            self.message_user(request, f"{updated_count} registros atualizados com sucesso!")
        else:
            self.message_user(request, "Nenhum registro foi atualizado.", level='WARNING')
    
    update_contract_fields.short_description = "Atualizar campos de contrato"
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('plan', 'licensed', 'is_courtesy')
        }),
        ('Status de Pagamento', {
            'fields': ('ind_payment_status', 'typ_payment', 'dtt_payment', 'points_generated')
        }),
        ('Status de Processamento', {
            'fields': ('ind_processing', 'ind_bonus_status')
        }),
        ('Contrato', {
            'fields': ('contract_status', 'contract_token')
        }),
        ('Cancelamento', {
            'fields': ('des_cancel_reason', 'dtt_cancel')
        }),
        ('Timestamps', {
            'fields': ('dtt_record', 'dtt_update')
        }),
    )


@admin.register(PlanCareer)
class PlanCareerAdmin(admin.ModelAdmin):
    list_display = (
        'id',  # Adiciona o campo ID para facilitar a identificação
        'stage_name', 'reward_description',
        'required_points', 'required_directs',
        'required_direct_sales', 'pml_short',
        'stt_record', 'data_criacao_formatada'
    )
    list_filter = ('stt_record', 'dtt_record')
    search_fields = ('stage_name', 'reward_description')
    readonly_fields = ('data_criacao_formatada', 'data_atualizacao_formatada', 'dtt_update', 'dtt_record')
    
    def pml_short(self, obj):
        return format_html(
            '<span class="pml-tooltip" title="Pontos Máximos por Linha" style="cursor: help;">{}</span>',
            obj.max_pml_per_line
        )
    pml_short.short_description = 'PML'
    pml_short.admin_order_field = 'max_pml_per_line'  # Permite ordenação
    
    fields = (
        'stage_name', 'reward_description', 'cover_image',
        'required_points', 'required_directs', 'required_direct_sales', 'max_pml_per_line',
        'stt_record', 'data_criacao_formatada', 'data_atualizacao_formatada'
    )
    #ordering = ('id',)  # ASCENDENTE por padrão
    

@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'licensed', 'plan_career', 'dtt_qualification')
    list_filter = ('plan_career',)
    search_fields = ('licensed__user__username', 'plan_career__stage_name')
    autocomplete_fields = ['licensed', 'plan_career']
    
