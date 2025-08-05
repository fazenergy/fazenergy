# core/admin.py ou plans/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Plan
from .models import PlanAdesion
from .models import PlanCareer

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','contract_template', 'price', 'points', 'stt_record', 'dtt_record']
    list_filter = ['stt_record']
    search_fields = ['name']
    readonly_fields = ('usr_update', 'dtt_update', 'dtt_record')

@admin.register(PlanAdesion)
class PlanAdesionAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'licensed', 'ind_payment_status', 'typ_payment', 'is_courtesy', 'points_generated', 'ind_processing')
    search_fields = ('licensed__username', 'plan__name')
    list_filter = ('ind_payment_status', 'typ_payment', 'ind_processing')
    readonly_fields = ('dtt_update', 'dtt_record')


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
    
