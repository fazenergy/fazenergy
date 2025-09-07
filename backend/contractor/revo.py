import os
import re
import time
from decimal import Decimal
from datetime import datetime, timedelta
import requests

from django.conf import settings
from django.utils.timezone import make_aware
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db import transaction

from .models import Contractor, Proposal, ProposalResult, ProposalLeadActor
from .serializers import ProposalSerializer, ProposalResultSerializer


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
    result = []
    by_actor = { (a.get('actor') or '').strip(): a for a in (incoming or []) }

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
    if (contract_person or '').upper() == 'PJ' and not contractor.get('legal_name'):
        return None, 'Para PJ, contractor.legal_name é obrigatório.'
    result.append(contractor)

    if (contract_person or '').upper() == 'PJ':
        lr = by_actor.get('legal_responsible')
        if not lr:
            return None, 'Para PJ, o ator legal_responsible é obrigatório.'
        result.append(lr)

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
            try:
                if 'proposal' in locals() and proposal and getattr(proposal, 'pk', None):
                    proposal.delete()
            except Exception:
                pass
            return Response({'detail': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)


class RevoSimulationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            print("[REVO_SIM] ENTER POST contractor_id=", request.data.get('contractor_id'))
        except Exception:
            pass
        force = request.query_params.get('force') == '1'
        token = request.headers.get('X-Revo-Token')
        if not token:
            token, err = _get_revo_token_cached(force=force)
            if err:
                return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)

        # Lead actors recebidos no payload (para possíveis fallbacks na criação do contractor)
        incoming_lead_actors_root = request.data.get('lead_actors') or []
        la_contractor_incoming_root = next((a for a in incoming_lead_actors_root if (a.get('actor') or '').strip() == 'contractor'), {})

        contractor_id = request.data.get('contractor_id') or request.data.get('prospect_id')
        contractor_block = request.data.get('contractor') or {}
        prospect = None
        if contractor_id:
            try:
                prospect = Contractor.objects.get(pk=contractor_id)
            except Contractor.DoesNotExist:
                return Response({'detail': 'Contractor não encontrado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Criar/Reutilizar contractor a partir do payload
            try:
                from core.models import Licensed as CoreLicensed  # import local para evitar ciclos
            except Exception:
                CoreLicensed = None
            lic_id = contractor_block.get('licensed_id') or request.data.get('licensed_id')
            fiscal_from_contractor = contractor_block.get('fiscal_number')
            fiscal_from_root = request.data.get('fiscal_number')
            if not lic_id:
                return Response({'detail': 'licensed_id é obrigatório quando contractor_id não é enviado'}, status=status.HTTP_400_BAD_REQUEST)
            if not (fiscal_from_contractor or fiscal_from_root):
                return Response({'detail': 'fiscal_number é obrigatório para criar/associar contractor'}, status=status.HTTP_400_BAD_REQUEST)
            if CoreLicensed is not None:
                try:
                    CoreLicensed.objects.only('id').get(pk=lic_id)
                except Exception:
                    return Response({'detail': 'Licensed não encontrado'}, status=status.HTTP_404_NOT_FOUND)
            fiscal_number_norm_tmp = _sanitize_digits(fiscal_from_contractor or fiscal_from_root)
            prospect = Contractor.objects.filter(fiscal_number=fiscal_number_norm_tmp, licensed_id=lic_id).first()
            if not prospect:
                derived_name = contractor_block.get('lead_name') or contractor_block.get('name') or la_contractor_incoming_root.get('name') or 'Novo Lead'
                derived_email = contractor_block.get('email') or la_contractor_incoming_root.get('email') or ''
                derived_cellphone = _sanitize_digits(
                    contractor_block.get('cellphone') or la_contractor_incoming_root.get('cellphone') or ''
                )
                if not derived_email:
                    return Response({'detail': 'email é obrigatório para criar contractor (lead_actors.contractor.email)'}, status=status.HTTP_400_BAD_REQUEST)
                if not derived_cellphone:
                    return Response({'detail': 'cellphone é obrigatório para criar contractor'}, status=status.HTTP_400_BAD_REQUEST)
                # Deriva person_type: se vier contract_person PJ ou contractor tiver legal_name, assumimos PJ
                desired_person_type = (request.data.get('contract_person') or '').strip().upper()
                if desired_person_type == 'PJ' or (contractor_block.get('legal_name') or la_contractor_incoming_root.get('legal_name')):
                    person_type_final = 'PJ'
                else:
                    person_type_final = (contractor_block.get('person_type') or 'PF')[:2]
                prospect = Contractor.objects.create(
                    licensed_id=lic_id,
                    lead_name=derived_name,
                    email=derived_email,
                    cellphone=derived_cellphone,
                    person_type=person_type_final,
                    fiscal_number=fiscal_number_norm_tmp,
                    legal_name=contractor_block.get('legal_name') or la_contractor_incoming_root.get('legal_name'),
                    usr_record=str(request.user),
                )
            else:
                # Atualiza legal_name se vier no payload e estiver vazio no registro
                incoming_legal_name = contractor_block.get('legal_name') or la_contractor_incoming_root.get('legal_name')
                if incoming_legal_name and not prospect.legal_name:
                    prospect.legal_name = incoming_legal_name
                    try:
                        prospect.save(update_fields=['legal_name'])
                    except Exception:
                        pass

        # Vendedor interno fixo via env (se não vier no payload)
        # Define seller_email a partir do payload, settings ou .env
        from django.conf import settings as dj_settings
        seller_email = (
            request.data.get('seller_email')
            or getattr(dj_settings, 'REVO_SELLER_EMAIL', None)
            or os.getenv('REVO_SELLER_EMAIL')
        )
        energy_provider_id = request.data.get('energy_provider_id') or None
        energy_provider_name = request.data.get('energy_provider_name') or None
        property_type = request.data.get('property_type') or None
        req_zip_code = request.data.get('zip_code')
        if not req_zip_code:
            return Response({'detail': 'zip_code é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        zip_code_norm = _sanitize_digits(req_zip_code)
        monthly_consumption = request.data.get('monthly_consumption')
        incoming_lead_actors = request.data.get('lead_actors') or []
        consumer_unit = request.data.get('consumer_unit')
        consumer_group = request.data.get('consumer_group')

        # REVO exige fiscal_number no payload raiz
        req_fiscal_number = request.data.get('fiscal_number') or prospect.fiscal_number
        fiscal_number_norm = _sanitize_digits(req_fiscal_number or '')
        if not fiscal_number_norm:
            return Response({'detail': 'fiscal_number é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        # email do contractor é obrigatório (prioriza lead_actors.contractor.email; se não, prospect.email)
        _derived_email_payload = la_contractor_incoming_root.get('email') or prospect.email or (contractor_block.get('email') if 'contractor_block' in locals() else None)
        if not _derived_email_payload:
            return Response({'detail': 'email é obrigatório (lead_actors.contractor.email)'}, status=status.HTTP_400_BAD_REQUEST)

        fallback = {
            'legal_name': prospect.legal_name,
            'name': prospect.lead_name,
            'cellphone': _sanitize_digits(prospect.cellphone) or _sanitize_digits(la_contractor_incoming_root.get('cellphone') or ''),
            'email': _derived_email_payload,
            # A REVO não separa endereço do contratante; endereço de instalação fica na Proposal
            'zip_code': None,
            'address': None,
            'number': None,
            'complement': None,
            'neighborhood': None,
            'city': None,
            'st': None,
        }

        # Define contract_person priorizando payload; caso contrário, usa person_type do contractor
        _contract_person_payload = (request.data.get('contract_person') or '').strip().upper()
        contract_person_final = _contract_person_payload if _contract_person_payload in ('PF', 'PJ') else (prospect.person_type or 'PF')

        body = {
            'property_type': property_type,
            'zip_code': zip_code_norm,
            'electric_bill': float((request.data.get('electric_bill')) or 0),
            'cellphone': _sanitize_digits(prospect.cellphone) or _sanitize_digits(la_contractor_incoming_root.get('cellphone') or ''),
            'contract_person': contract_person_final,
            'owner': request.data.get('owner') or 'Outro',
            'seller_email': seller_email,
            'energy_provider_id': energy_provider_id,
        }
        # Atualiza o person_type do contractor existente para refletir o payload (PF/PJ)
        try:
            if prospect and contract_person_final and prospect.person_type != contract_person_final:
                prospect.person_type = contract_person_final
                prospect.save(update_fields=['person_type'])
        except Exception:
            pass
        if not body['cellphone']:
            return Response({'detail': 'cellphone é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)
        body['fiscal_number'] = fiscal_number_norm
        if consumer_unit:
            body['consumer_unit'] = consumer_unit
        if consumer_group:
            body['consumer_group'] = consumer_group
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

        # Validação de aliciamento: CPF + CEP com proposta ativa e janela 30 dias pós-expiração
        cpf_norm = _sanitize_digits(prospect.fiscal_number or '')
        override = request.query_params.get('override') == '1'
        if cpf_norm and zip_code_norm and not override:
            active_conflict = Proposal.objects.filter(
                cpf_cnpj=cpf_norm,
                zip_code=zip_code_norm,
                status__in=['Aguardando', 'Simulated', 'Ativo'],
                dtt_expired__gt=timezone.now(),
            ).exclude(contractor=prospect).select_related('contractor').first()
            if active_conflict:
                return Response({'detail': 'CPF já possui proposta ativa para este CEP até expirar.', 'licensed_id': active_conflict.contractor.licensed_id}, status=409)
            cutoff = timezone.now() - timedelta(days=30)
            recent_conflict = Proposal.objects.filter(
                cpf_cnpj=cpf_norm,
                zip_code=zip_code_norm,
                dtt_expired__isnull=False,
                dtt_expired__gte=cutoff,
            ).exclude(contractor__licensed_id=prospect.licensed_id).select_related('contractor').first()
            if recent_conflict:
                return Response({'detail': 'Proposta recente (≤30 dias) para este CPF+CEP associada a outro licenciado.', 'licensed_id': recent_conflict.contractor.licensed_id}, status=409)

        # Idempotência: já existe proposta ativa igual para o mesmo licensed+CPF+CEP
        existing = Proposal.objects.filter(
            contractor__licensed_id=prospect.licensed_id,
            cpf_cnpj=cpf_norm,
            zip_code=zip_code_norm,
            status__in=['Aguardando', 'Simulated', 'Ativo'],
        ).order_by('-id').first()
        if existing:
            latest_result = ProposalResult.objects.filter(proposal=existing).order_by('-id').first()
            return Response({
                'detail': 'Já existe proposta ativa para este CPF+CEP neste licenciado.',
                'licensed_id': existing.contractor.licensed_id,
                'proposal_id': existing.id,
                'result_id': latest_result.id if latest_result else None,
                'proposal': ProposalSerializer(existing).data,
                'result': ProposalResultSerializer(latest_result).data if latest_result else None,
            }, status=409)

        url = f'{REVO_BASE_URL}/v3/simulation'
        try:
            print(f"[REVO_SIM] seller_email={seller_email}")
        except Exception:
            pass
        try:
            resp = requests.post(url, json=body, headers=_bearer_headers(token), timeout=40)
            if resp.status_code in (401, 403) and not request.headers.get('X-Revo-Token'):
                token, err = _get_revo_token_cached(force=True)
                if err:
                    return Response({'detail': err}, status=status.HTTP_400_BAD_REQUEST)
                resp = requests.post(url, json=body, headers=_bearer_headers(token), timeout=40)
            if resp.status_code not in (200, 201):
                return Response(resp.json(), status=resp.status_code)

            payload = resp.json()
            raw_data = payload.get('data')
            if isinstance(raw_data, list):
                data = (raw_data or [{}])[0]
            elif isinstance(raw_data, dict):
                data = raw_data
            else:
                data = {}

            installation = data.get('installation_address') or {}
            electric_bill_info = data.get('electric_bill') or {}

            is_owner_self = _normalize_bool_owner(body.get('owner'))

            # Fallback do endereço de instalação a partir do body (lead_actors.actor == 'contractor')
            contractor_actor = next((a for a in (la_payload or []) if a.get('actor') == 'contractor'), {})
            install_zip = _sanitize_digits(
                (installation.get('zip_code') if installation else None)
                or contractor_actor.get('zip_code')
                or zip_code_norm
            )
            install_addr = (installation.get('address') if installation else None) or contractor_actor.get('address') or ''
            install_number = (installation.get('number') if installation else None) or contractor_actor.get('number')
            install_complement = (installation.get('complement') if installation else None) or contractor_actor.get('complement')
            install_neighborhood = (installation.get('neighborhood') if installation else None) or contractor_actor.get('neighborhood')
            install_city = (installation.get('city') if installation else None) or contractor_actor.get('city') or ''
            install_state = ((installation.get('st') if installation else None) or contractor_actor.get('st') or '')[:2]

            ep_name = energy_provider_name or data.get('energy_provider_name')

            proposal = Proposal.objects.create(
                contractor=prospect,
                product=None,
                reference_code=str(data.get('reference') or ''),
                zip_code=install_zip,
                address=install_addr,
                number=install_number,
                complement=install_complement,
                neighborhood=install_neighborhood,
                city=install_city,
                state=install_state,
                contract_person=body.get('contract_person', 'PF'),
                property_type=property_type,
                owner=body.get('owner', 'Outro'),
                is_owner_self=is_owner_self,
                seller_email=seller_email,
                cpf_cnpj=fiscal_number_norm or (_sanitize_digits(prospect.fiscal_number) if prospect.fiscal_number else None),
                legal_name=prospect.legal_name,
                email=prospect.email,
                electric_bill_amount=Decimal(str(electric_bill_info.get('value') or request.data.get('electric_bill') or 0)),
                consumer_unit=consumer_unit or electric_bill_info.get('consumer_unit'),
                consumer_group=consumer_group or electric_bill_info.get('consumer_group'),
                monthly_consumption=monthly_consumption,
                energy_provider_id=energy_provider_id,
                energy_provider_name=ep_name,
                visit_1=request.data.get('visit_1'),
                visit_2=request.data.get('visit_2'),
                usr_record=str(request.user),
                request_payload=body,
            )
            try:
                print(f"[REVO_SIM] Proposal created id={proposal.id} ref={proposal.reference_code} zip={proposal.zip_code}")
            except Exception:
                pass

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
                    parsed = datetime.fromisoformat(exp_raw.replace('Z', '+00:00'))
                    dtt_exp = parsed if parsed.tzinfo is not None else make_aware(parsed)
                except Exception:
                    dtt_exp = None

            result = ProposalResult.objects.create(
                proposal=proposal,
                contract_type=data.get('contract_type') or '',
                contract_duration=int(data.get('contract_duration') or 0),
                discount_percentage=Decimal(str(data.get('discount_percentage') or 0)),
                discount_amount=Decimal(str(data.get('discount_amount') or 0)),
                economy_thirty_years=Decimal(str(data.get('economy_thirty_years') or 0)),
                installment_amount=Decimal('0'),
                total_installments=0,
                total_amount=Decimal('0'),
                kwp=Decimal(str(data.get('kwp') or 0)),
                kwh_annual=Decimal(str(data.get('kWh_annual') or 0)),
                required_area=Decimal(str(data.get('required_area'))) if data.get('required_area') is not None else None,
                qty_modules=int(data.get('quantity_modules') or 0) if data.get('quantity_modules') is not None else None,
                energy_provider_id=int(data.get('energy_provider_id') or 0) if data.get('energy_provider_id') is not None else None,
                energy_provider_name=data.get('energy_provider_name'),
                provider_costs=Decimal(str(data.get('energy_provider_costs') or 0)),
                revo_costs=Decimal(str(data.get('energy_revo_costs') or 0)),
                electric_bill_value=Decimal(str(data.get('energy_provider_electric_bill') or 0)),
                consumer_unit=(electric_bill_info.get('consumer_unit') or consumer_unit),
                consumer_group=(electric_bill_info.get('consumer_group') or consumer_group),
                proposal_expiration_at=dtt_exp or make_aware(datetime.utcnow()),
                status='Ativo',
                usr_record=str(request.user),
            )
            try:
                print(f"[REVO_SIM] Result created id={result.id} proposal_id={proposal.id} contract_type={result.contract_type}")
            except Exception:
                pass
            # guarda payload de resposta bruto no objeto (para refletir no serializer)
            try:
                result.response_payload = payload
                result.save(update_fields=['response_payload'])
            except Exception:
                pass

            # Reflete expiração também na Proposal para filtros rápidos
            if dtt_exp:
                proposal.dtt_expired = dtt_exp
                proposal.save(update_fields=['dtt_expired'])

            return Response({
                'revo': payload,
                'proposal_id': proposal.id,
                'result_id': result.id,
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
        # Garante seller_email via .env se não vier no payload
        try:
            if not body.get('seller_email'):
                from django.conf import settings as dj_settings
                env_seller = getattr(dj_settings, 'REVO_SELLER_EMAIL', None) or os.getenv('REVO_SELLER_EMAIL')
                if env_seller:
                    body['seller_email'] = env_seller
        except Exception:
            pass
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
                    parsed = datetime.fromisoformat(exp_raw.replace('Z', '+00:00'))
                    dtt_exp = parsed if parsed.tzinfo is not None else make_aware(parsed)
                except Exception:
                    dtt_exp = None

            result = ProposalResult.objects.create(
                proposal=proposal,
                contract_type=data.get('contract_type') or '',
                contract_duration=int(data.get('contract_duration') or 0),
                discount_percentage=Decimal(str(data.get('discount_percentage') or 0)),
                discount_amount=Decimal(str(data.get('discount_amount') or 0)),
                economy_thirty_years=Decimal(str(data.get('economy_thirty_years') or 0)),
                installment_amount=Decimal('0'),
                total_installments=0,
                total_amount=Decimal('0'),
                kwp=Decimal(str(data.get('kwp') or 0)),
                kwh_annual=Decimal(str(data.get('kWh_annual') or 0)),
                required_area=Decimal(str(data.get('required_area'))) if data.get('required_area') is not None else None,
                qty_modules=int(data.get('quantity_modules') or 0) if data.get('quantity_modules') is not None else None,
                energy_provider_id=int(data.get('energy_provider_id') or 0) if data.get('energy_provider_id') is not None else None,
                energy_provider_name=data.get('energy_provider_name'),
                provider_costs=Decimal(str(data.get('energy_provider_costs') or 0)),
                revo_costs=Decimal(str(data.get('energy_revo_costs') or 0)),
                electric_bill_value=Decimal(str(data.get('energy_provider_electric_bill') or 0)),
                consumer_unit=( (data.get('electric_bill') or {}).get('consumer_unit') or body.get('consumer_unit') ),
                consumer_group=( (data.get('electric_bill') or {}).get('consumer_group') or body.get('consumer_group') ),
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


