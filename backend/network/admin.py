from django.contrib import admin
from .models import UnilevelNetwork, AffiliatePoints

@admin.register(UnilevelNetwork)
class UnilevelNetworkAdmin(admin.ModelAdmin):
    list_display = ('parent_affiliate', 'child_affiliate', 'level', 'dtt_record')
    search_fields = ('parent_affiliate__user__username', 'child_affiliate__user__username')
   # list_filter = ('level')
    readonly_fields = ('dtt_record', 'dtt_update')

@admin.register(AffiliatePoints)
class AffiliatePointsAdmin(admin.ModelAdmin):
    list_display = ('affiliate', 'points', 'description', 'status', 'dtt_record')
    search_fields = ('affiliate__user__username', 'description', 'reference')
   # list_filter = ('status')
    #readonly_fields = ('dtt_record')