## Integração Amazon S3 no projeto FazEnergyFinal

Este guia descreve como integrar o Amazon S3 ao monorepo (`@backend/` Django/DRF e `@frontend/` Vue 3), cobrindo o que pegar no painel da AWS, permissões IAM mínimas, CORS do bucket, variáveis de ambiente, e exemplos de upload/download usando URLs pré‑assinadas.

### 1) O que coletar no painel da AWS
- **Bucket name**: nome exato do bucket S3 já criado (ex.: `fazenergy-cloud-bucket`).
- **Region**: região do bucket (ex.: `us-east-1`).
- (Recomendado) **IAM User** dedicado para o backend, com Access Key/Secret restritos ao bucket.
  - Access key ID
  - Secret access key
- (Opcional) **Bucket ARN** e **AWS Account ID** (úteis em políticas/CloudTrail).
- (Opcional) **SSE (Server-Side Encryption)** adotado (ex.: AES256) caso queira impor no upload.

Onde pegar:
- S3 > Buckets > selecione o bucket > aba "Properties" e "Permissions" (CORS e Policy)
- IAM > Users > selecione o usuário > aba "Security credentials" (Access Key/Secret)

### 2) Permissões IAM mínimas (política para o usuário do backend)
Conceda apenas o necessário para o backend gerar URLs pré‑assinadas e gerenciar objetos. Ajuste `RESOURCE_BUCKET`/`REGION`:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ListBucketMinimal",
      "Effect": "Allow",
      "Action": ["s3:ListBucket"],
      "Resource": "arn:aws:s3:::RESOURCE_BUCKET"
    },
    {
      "Sid": "S3ObjectRW",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:AbortMultipartUpload"
      ],
      "Resource": "arn:aws:s3:::RESOURCE_BUCKET/*"
    }
  ]
}
```

Boas práticas:
- Crie um usuário exclusivo para o `@backend/` com essa política anexada.
- Se necessário, restrinja por `aws:SourceIp` ou prefixes (ex.: `arn:aws:s3:::bucket/app/*`).

### 3) CORS do bucket (para uploads diretos do frontend)
Configure no S3 > Bucket > Permissions > CORS rules, permitindo seus domínios (produção e dev). Exemplo seguro (ajuste `https://app.seudominio.com` e mantenha `http://localhost:5173` para dev):

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "HEAD"],
    "AllowedOrigins": [
      "https://app.seudominio.com",
      "http://localhost:5173"
    ],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

Evite `DELETE` no CORS para o navegador; exclusões devem ser feitas pelo backend.

### 4) Variáveis de ambiente do `@backend/`
Defina no `.env`/`docker-compose.yml` do backend:

```bash
AWS_ACCESS_KEY_ID=AKIA...           # do usuário IAM
AWS_SECRET_ACCESS_KEY=...           # do usuário IAM
AWS_STORAGE_BUCKET_NAME=fazenergy-files-...  # nome exato do bucket
AWS_S3_REGION_NAME=sa-east-1        # região do bucket
# Opcional(es)
AWS_S3_SIGNATURE_VERSION=s3v4
AWS_S3_ADDRESSING_STYLE=virtual     # virtual (padrão) ou path
AWS_S3_DEFAULT_ACL=private
AWS_S3_SSE=AES256                   # enforce criptografia no upload (se adotado)
```

Se for usar `django-storages` para FileField/Media, adicione também:

```bash
USE_S3_STORAGE=true
```

### 5) Backend: configuração e endpoints (Django/DRF)
Você pode usar duas abordagens complementares:

- **A)** `django-storages` como `DEFAULT_FILE_STORAGE` (para armazenar `FileField/ImageField` diretamente no S3).
- **B)** Geração de **URLs pré‑assinadas** (recomendado para uploads grandes via browser, sem transitar o arquivo pelo servidor).

#### 5.A) `django-storages` (opcional)
1. Dependências (adicionar no `@backend/requirements.txt` e instalar):
   - `boto3`
   - `django-storages`
2. `@backend/config/settings.py` (exemplo):

```python
INSTALLED_APPS += ["storages"]

if os.getenv("USE_S3_STORAGE") == "true":
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "sa-east-1")
    AWS_S3_SIGNATURE_VERSION = os.getenv("AWS_S3_SIGNATURE_VERSION", "s3v4")
    AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE", "virtual")
    AWS_DEFAULT_ACL = os.getenv("AWS_S3_DEFAULT_ACL", "private")
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = True  # impede URLs públicas permanentes
    if os.getenv("AWS_S3_SSE"):
        AWS_S3_OBJECT_PARAMETERS = {"ServerSideEncryption": os.getenv("AWS_S3_SSE")}
```

> Use esta opção quando os modelos salvarem arquivos via `FileField` e você quiser transparência no armazenamento.

#### 5.B) URLs pré‑assinadas (recomendado)
Implemente dois endpoints no `@backend/`:

- `POST /api/core/storage/presign-upload` → retorna URL/fields para upload direto ao S3 (POST) ou URL (PUT)
- `GET  /api/core/storage/presign-download` → retorna URL para download temporário

Exemplo esquemático (DRF + `boto3`):

```python
import boto3
from botocore.config import Config
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import uuid

def _s3_client():
    return boto3.client(
        "s3",
        region_name=settings.AWS_S3_REGION_NAME,
        config=Config(signature_version=settings.AWS_S3_SIGNATURE_VERSION),
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def presign_upload(request):
    content_type = request.data.get("content_type")
    original_name = request.data.get("filename")
    # Escolha um prefix seguro, ex.: por usuário
    key = f"uploads/{request.user.id}/{uuid.uuid4()}-{original_name}"

    s3 = _s3_client()
    # Exemplo com POST pré-assinado (permite multipart e campos extra)
    conditions = []
    fields = {}
    if getattr(settings, "AWS_S3_SSE", None):
        fields["x-amz-server-side-encryption"] = settings.AWS_S3_SSE
        conditions.append({"x-amz-server-side-encryption": settings.AWS_S3_SSE})
    if content_type:
        conditions.append(["starts-with", "$Content-Type", content_type.split("/")[0]])

    post = s3.generate_presigned_post(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=600,  # 10 min
    )
    return Response({"upload": post, "key": key})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def presign_download(request):
    key = request.query_params.get("key")
    if not key:
        return Response({"detail": "key é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)
    s3 = _s3_client()
    url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": settings.AWS_STORAGE_BUCKET_NAME, "Key": key},
        ExpiresIn=600,
    )
    return Response({"url": url})
```

Validações recomendadas no backend:
- Verificar extensão/tipo (`content_type`) e tamanho máximo.
- Forçar prefixos por usuário/entidade do domínio (evita colisões e acesso indevido).
- Persistir a `key` no seu modelo de domínio, se aplicável.

### 6) Frontend (`@frontend/` Vue 3): upload/download

#### Upload via POST pré‑assinado (recomendado)
Fluxo:
1) Frontend pede ao backend a URL pré‑assinada com `filename` e `content_type`.
2) Backend retorna `{ upload: { url, fields }, key }`.
3) Frontend envia `FormData` diretamente ao S3.

Exemplo (Axios):

```javascript
// services/s3.js
import axios from "axios";

export async function requestPresignUpload(file) {
  const { data } = await axios.post("/api/core/storage/presign-upload", {
    filename: file.name,
    content_type: file.type,
  });
  return data; // { upload: { url, fields }, key }
}

export async function uploadToS3PresignedPost(upload, file) {
  const formData = new FormData();
  Object.entries(upload.fields).forEach(([k, v]) => formData.append(k, v));
  formData.append("file", file);
  const res = await axios.post(upload.url, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (e) => {/* opcional: progresso */},
  });
  return res.status === 204 || res.status === 201;
}
```

Uso em um componente:

```javascript
import { requestPresignUpload, uploadToS3PresignedPost } from "@/services/s3";

async function handleUpload(file) {
  const { upload, key } = await requestPresignUpload(file);
  const ok = await uploadToS3PresignedPost(upload, file);
  if (ok) {
    // Persistir a key no backend (se necessário)
    // await axios.post('/api/.../save', { key })
  }
}
```

Alternativa (PUT pré‑assinado):

```javascript
// Se backend retornar apenas { url, key } para PUT
await axios.put(url, file, { headers: { "Content-Type": file.type } });
```

#### Download via URL pré‑assinada

```javascript
// Solicita ao backend uma URL de download temporária
const { data } = await axios.get("/api/core/storage/presign-download", { params: { key } });
window.location.href = data.url; // ou abrir em nova aba
```

### 7) Boas práticas de segurança e operação
- Mantenha o bucket **privado**; use sempre URLs pré‑assinadas.
- TTL curto nas URLs (5–15 min) e verificação de autorização no backend.
- Restrinja CORS aos domínios necessários.
- Utilize SSE (`AES256` ou KMS) e, se quiser, imponha via política do bucket.
- Defina limites de tamanho de upload e valide `content_type`.
- Atribua chaves (`key`) com prefixos por entidade (ex.: `uploads/<licensed_id>/...`).

Política de bucket para impor TLS (opcional):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::RESOURCE_BUCKET",
        "arn:aws:s3:::RESOURCE_BUCKET/*"
      ],
      "Condition": {"Bool": {"aws:SecureTransport": "false"}}
    }
  ]
}
```

### 8) Docker/Deploy
- Adicione as variáveis AWS no serviço do backend no `docker-compose.yml`.
- Em produção, injete variáveis via Secrets/CI e não comite Access Keys.

Exemplo de trecho no compose (ilustrativo):

```yaml
services:
  backend:
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_STORAGE_BUCKET_NAME=${AWS_STORAGE_BUCKET_NAME}
      - AWS_S3_REGION_NAME=${AWS_S3_REGION_NAME}
      - AWS_S3_SIGNATURE_VERSION=s3v4
      - AWS_S3_DEFAULT_ACL=private
      - AWS_S3_SSE=AES256
      - USE_S3_STORAGE=true
```

### 9) Troubleshooting
- `SignatureDoesNotMatch`: confira região, método (POST vs PUT), `Content-Type` e relógio do servidor (NTP).
- `CORS error`: revise `AllowedOrigins` e `AllowedMethods` no CORS do bucket.
- `AccessDenied`: valide a política do usuário IAM e se a `key` está no prefix permitido.
- `204 esperado no POST`: upload S3 por POST normalmente retorna `204 No Content` (ou `201`).

### 10) Checklist rápido
- [ ] Bucket e região definidos
- [ ] Usuário IAM com política mínima
- [ ] CORS configurado (prod + dev)
- [ ] Variáveis de ambiente no `@backend/`
- [ ] Endpoints DRF de pré‑assinatura
- [ ] Fluxo no `@frontend/` (upload/download)
- [ ] Validações e segurança ativas

—
Referências: `boto3` S3, `django-storages` S3Boto3Storage, documentação AWS S3.


