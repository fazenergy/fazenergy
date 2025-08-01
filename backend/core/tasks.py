# core/tasks.py
from celery import shared_task
from core.models.Licensed import Licensed

@shared_task
def verificar_plano_de_carreira_task(licensed_id):
    from django.db import connection
    connection.close()  # fecha conexão reaproveitada, padrão Celery
    af = Licensed.objects.get(id=licensed_id)
    af.verificar_plano_de_carreira()
