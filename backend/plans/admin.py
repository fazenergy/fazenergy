# core/admin.py ou plans/admin.py
from django.contrib import admin
from .models import Plan
from .models import PlanAdesion
from .models import PlanCareer

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','contract_template', 'price', 'points', 'stt_record', 'dtt_record']
    list_filter = ['stt_record']
    search_fields = ['name']

@admin.register(PlanAdesion)
class PlanAdesionAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan', 'affiliate', 'ind_payment_status', 'typ_payment', 'is_courtesy', 'points_generated', 'ind_processing')
    search_fields = ('affiliate__username', 'plan__name')
    list_filter = ('ind_payment_status', 'typ_payment', 'ind_processing')


@admin.register(PlanCareer)
class PlanCareerAdmin(admin.ModelAdmin):
    list_display = (
        'id',  # Adiciona o campo ID para facilitar a identificação
        'stage_name', 'reward_description',
        'required_points', 'required_directs',
        'required_direct_sales', 'max_pml_per_line',
        'stt_record', 'dtt_record'
    )
    list_filter = ('stt_record',)
    search_fields = ('stage_name', 'reward_description')
    readonly_fields = ('dtt_record', 'dtt_update')
    ordering = ('id',)  # ASCENDENTE por padrão
    
