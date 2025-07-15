# core/admin_utils.py
# Motivo desse metodo serve para evitar repetição de código e customizar a exibição de campos no grid do Django Admin.
# Ele gera funções decoradas com @admin.display que podem ser usadas diretamente no list_display do ModelAdmin.
# Essas funções podem exibir campos de relacionamentos, datas formatadas, booleanos customizados   
# e outros tipos de dados de forma mais legível e amigável.
# core/admin_utils.py
# -*- coding: utf-8 -*-

from django.contrib import admin

def display_related_field(attr, field, verbose_name):
    """
    Gera uma função @admin.display para exibir um campo de um relacionamento.
    Ex: display_related_field('user', 'username', 'Usuário')
    """
    @admin.display(description=verbose_name)
    def func(self, obj):
        rel = getattr(obj, attr, None)
        return getattr(rel, field, '-') if rel else '-'
    return func

def display_related_name(attr, verbose_name):
    """
    Gera uma função @admin.display para exibir o .name de um relacionamento.
    Ex: display_related_name('city_lookup', 'Cidade')
    """
    return display_related_field(attr, 'name', verbose_name)

def display_date(attr, verbose_name):
    """
    Gera uma função @admin.display para exibir datas formatadas.
    Ex: display_date('dtt_record', 'Cadastro')
    """
    @admin.display(description=verbose_name)
    def func(self, obj):
        dt = getattr(obj, attr, None)
        return dt.strftime('%d/%m/%Y %H:%M') if dt else '-'
    return func

def display_boolean(attr, verbose_name, yes='Sim', no='Não'):
    """
    Gera uma função @admin.display para exibir booleanos customizados.
    """
    @admin.display(description=verbose_name)
    def func(self, obj):
        val = getattr(obj, attr, False)
        return yes if val else no
    return func
