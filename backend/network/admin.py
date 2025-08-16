from django.contrib import admin
from .models import UnilevelNetwork, LicensedPoints, Product

@admin.register(UnilevelNetwork)
class UnilevelNetworkAdmin(admin.ModelAdmin):
    list_display = ('upline_licensed', 'downline_licensed', 'level', 'dtt_record')
    search_fields = ('upline_licensed__user__username', 'downline_licensed__user__username')
   # list_filter = ('level')
    readonly_fields = ('dtt_record', 'dtt_update')

@admin.register(LicensedPoints)
class LicensedPointsAdmin(admin.ModelAdmin):
    list_display = ('licensed', 'points', 'description', 'status', 'data_referencia_formatada', 'data_registro_formatada')
    search_fields = ('licensed__user__username', 'description', 'reference')
    list_filter = ('status', 'dtt_ref', 'dtt_record')
    readonly_fields = ('data_registro_formatada',)
    
    fields = (
        'licensed', 'description', 'points', 'reference', 'status',
        'dtt_ref', 'data_registro_formatada'
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dtt_record', 'dtt_update')
    search_fields = ('name',)
    list_filter = ('dtt_record',)
    readonly_fields = ('dtt_record', 'dtt_update')