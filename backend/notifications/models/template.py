
from django.db import models
from ckeditor.fields import RichTextField

class NotificationTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nome da Notificação")
    subject = models.CharField(max_length=255, verbose_name="Assunto do E-mail")
    body = RichTextField(verbose_name="Corpo do E-mail")
    active = models.BooleanField(default=True, verbose_name="Ativo?")

    class Meta:
        verbose_name = "Template de Notificação"
        verbose_name_plural = "Templates de Notificação"

    def __str__(self):
        return self.name