# core/tasks.py
from celery import shared_task
from core.models import Affiliate

@shared_task
def verificar_plano_de_carreira_task(affiliate_id):
    from django.db import connection
    connection.close()  # fecha conexão reaproveitada, padrão Celery
    af = Affiliate.objects.get(id=affiliate_id)
    af.verificar_plano_de_carreira()
