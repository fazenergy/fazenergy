#contracts/utils.py  (gera PDF em base64)
import io,base64
from django.template import Template, Context
#from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from core.models import Affiliate, User
from xhtml2pdf import pisa

# MAPA DE CHAVES MAGICAS PARA USAR NO EDITOR DE TEXTO DO TEMPLATE
def get_affiliate_mapping(affiliate):
    return {
        'id': affiliate.id,
        'nome': getattr(affiliate, 'nome', ''),
        'cpf_cnpj': affiliate.cpf_cnpj,
        'address': affiliate.address,
        'email': affiliate.user.email,
        'phone': affiliate.phone,
        'status': affiliate.status, 
        'created_at': affiliate.created_at.isoformat() if affiliate.created_at else None,
        'updated_at': affiliate.updated_at.isoformat() if affiliate.updated_at else None,
        'user': {
            'id': affiliate.user.id,
            'username': affiliate.user.username,
            'first_name': affiliate.user.first_name,
            'last_name': affiliate.user.last_name,
            'email': affiliate.user.email,
            'is_active': affiliate.user.is_active,
            'is_staff': affiliate.user.is_staff,
        }   
    }


def doc_to_pdf_base64(pk: int, template_name: str) -> str:
    affiliate = get_object_or_404(Affiliate, pk=pk)
    userAffiliate = get_object_or_404(User, pk=affiliate.user.pk)

    from contracts.models import ContractTemplate
    template = get_object_or_404(ContractTemplate, name=template_name)

    tpl = Template(template.body)
    ctx = Context({
        'affiliate': affiliate,
        'user': userAffiliate,
        'site_url': 'https://www.fazenergy.com.br',
    })
    html = tpl.render(ctx)

    buffer = io.BytesIO()
    pisa_status = pisa.CreatePDF(src=html, dest=buffer)
    if pisa_status.err:
        raise Exception('Erro ao gerar PDF')

    pdf_bytes = buffer.getvalue()
    return base64.b64encode(pdf_bytes).decode('ascii')

