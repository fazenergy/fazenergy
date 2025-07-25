
from django.db import models
from django_ckeditor_5.fields import CKEditor5Field


class NotificationTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Notificação")
    subject = models.CharField(max_length=255, verbose_name="Assunto do E-mail")
    body = CKEditor5Field(verbose_name="Corpo do E-mail")
    active = models.BooleanField(default=True, verbose_name="Ativo?")

    class Meta:
        db_table = 'tb_NotifyConfigTemplate'
        verbose_name = "Template de Notificação"
        verbose_name_plural = "Templates de Notificação"

    def __str__(self):
        return self.name