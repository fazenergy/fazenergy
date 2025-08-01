#contracts/utils.py  (gera PDF em base64)
import io,base64
from django.template import Template, Context
#from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from core.models.User import User
from core.models.Licensed import Licensed
from xhtml2pdf import pisa

# MAPA DE CHAVES MAGICAS PARA USAR NO EDITOR DE TEXTO DO TEMPLATE
def get_licensed_mapping(licensed):
    return {
        'id': licensed.id,
        'nome': getattr(licensed, 'nome', ''),
        'cpf_cnpj': licensed.cpf_cnpj,
        'address': licensed.address,
        'email': licensed.user.email,
        'phone': licensed.phone,
        'status': licensed.status, 
        'created_at': licensed.created_at.isoformat() if licensed.created_at else None,
        'updated_at': licensed.updated_at.isoformat() if licensed.updated_at else None,
        'user': {
            'id': licensed.user.id,
            'username': licensed.user.username,
            'first_name': licensed.user.first_name,
            'last_name': licensed.user.last_name,
            'email': licensed.user.email,
            'is_active': licensed.user.is_active,
            'is_staff': licensed.user.is_staff,
        }   
    }


def doc_to_pdf_base64(pk: int, template_name: str) -> str:
    licensed = get_object_or_404(Licensed, pk=pk)
    userLicensed = get_object_or_404(User, pk=licensed.user.pk)

    from contracts.models import ContractTemplate
    template = get_object_or_404(ContractTemplate, name=template_name)

    tpl = Template(template.body)
    ctx = Context({
        'licensed': licensed,
        'user': userLicensed,
        'site_url': 'https://faz.energy',  # ou use settings.SITE_URL
           # Adicione outras variáveis de contexto conforme necessário
    })
    html = tpl.render(ctx)

    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=buffer)
    if pisa_status.err:
        raise Exception('Erro ao gerar PDF')

    pdf_bytes = buffer.getvalue()
    return base64.b64encode(pdf_bytes).decode('ascii')

