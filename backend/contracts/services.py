# contracts/services.py (regras do domínio)
from django.shortcuts import get_object_or_404
from contracts.utils import doc_to_pdf_base64
from core.models.User import User
from core.models.Licensed import Licensed

import requests
from contracts.models import ContractConfig, ContractLog, ContractTemplate

def send_doc_lexio_api(filename, base_document, signers, resumo, send_email=True, order_by=False):
    config = ContractConfig.objects.first()
    if not config:
        raise ValueError("Configuração da API Lexio não encontrada!")

    url = config.lexio_url
    token = config.lexio_token

    headers = {
        "Authorization": f"Bearer {token}",
        "lexiotoken": token,
        "Content-Type": "application/json",
    }

    payload = {
        "document": {
            "filename": filename,
            "base_document": f"data:application/pdf;base64,{base_document}",
            "signers": signers,
            "resumo": resumo,
            "send_email": send_email,
            "order_by": order_by,
        }
    }

    resp = requests.post(url, headers=headers, json=payload)
    resp.raise_for_status()
    doc = resp.json().get("document", {})
    return {
        "document_token": doc.get("document_token"),
        "status": doc.get("status"),
    }



def send_doc_adesion_to_lexio(pk: int) -> dict:
    licensed = get_object_or_404(Licensed, pk=pk)
    userLicensed = get_object_or_404(User, pk=licensed.user.pk)

    plan = licensed.plan
    if not plan:
        raise ValueError("Licenciado não possui um plano cadastrado.")

    template = plan.contract_template
    if not template:
        raise ValueError("Plano não possui um contrato vinculado.")

    contrato_b64 = doc_to_pdf_base64(pk, template_name=template.name)

    config = ContractConfig.objects.first()
    if not config:
        raise ValueError("Configuração da API Lexio não encontrada!")

    # Monta os signatários
    signers = [
        {
            "completed_name": config.signer_name_partner,
            "email": config.signer_mail_partner,
            "function": "Parte da Empresa",
        },
        {
            "completed_name": config.signer_name_testmon,
            "email": config.signer_mail_testmon,
            "function": "Testemunha",
        },
        {
            "completed_name": userLicensed.get_full_name(),
            "email": userLicensed.email,
            "function": "Representante legal", # que seria a parte contratada no caso
        },
    ]

    result = send_doc_lexio_api(
        filename=f"Contrato de Adesao_{pk}",
        base_document=contrato_b64,
        signers=signers,
        resumo=f"Contrato de Adesão MMN - Faz Energy - Cliente {pk}",
    )

    ContractLog.objects.create(
        licensed=licensed,
        contract_template=template,
        document_token=result.get("document_token"),
        status=result.get("status"),
    )

    return result

