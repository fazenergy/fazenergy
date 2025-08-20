from django.contrib import admin
from .models import UnilevelNetwork, Product, ScoreReference

@admin.register(UnilevelNetwork)
class UnilevelNetworkAdmin(admin.ModelAdmin):
    list_display = ('upline_licensed', 'downline_licensed', 'level', 'dtt_record')
    search_fields = ('upline_licensed__user__username', 'downline_licensed__user__username')
   # list_filter = ('level')
    readonly_fields = ('dtt_record', 'dtt_update')



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'dtt_record', 'dtt_update')
    search_fields = ('name',)
    list_filter = ('dtt_record',)
    readonly_fields = ('dtt_record', 'dtt_update')


@admin.register(ScoreReference)
class ScoreReferenceAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'points_amount', 'status', 'receiver_licensed', 'triggering_licensed',
        'content_type', 'object_id', 'created_at'
    )
    search_fields = (
        'receiver_licensed__user__username',
        'triggering_licensed__user__username',
        'object_id',
    )
    list_filter = ('status', 'content_type', 'created_at')
    readonly_fields = ('created_at', 'updated_at')