import os
import uuid
from typing import Dict, Optional

import requests


class SicoobPixClient:
    """Cliente mínimo para integração com PIX Pagamentos do Sicoob.

    Observações:
    - Este cliente lê configurações de ambiente. Para produção, configure:
      SICOOB_API_BASE_URL, SICOOB_OAUTH_URL, SICOOB_CLIENT_ID, SICOOB_CLIENT_SECRET,
      SICOOB_CERT_PATH, SICOOB_KEY_PATH.
    - Se possuir token pré-gerado, defina SICOOB_ACCESS_TOKEN (prioritário em dev).
    - Implementação resiliente: em caso de falha de autenticação/HTTP, retorna
      payload de erro descritivo.
    """

    def __init__(self, overrides: Optional[dict] = None) -> None:
        self.base_url = os.getenv("SICOOB_API_BASE_URL", "https://api.sicoob.com.br")
        self.oauth_url = os.getenv("SICOOB_OAUTH_URL", "https://auth.sicoob.com.br/oauth/token")
        self.client_id = os.getenv("SICOOB_CLIENT_ID", "")
        self.client_secret = os.getenv("SICOOB_CLIENT_SECRET", "")
        self.access_token = os.getenv("SICOOB_ACCESS_TOKEN", "")
        self.cert_path = os.getenv("SICOOB_CERT_PATH")
        self.key_path = os.getenv("SICOOB_KEY_PATH")

        # Overrides de configuração vindos do banco (PixConfig)
        cfg = overrides or {}
        self.base_url = cfg.get('api_base_url', self.base_url)
        self.oauth_url = cfg.get('oauth_url', self.oauth_url)
        self.client_id = cfg.get('client_id', self.client_id)
        self.client_secret = cfg.get('client_secret', self.client_secret)
        self.access_token = cfg.get('access_token', self.access_token)
        self.cert_path = cfg.get('cert_path', self.cert_path)
        self.key_path = cfg.get('key_path', self.key_path)

    def _mtls(self) -> Optional[tuple]:
        if self.cert_path and self.key_path:
            return (self.cert_path, self.key_path)
        if self.cert_path and not self.key_path:
            # Certificado combinado (pem) sem chave separada
            return self.cert_path  # type: ignore[return-value]
        return None

    def get_token(self) -> Optional[str]:
        if self.access_token:
            return self.access_token
        if not (self.client_id and self.client_secret):
            return None
        try:
            data = {
                "grant_type": "client_credentials",
                "scope": "pagamentos.pix.write pagamentos.pix.read",
            }
            auth = (self.client_id, self.client_secret)
            resp = requests.post(self.oauth_url, data=data, auth=auth, cert=self._mtls(), timeout=20)
            resp.raise_for_status()
            payload = resp.json()
            self.access_token = payload.get("access_token", "")
            return self.access_token or None
        except Exception:
            return None

    def _headers(self) -> Dict[str, str]:
        token = self.get_token() or ""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    @staticmethod
    def _join_url(base: str, path: str) -> str:
        """Junta base e path garantindo exatamente uma barra entre eles."""
        return f"{(base or '').rstrip('/')}/{(path or '').lstrip('/')}"

    def pay_pix_by_cpf_cnpj(self, *, amount: str, cpf_cnpj: str, name: str) -> Dict:
        """Inicia um pagamento PIX para uma chave tipo CPF/CNPJ.

        Parâmetros:
        - amount: string decimal com 2 casas (ex.: "123.45").
        - cpf_cnpj: somente dígitos.
        - name: nome do recebedor (até o limite aceito pela API).

        Retorno: dict com chaves 'ok' (bool), 'data' (payload) e 'error' (quando houver).
        """
        txid = uuid.uuid4().hex[:25]  # 25 chars máx (boa prática em Pix)
        # Espera-se que self.base_url já aponte para a base ".../pix-pagamentos/v2"
        # Ex.: https://sandbox.sicoob.com.br/sicoob/sandbox/pix-pagamentos/v2
        # Então o recurso correto é apenas "/pagamentos".
        endpoint = self._join_url(self.base_url, "pagamentos")

        # O payload exato depende da API do Sicoob (PIX Pagamentos).
        # Ajuste campos conforme contrato/homologação da instituição financeira.
        payload = {
            "txid": txid,
            "valor": {"original": str(amount)},
            "chave": cpf_cnpj,
            "recebedor": {
                "nome": name[:80]
            },
            # Campos adicionais podem ser necessários conforme o contrato
        }

        try:
            resp = requests.post(endpoint, json=payload, headers=self._headers(), cert=self._mtls(), timeout=30)
            if resp.status_code in (200, 201, 202):
                return {"ok": True, "data": {"txid": txid, "response": resp.json()}}
            return {"ok": False, "error": {"status": resp.status_code, "body": self._safe_json(resp)}}
        except Exception as exc:
            return {"ok": False, "error": {"exception": str(exc)}}

    @staticmethod
    def _safe_json(resp: requests.Response):
        try:
            return resp.json()
        except Exception:
            return {"text": resp.text}


