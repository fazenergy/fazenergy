# finance/services/CreatePaymentLink.py
# É um "serviço" que cria link de pagamento no gateway.
import base64
import requests 
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta
import json

def create_payment_link(plan_adesion):
    from backend.finance.models.PaymentLink import PaymentLink
    from backend.finance.models.GatewayConfig import PaymentConfig
    """
        Service: gera PaymentLink para a PlanAdesion recebida.
    """
    print("Criando Payment Link — via Payment Links API")

    time_threshold = timezone.now() - timedelta(hours=1)
    if plan_adesion.payment_links.filter(created_at__gte=time_threshold).exists():
        payment_link = plan_adesion.payment_links.filter(
            created_at__gte=time_threshold
        ).last()
        return payment_link, None

    buyer = plan_adesion.licensed # cliente comprador
    buyer_name = f"{buyer.first_name} {buyer.last_name}".strip() #nome completo do comprador
    amount = int(plan_adesion.plan.price * 100) # valor do plano
    code = f"PLAN-ADES-{plan_adesion.id}"

    # parcelas
    installments_setup = {
        "amount": amount,
        "interest_type": "Simple",
        "interest_rate": 11.86,
        "max_installments": 10,
        "free_installments": 10
    }

    # payload
    payload = {
        "name": f"Pedido {code}",
        "layout_settings": {
            "image_url": "https://app.faz.energy/static/empresa/logo.png"
        },
        "type": "order",
        "payment_settings": {
            "accepted_payment_methods": ["credit_card", "boleto", "pix"],
            "statement_descriptor": code,
            "credit_card_settings": {
                "operation_type": "auth_and_capture",
                "installments_setup": installments_setup
            },
            "boleto_settings": {
                "instructions": "Sr. Caixa, favor não aceitar após o vencimento",
                "due_in": 7 * 24 * 3600
            },
            "pix_settings": {
                "expires_in": 3600,
                "additional_information": [
                    {"name": "Pedido", "value": code}
                ]
            }
        },
        "cart_settings": {
            "items": [
                {
                    "name": plan_adesion.plan.name, # Nome do plano de adesão
                    "amount": amount,
                    "default_quantity": 1
                }
            ]
        },
        "expires_in": 86400,
    }

    # Busca config ativa
    config = PaymentConfig.objects.filter(active=True).first()
    if not config:
        raise ValueError("Nenhuma configuração de pagamento ativa encontrada.")

    url = config.api_url
    token = config.api_token

    payload["redirect_url"] = config.redirect_url
    payload["postback_url"] = config.postback_url

    basic = base64.b64encode(f"{token}:".encode()).decode()
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {basic}"
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=10)

        print("Status Code:", resp.status_code)
        print("Payload Enviado:", json.dumps(payload, indent=2))

        print("Criando Payment Link no Pagar.me...")
        print("URL:", url)
        print("Headers:", headers)
        print("Payload:", json.dumps(payload, indent=2))

        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("Status:", resp.status_code)
            print("Response body:", resp.text)
            raise

        data = resp.json()
        print("Resposta do Pagar.me:", json.dumps(data, indent=2))

        from backend.core.models.Licensed import Licensed
        licensed = Licensed.objects.get(user=plan_adesion.licensed)

        payment_link = PaymentLink(
                adesion=plan_adesion, 
                 licensed=licensed,
                gateway='pagarme'
                )
        payment_link.request_payload = payload
        payment_link.response_payload  = data
        payment_link.order_id = data.get("id")
        payment_link.code = data.get("code") # code de controle pra quando webhook chamar
        payment_link.url = data.get("url")
        payment_link.status = data.get("status")
        payment_link.amount = data.get("amount", amount)
        payment_link.installments = installments_setup["max_installments"]
        payment_link.created_at = timezone.now()
        payment_link.updated_at = timezone.now()
        payment_link.closed_at = None
        #payment_link.splited = False
        payment_link.save()

        print("✅ Payment Link criado:", data)
        return [payment_link, None]

    except Exception as e:
        print("Erro geral ao criar Payment Link:", str(e))
        return None, e