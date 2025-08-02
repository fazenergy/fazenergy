import os
import requests
import time
from django.conf import settings

_cached_token = None
_cached_token_time = 0


REVO_AUTH_URL = os.getenv("REVO_AUTH_URL", "")
REVO_USERNAME = os.getenv("REVO_USERNAME", "")
REVO_PASSWORD = os.getenv("REVO_PASSWORD", "")


def fetch_and_cache_token():
    global _cached_token, _cached_token_time

    now = time.time()
    if _cached_token and (now - _cached_token_time < 3600):
        return _cached_token

    response = requests.post(REVO_AUTH_URL, auth=(REVO_USERNAME, REVO_PASSWORD))
    if response.status_code == 200:
        _cached_token = response.json().get("token")
        _cached_token_time = now
        return _cached_token
    else:
        raise Exception("Erro ao autenticar com a API da Revo")

class TestTokenView(APIView):
    def post(self, request):
        return Response({
            "success": True,
            "data": [
                {
                    "token": "5717|F3zMHYyw5cMkYF7cLhbFanChGzBNiwP7Nzz8O6Osd76aa594"
                }
            ],
            "message": [
                "Operação realizada com sucesso."
            ]
        })