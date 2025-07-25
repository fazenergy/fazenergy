from django.db import models

class EmailConfig(models.Model):
    smtp_host = models.CharField(max_length=255, verbose_name="Servidor SMTP")
    smtp_port = models.PositiveIntegerField(default=465, verbose_name="Porta SMTP")
    smtp_user = models.EmailField(verbose_name="Usuário SMTP")
    smtp_password = models.CharField(max_length=255, verbose_name="Senha APP")
    use_tls = models.BooleanField(default=False, verbose_name="Usar TLS?")
    use_ssl = models.BooleanField(default=True, verbose_name="Usar SSL?")
    default_from_email = models.EmailField(verbose_name="Remetente Padrão")
    test_recipient = models.EmailField(
        blank=True, null=True,
        verbose_name="Destinatário de Teste",
        help_text="E-mail para receber os envios de teste."
    )

    class Meta:
        db_table = 'tb_NotifyEmailConfig'
        verbose_name = "Configuração de E-mail"
        verbose_name_plural = "Configurações de E-mail"

    def __str__(self):
        return f"{self.smtp_user} ({self.smtp_host}:{self.smtp_port})"


    


 


# COMO USAR:

# from django.core.exceptions import ObjectDoesNotExist
# from .models import EmailConfig, NotificationTemplate
# import smtplib
# from email.mime.text import MIMEText

# def send_email(notification_name, context, recipients):
#     """
#     Envia o e-mail com base em um template salvo no banco.
#     `context` é um dict para substituir variáveis.
#     """
#     try:
#         email_config = EmailConfig.objects.first()
#         template = NotificationTemplate.objects.get(name=notification_name)
#     except ObjectDoesNotExist:
#         print("Configuração ou template não encontrados!")
#         return

#     # Renderiza variáveis simples usando str.format
#     subject = template.subject.format(**context)
#     body = template.body.format(**context)

#     msg = MIMEText(body)
#     msg['Subject'] = subject
#     msg['From'] = email_config.default_from_email
#     msg['To'] = ', '.join(recipients)

#     if email_config.use_ssl:
#         smtp_class = smtplib.SMTP_SSL
#     else:
#         smtp_class = smtplib.SMTP

#     with smtp_class(email_config.smtp_host, email_config.smtp_port) as smtp_server:
#         if email_config.use_tls:
#             smtp_server.starttls()
#         smtp_server.login(email_config.smtp_user, email_config.smtp_password)
#         smtp_server.sendmail(email_config.default_from_email, recipients, msg.as_string())

#     print("Mensagem enviada!")

# def recuperar_user_pass(distribuidor):
#     from .functions import gen_pass
#     nova_senha = gen_pass()

#     # Atualiza a senha
#     distribuidor.user.set_password(nova_senha)
#     distribuidor.user.save()

#     context = {
#         "nome": distribuidor.nome,
#         "id": distribuidor.user.username,
#         "nova_senha": nova_senha,
#         "site_url": "www.fazenergy.com.br",
#     }

#     send_email("Recuperar Senha", context, [distribuidor.email])



# Como usar variáveis nos Templates
# Olá {nome}!
# Sua nova senha é: {nova_senha}
# Site: {site_url}
