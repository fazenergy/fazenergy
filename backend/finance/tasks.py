from datetime import datetime

from celery import shared_task
from django.utils import timezone

from finance.models import WithdrawRequest, WithdrawRequestLog
from finance.services.withdraw import process_withdraw_request
from django.conf import settings
from core.models.ScheduledTaskConfig import ScheduledTaskConfig


@shared_task(bind=True, max_retries=0)
def process_scheduled_withdraws(self):
    """Tarefa periódica: processa solicitações com status 'scheduled' e horário vencido.

    Deve ser agendada diariamente (ou mais frequente) via Celery Beat.
    """
    # Respeita flag ativa (se existir config)
    try:
        cfg = ScheduledTaskConfig.objects.filter(key='finance.process_scheduled_withdraws_daily').first()
        if cfg and cfg.active is False:
            return {'ok': False, 'disabled': True, 'reason': cfg.disabled_reason}
    except Exception:
        pass

    now = timezone.now()
    qs = WithdrawRequest.objects.filter(status='scheduled', scheduled_for__lte=now)
    for req in qs.select_related('licensed'):
        try:
            WithdrawRequestLog.objects.create(
                withdraw_request=req,
                action='processing',
                note=f'Processamento automático agendado em {now.isoformat()}',
            )
        except Exception:
            pass
        result = process_withdraw_request(req, actor_username='celery', bypass_window=True)
        # Logs adicionais já são criados no serviço
    return {'ok': True, 'processed': qs.count()}


