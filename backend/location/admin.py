from django.contrib import admin
from .models import Country, State, City


@admin.register(Country)
class CityAdmin(admin.ModelAdmin):
    list_display = ('iso_code', 'name')
    list_filter = ('name',)

# @admin.register(State)
# class StateAdmin(admin.ModelAdmin):
#     list_display = ('name', 'uf', 'country')

# @admin.register(City)
# class CityAdmin(admin.ModelAdmin):
#     list_display = ('name', 'state')
#     list_filter = ('state',)


# TO DO: AJUSTAR DEPOIS OS FILTROS E BUSCAR PARA ESTADOS > CIDADE COM O: pip install django-autocomplete-light
# ####################################################################################


# SEARCH PAR A CIDADE E ESTADO
# #####################################################################################
@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    search_fields = ['name', 'uf', 'country__name']

@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    search_fields = ['name', 'state__uf']
    list_display = ['name', 'state']

