import json
import base64
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.utils.dateparse import parse_datetime
from finance.models import PaymentLink, PaymentConfig

@csrf_exempt
def pagarme_webhook(request):
    print("WEBHOOK - PAGARME ")
    print("#########################################")
    
    config = PaymentConfig.objects.filter(active=True).first()
    if not config:
        return HttpResponseForbidden("Configuração não encontrada")
    
     # 1) Checar método
    if request.method != 'POST':
        return HttpResponseBadRequest('Método não permitido')

    # 2) Tentar autenticação via X-Webhook-Token
    token_header = request.headers.get("X-Webhook-Token")
    if token_header:
        if token_header != config.webhook_token:
            return HttpResponseForbidden("Token inválido")
    else:
        # 3) Tentar autenticação via Basic Auth
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Basic "):
            return HttpResponseForbidden("Basic auth header ausente")

        try:
            b64 = auth_header.split(" ", 1)[1]
            userpass = base64.b64decode(b64).decode()
            user, passwd = userpass.split(":", 1)
        except Exception:
            return HttpResponseForbidden("Credenciais inválidas")

        if user != config.webhook_user or passwd != config.webhook_password:
            return HttpResponseForbidden("Credenciais incorretas")

    # 4) Processar payload
    try:
        event = json.loads(request.body)
    except ValueError:
        return HttpResponseBadRequest('JSON inválido')

    event_type  = event.get('type')
    data        = event.get('data', {})
    order_id    = data.get('id')  # corresponde ao `order.id`
    status      = data.get('status')  # ex: "paid", "pending", etc.
    closed_at   = data.get('closed_at')  # timestamp ISO

    print("---------------------------------")
    print("order_id: ", order_id)
    print("event_type: ", event_type)
    print("status: ", status)
    print("closed_at: ", closed_at)
    print("---------------------------------")

    # 5) Atualiza ou cria a fatura (PaymentLink)
    try:
        fatura = PaymentLink.objects.get(order_id=order_id)
        fatura.status = status
        fatura.charge_id = data.get('charge', {}).get('id') or data.get('id')
        fatura.payment_method = data.get('payment_method')
        fatura.paid_amount = str(data.get('paid_amount', '0')),
        fatura.closed_at = parse_datetime(closed_at) if closed_at else None
        fatura.response_payload = json.dumps(event)
        fatura.save(update_fields=[
            'status', 'charge_id', 'payment_method',
            'paid_amount', 'closed_at', 'response_payload'
        ])
    except PaymentLink.DoesNotExist:
        print(f"❌ Nenhuma fatura encontrada com order_id={order_id}")
        return HttpResponseBadRequest("Fatura não encontrada para este order_id")
    
    except Exception as e:
        print("❌ Erro ao salvar PaymentLink:")
        print(e)
        return HttpResponseBadRequest("Erro ao salvar PaymentLink")
    
    # 6) Aprova o pagamento se evento indicar que foi pago
    if event_type == 'order.paid':
        print("✅ Chamando fatura.approve_payment()")
        fatura.approve_payment()

    return HttpResponse('OK')
