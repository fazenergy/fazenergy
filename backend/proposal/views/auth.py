from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests, os, time

_cached_token = None
_cached_token_time = 0


def fetch_token():
    global _cached_token, _cached_token_time
    now = time.time()

    REVO_AUTH_URL = os.getenv("REVO_AUTH_URL", "")
    REVO_USERNAME = os.getenv("REVO_USERNAME", "")
    REVO_PASSWORD = os.getenv("REVO_PASSWORD", "")

    if _cached_token and (now - _cached_token_time < 3600):
        return _cached_token
    response = requests.post(REVO_AUTH_URL, auth=(REVO_USERNAME, REVO_PASSWORD))
    if response.status_code == 200:
        _cached_token = response.json()["data"][0]["token"]
        _cached_token_time = now
        return _cached_token
    raise Exception("Erro ao buscar token")

class RevoTokenView(APIView):
    def post(self, request):
        try:
            token = fetch_token()
            return Response({"success": True, "token": token}, status=200)
        except Exception as e:
            return Response({"success": False, "error": str(e)}, status=500)
