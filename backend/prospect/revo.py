import os
import re
import time
from decimal import Decimal
from datetime import datetime
import requests

from django.conf import settings
from django.utils.timezone import make_aware
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from contractor.models import Contractor as Prospect
from contractor.models import Proposal, ProposalResult, ProposalLeadActor
from contractor.serializers import ProposalSerializer, ProposalResultSerializer


REVO_BASE_URL = getattr(settings, 'REVO_BASE_URL', 'https://sandbox.revoenergia.com.br/api/partners')
REVO_TOKEN_TTL_SECONDS = int(os.getenv('REVO_TOKEN_TTL_SECONDS', '3300'))  # ~55min
_REVO_TOKEN_CACHE = {
    'token': None,
    'exp_ts': 0.0,
}


def _sanitize_digits(value: str) -> str:
    return re.sub(r'\D', '', value or '')


def _bearer_headers(token: str) -> dict:
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json',
    }


def _revo_auth_token():
    username = os.getenv('REVO_USERNAME')
    password = os.getenv('REVO_PASSWORD')
    if not username or not password:
        return None, 'Credenciais REVO não configuradas (REVO_USERNAME/REVO_PASSWORD).'

    try:
        url = f'{REVO_BASE_URL}/auth'
        resp = requests.post(url, auth=(username, password), timeout=20)
        if resp.status_code != 200:
            try:
                return None, f'Erro na autenticação REVO: {resp.status_code} {resp.text}'
            finally:
                resp.close()

        data = resp.json()
        token = (data.get('data') or [{}])[0].get('token')
        if not token:
            return None, 'Token não retornado pela REVO.'
        return token, None
    except Exception as exc:
        return None, str(exc)


def _get_revo_token_cached(force: bool = False):
    now = time.time()
    if (not force) and _REVO_TOKEN_CACHE['token'] and now < _REVO_TOKEN_CACHE['exp_ts']:
        return _REVO_TOKEN_CACHE['token'], None
    token, err = _revo_auth_token()
    if token:
        _REVO_TOKEN_CACHE['token'] = token
        _REVO_TOKEN_CACHE['exp_ts'] = now + REVO_TOKEN_TTL_SECONDS
    return token, err


def _normalize_bool_owner(owner_text: str) -> bool:
    if not owner_text:
        return False
    txt = owner_text.strip().lower()
    return txt in ('próprio', 'proprio')


def _build_lead_actors_payload(contract_person: str, owner_text: str, incoming: list, fallback: dict):
    # incoming: lista de dicts já no formato da REVO (actor, campos)
    # fallback: dados básicos (nome/email/celular/endereço) para compor contractor se necessário
    result = []
    by_actor = { (a.get('actor') or '').strip(): a for a in (incoming or []) }

    # contractor sempre
    contractor = by_actor.get('contractor')
    if not contractor:
        contractor = {
            'actor': 'contractor',
            'legal_name': fallback.get('legal_name'),
            'name': fallback.get('name'),
            'cellphone': fallback.get('cellphone'),
            'email': fallback.get('email'),
            'zip_code': fallback.get('zip_code'),
            'address': fallback.get('address'),
            'number': fallback.get('number'),
            'complement': fallback.get('complement'),
            'neighborhood': fallback.get('neighborhood'),
            'city': fallback.get('city'),
            'st': fallback.get('st'),
        }
    # regra: se PJ, exigir legal_name no contractor
    if (contract_person or '').upper() == 'PJ' and not contractor.get('legal_name'):
        return None, 'Para PJ, contractor.legal_name é obrigatório.'
    result.append(contractor)

    # legal_responsible somente PJ
    if (contract_person or '').upper() == 'PJ':
        lr = by_actor.get('legal_responsible')
        if not lr:
            return None, 'Para PJ, o ator legal_responsible é obrigatório.'
        result.append(lr)

    # owner se não for próprio
    if not _normalize_bool_owner(owner_text):
        ow = by_actor.get('owner')
        if not ow:
            return None, 'Quando owner != "Próprio", envie os dados do ator owner.'
        result.append(ow)

    return result, None


class RevoAuthView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        force = request.query_params.get('force') == '1'
        token, err = _get_revo_token_cached(force=force)
        if err:
            return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'token': token}, status=status.HTTP_200_OK)


class RevoCEPView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, zipcode: str, propertyType: str = None):
        force = request.query_params.get('force') == '1'
        token = request.headers.get('X-Revo-Token')
        if not token:
            token, err = _get_revo_token_cached(force=force)
            if err:
                return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)

        zipcode = _sanitize_digits(zipcode)
        prop = propertyType or 'casa'
        url = f'{REVO_BASE_URL}/v3/cep/{zipcode}/{prop}'
        try:
            resp = requests.get(url, headers=_bearer_headers(token), timeout=20)
            if resp.status_code in (401, 403) and not request.headers.get('X-Revo-Token'):
                token, err = _get_revo_token_cached(force=True)
                if err:
                    return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)
                resp = requests.get(url, headers=_bearer_headers(token), timeout=20)
            data = resp.json()
            return Response(data, status=resp.status_code)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class RevoSimulationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        force = request.query_params.get('force') == '1'
        token = request.headers.get('X-Revo-Token')
        if not token:
            token, err = _get_revo_token_cached(force=force)
            if err:
                return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)

        prospect_id = request.data.get('prospect_id')
        if not prospect_id:
            return Response({'detail': 'prospect_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            prospect = Prospect.objects.get(pk=prospect_id)
        except Prospect.DoesNotExist:
            return Response({'detail': 'Prospect não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        seller_email = request.data.get('seller_email')
        energy_provider_id = request.data.get('energy_provider_id') or None
        energy_provider_name = request.data.get('energy_provider_name') or None
        property_type = request.data.get('property_type') or None
        monthly_consumption = request.data.get('monthly_consumption')
        incoming_lead_actors = request.data.get('lead_actors') or []

        # Monta fallback para contractor a partir do Prospect
        fallback = {
            'legal_name': prospect.legal_name,
            'name': prospect.lead_name,
            'cellphone': _sanitize_digits(prospect.cellphone),
            'email': prospect.email,
            'zip_code': _sanitize_digits(prospect.contractor_zip_code or prospect.zip_code),
            'address': prospect.contractor_address or '',
            'number': prospect.contractor_number or '',
            'complement': prospect.contractor_complement or '',
            'neighborhood': prospect.contractor_neighborhood or '',
            'city': prospect.contractor_city or '',
            'st': (prospect.contractor_st or '')[:2],
        }

        # Corpo base da simulação
        body = {
            'property_type': property_type or prospect.preferred_property_type,
            'zip_code': _sanitize_digits(prospect.zip_code),
            'electric_bill': float((prospect.last_electric_bill) or 0),
            'cellphone': _sanitize_digits(prospect.cellphone),
            'contract_person': prospect.person_type or 'PF',
            'owner': request.data.get('owner') or 'Outro',
            'seller_email': seller_email,
            'energy_provider_id': energy_provider_id,
        }
        # lead_actors conforme regras
        la_payload, la_err = _build_lead_actors_payload(
            contract_person=body['contract_person'],
            owner_text=body['owner'],
            incoming=incoming_lead_actors,
            fallback=fallback,
        )
        if la_err:
            return Response({'detail': la_err}, status=status.HTTP_400_BAD_REQUEST)
        body['lead_actors'] = la_payload

        if monthly_consumption:
            body['monthly_consumption'] = monthly_consumption

        url = f'{REVO_BASE_URL}/v3/simulation'
        try:
            resp = requests.post(url, json=body, headers=_bearer_headers(token), timeout=40)
            if resp.status_code in (401, 403) and not request.headers.get('X-Revo-Token'):
                token, err = _get_revo_token_cached(force=True)
                if err:
                    return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)
                resp = requests.post(url, json=body, headers=_bearer_headers(token), timeout=40)
            if resp.status_code != 200:
                return Response(resp.json(), status=resp.status_code)

            payload = resp.json()
            data = (payload.get('data') or [{}])[0]

            installation = data.get('installation_address') or {}
            electric_bill_info = data.get('electric_bill') or {}

            is_owner_self = _normalize_bool_owner(body.get('owner'))

            proposal = Proposal.objects.create(
                prospect=prospect,
                product=None,
                reference_code=str(data.get('reference') or ''),
                zip_code=_sanitize_digits(installation.get('zip_code') or prospect.zip_code),
                address=installation.get('address') or '',
                number=installation.get('number'),
                complement=installation.get('complement'),
                neighborhood=installation.get('neighborhood'),
                city=installation.get('city') or '',
                state=(installation.get('st') or '')[:2],
                contract_person=body.get('contract_person', 'PF'),
                property_type=property_type,
                owner=body.get('owner', 'Outro'),
                is_owner_self=is_owner_self,
                seller_email=seller_email,
                nsu=None,
                cpf_cnpj=_sanitize_digits(prospect.fiscal_number) if prospect.fiscal_number else None,
                legal_name=prospect.legal_name,
                email=prospect.email,
                electric_bill_amount=Decimal(str(electric_bill_info.get('value') or prospect.last_electric_bill or 0)),
                consumer_unit=electric_bill_info.get('consumer_unit'),
                consumer_group=electric_bill_info.get('consumer_group'),
                monthly_consumption=monthly_consumption,
                energy_provider_id=energy_provider_id,
                energy_provider_name=energy_provider_name,
                usr_record=str(request.user),
            )

            # Persistir atores usados (exceto contractor)
            for item in la_payload:
                if item.get('actor') == 'contractor':
                    continue
                ProposalLeadActor.objects.update_or_create(
                    proposal=proposal,
                    actor=item.get('actor'),
                    defaults={
                        'legal_name': item.get('legal_name'),
                        'name': item.get('name'),
                        'cpf_cnpj': item.get('cpf') or item.get('cpf_cnpj'),
                        'cellphone': item.get('cellphone'),
                        'email': item.get('email'),
                        'zip_code': item.get('zip_code'),
                        'address': item.get('address'),
                        'number': item.get('number'),
                        'complement': item.get('complement'),
                        'neighborhood': item.get('neighborhood'),
                        'city': item.get('city'),
                        'st': item.get('st'),
                    }
                )

            exp_raw = data.get('proposal_expiration_date')
            dtt_exp = None
            if exp_raw:
                try:
                    dtt_exp = make_aware(datetime.fromisoformat(exp_raw.replace('Z', '+00:00')))
                except Exception:
                    dtt_exp = None

            result = ProposalResult.objects.create(
                proposal=proposal,
                contract_type=data.get('contract_type') or '',
                contract_duration_months=int(data.get('contract_duration') or 0),
                discount_percentage=Decimal(str(data.get('discount_percentage') or 0)),
                discount_amount=Decimal(str(data.get('discount_amount') or 0)),
                annual_economy=Decimal(str(data.get('economy_thirty_years') or 0)),
                economy_in_three_years=None,
                installment_amount=Decimal('0'),
                total_installments=0,
                total_amount=Decimal('0'),
                kwp=Decimal(str(data.get('kwp') or 0)),
                kwh_annual=Decimal(str(data.get('kWh_annual') or 0)),
                required_area=int(data.get('required_area') or 0) if data.get('required_area') is not None else None,
                qty_modules=int(data.get('quantity_modules') or 0) if data.get('quantity_modules') is not None else None,
                energy_provider_id=int(data.get('energy_provider_id') or 0) if data.get('energy_provider_id') is not None else None,
                energy_provider_name=data.get('energy_provider_name'),
                provider_costs=Decimal(str(data.get('energy_provider_costs') or 0)),
                revo_costs=Decimal(str(data.get('energy_revo_costs') or 0)),
                electric_bill_value=Decimal(str(data.get('energy_provider_electric_bill') or 0)),
                consumer_unit=electric_bill_info.get('consumer_unit'),
                consumer_group=electric_bill_info.get('consumer_group'),
                proposal_expiration_at=dtt_exp or make_aware(datetime.utcnow()),
                status='Ativo',
                usr_record=str(request.user),
            )

            return Response({
                'revo': payload,
                'proposal': ProposalSerializer(proposal).data,
                'result': ProposalResultSerializer(result).data,
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

    def put(self, request):
        force = request.query_params.get('force') == '1'
        token = request.headers.get('X-Revo-Token')
        if not token:
            token, err = _get_revo_token_cached(force=force)
            if err:
                return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)

        reference = request.data.get('reference')
        if not reference:
            return Response({'detail': 'reference é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        body = dict(request.data)
        url = f'{REVO_BASE_URL}/v3/simulation'
        try:
            resp = requests.put(url, json=body, headers=_bearer_headers(token), timeout=40)
            if resp.status_code in (401, 403) and not request.headers.get('X-Revo-Token'):
                token, err = _get_revo_token_cached(force=True)
                if err:
                    return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)
                resp = requests.put(url, json=body, headers=_bearer_headers(token), timeout=40)
            if resp.status_code != 200:
                return Response(resp.json(), status=resp.status_code)

            payload = resp.json()
            data = (payload.get('data') or [{}])[0]

            try:
                proposal = Proposal.objects.get(reference_code=str(reference))
            except Proposal.DoesNotExist:
                proposal = None

            exp_raw = data.get('proposal_expiration_date')
            dtt_exp = None
            if exp_raw:
                try:
                    dtt_exp = make_aware(datetime.fromisoformat(exp_raw.replace('Z', '+00:00')))
                except Exception:
                    dtt_exp = None

            result = ProposalResult.objects.create(
                proposal=proposal,
                contract_type=data.get('contract_type') or '',
                contract_duration_months=int(data.get('contract_duration') or 0),
                discount_percentage=Decimal(str(data.get('discount_percentage') or 0)),
                discount_amount=Decimal(str(data.get('discount_amount') or 0)),
                annual_economy=Decimal(str(data.get('economy_thirty_years') or 0)),
                economy_in_three_years=None,
                installment_amount=Decimal('0'),
                total_installments=0,
                total_amount=Decimal('0'),
                kwp=Decimal(str(data.get('kwp') or 0)),
                kwh_annual=Decimal(str(data.get('kWh_annual') or 0)),
                required_area=int(data.get('required_area') or 0) if data.get('required_area') is not None else None,
                qty_modules=int(data.get('quantity_modules') or 0) if data.get('quantity_modules') is not None else None,
                energy_provider_id=int(data.get('energy_provider_id') or 0) if data.get('energy_provider_id') is not None else None,
                energy_provider_name=data.get('energy_provider_name'),
                provider_costs=Decimal(str(data.get('energy_provider_costs') or 0)),
                revo_costs=Decimal(str(data.get('energy_revo_costs') or 0)),
                electric_bill_value=Decimal(str(data.get('energy_provider_electric_bill') or 0)),
                consumer_unit=None,
                consumer_group=None,
                proposal_expiration_at=dtt_exp or make_aware(datetime.utcnow()),
                status='Ativo',
                usr_record=str(request.user),
            )

            response = {
                'revo': payload,
                'result': ProposalResultSerializer(result).data,
            }
            if proposal:
                response['proposal'] = ProposalSerializer(proposal).data

            return Response(response, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


