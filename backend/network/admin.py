from django.contrib import admin
from .models import UnilevelNetwork, LicensedPoints

@admin.register(UnilevelNetwork)
class UnilevelNetworkAdmin(admin.ModelAdmin):
    list_display = ('upline_licensed', 'downline_licensed', 'level', 'dtt_record')
    search_fields = ('upline_licensed__user__username', 'downline_licensed__user__username')
   # list_filter = ('level')
    readonly_fields = ('dtt_record', 'dtt_update')

@admin.register(LicensedPoints)
class LicensedPointsAdmin(admin.ModelAdmin):
    list_display = ('licensed', 'points', 'description', 'status', 'dtt_record')
    search_fields = ('licensed__user__username', 'description', 'reference')
   # list_filter = ('status')
    #readonly_fields = ('dtt_record')