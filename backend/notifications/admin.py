from django.contrib import admin, messages
from django.urls import path
from django.shortcuts import redirect
from notifications.models.NotifyConfig import NotifyConfig
from notifications.models.NotifyTemplate import NotifyTemplate
from notifications.utils import send_email
from django.utils.html import format_html


@admin.register(NotifyConfig)
class NotifyConfigAdmin(admin.ModelAdmin):
    list_display = ('smtp_host', 'smtp_port', 'smtp_user', 'use_ssl', 'use_tls')
    list_editable = ('use_ssl', 'use_tls')
    fieldsets = (
        (None, {
            'fields': ('smtp_host', 'smtp_port', 'smtp_user', 'smtp_password')
        }),
        ('Opções de Segurança', {
            'fields': ('use_ssl', 'use_tls')
        }),
        ('Outros', {
            'fields': ('default_from_email','test_recipient')
        }),
    )


@admin.register(NotifyTemplate)
class NotifyTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'active', 'test_send_link')
    list_filter = ('active',)
    search_fields = ('name', 'subject')
    fieldsets = (
        (None, {
            'fields': ('name', 'active')
        }),
        ('Conteúdo do E-mail', {
            'fields': ('subject', 'body')
        }),
    )
    # adicionei isso só pra testarmos o envio de email
    actions = ['test_send']


    # AQUI PRA BAIXO É SÓ FIRULA, IMPORTANTE É O QUE ESTÁ ACIMA
    #####################################################################################################################
    # Inclui rota custom pra /<pk>/test/
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:pk>/test/', self.admin_site.admin_view(self.test_template), name='notificationtemplate-test'),
        ]
        return custom_urls + urls

    def test_send_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Testar Envio</a>',
            f'{obj.pk}/test/'
        )
    test_send_link.short_description = 'Testar'
    test_send_link.allow_tags = True

    def test_template(self, request, pk):
        template = NotifyTemplate.objects.get(pk=pk)

        config = NotifyConfig.objects.first()
        recipient = config.test_recipient if config and config.test_recipient else None

        if not recipient:
            self.message_user(request, "Destinatário de teste não configurado!", messages.ERROR)
            return redirect('/admin/notifications/notificationtemplate/')

        context = {
            "nome": "Teste",
            "id": "USR001",
            "nova_senha": "abc123",
            "site_url": "https://faz.energy",
        }

        send_email(template.name, context, [recipient])
        self.message_user(request, f"E-mail de teste enviado para {recipient}.", messages.SUCCESS)
        return redirect('/admin/notifications/notificationtemplate/')