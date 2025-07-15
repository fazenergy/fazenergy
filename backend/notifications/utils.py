from django.core.exceptions import ObjectDoesNotExist
from notifications.models import EmailConfig, NotificationTemplate
import smtplib
from email.mime.text import MIMEText

def send_email(notification_name, context, recipients):
    """
    Busca config e template no banco e dispara.
    """
    try:
        email_config = EmailConfig.objects.first()
        template = NotificationTemplate.objects.get(name=notification_name)
    except ObjectDoesNotExist:
        print("Configuração ou template não encontrados!")
        return

    subject = template.subject.format(**context)
    body = template.body.format(**context)

    msg = MIMEText(body, "html", "utf-8")  # isso manda como text/html UTF-8
    msg['Subject'] = subject
    msg['From'] = email_config.default_from_email
    msg['To'] = ', '.join(recipients)

    # teste direto
    # sender = 'faz.energy.aws@gmail.com'
    # password = 'seaz ovkn wavt wpwo'
    # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
    #    smtp_server.login(sender, password)
    #    smtp_server.sendmail(sender, recipients, msg.as_string())
    # print("Mensagem enviada!")

    #Trava para não misturar SSL/TLS
    if email_config.use_ssl and email_config.use_tls:
        raise ValueError("Não use SSL e TLS ao mesmo tempo!")

    smtp_class = smtplib.SMTP_SSL if email_config.use_ssl else smtplib.SMTP

    with smtp_class(email_config.smtp_host, email_config.smtp_port) as smtp_server:
        if email_config.use_tls:
            smtp_server.starttls()
        smtp_server.login(
            email_config.smtp_user.strip(),
            email_config.smtp_password.strip()
        )
        smtp_server.sendmail(email_config.default_from_email, recipients, msg.as_string())

    print("Mensagem enviada!")
