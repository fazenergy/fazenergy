from django.core.exceptions import ObjectDoesNotExist
from notifications.models import NotifyConfig, NotifyTemplate
import smtplib
from email.mime.text import MIMEText

def send_email(notification_name, context, recipients):
    """
    Busca config e template no banco e dispara.
    """
    try:
        notify_config = NotifyConfig.objects.first()
        template = NotifyTemplate.objects.get(name=notification_name)
    except ObjectDoesNotExist:
        print("Configuração ou template não encontrados!")
        return

    subject = template.subject.format(**context)
    body = template.body.format(**context)

    msg = MIMEText(body, "html", "utf-8")  # isso manda como text/html UTF-8
    msg['Subject'] = subject
    msg['From'] = notify_config.default_from_email
    msg['To'] = ', '.join(recipients)

    # teste direto
    # sender = 'faz.energy.aws@gmail.com'
    # password = 'seaz ovkn wavt wpwo'
    # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
    #    smtp_server.login(sender, password)
    #    smtp_server.sendmail(sender, recipients, msg.as_string())
    # print("Mensagem enviada!")

    #Trava para não misturar SSL/TLS
    if notify_config.use_ssl and notify_config.use_tls:
        raise ValueError("Não use SSL e TLS ao mesmo tempo!")

    smtp_class = smtplib.SMTP_SSL if notify_config.use_ssl else smtplib.SMTP

    with smtp_class(notify_config.smtp_host, notify_config.smtp_port) as smtp_server:
        if notify_config.use_tls:
            smtp_server.starttls()
        smtp_server.login(
            notify_config.smtp_user.strip(),
            notify_config.smtp_password.strip()
        )
        smtp_server.sendmail(notify_config.default_from_email, recipients, msg.as_string())

    print("Mensagem enviada!")
