## Explicação da API Sicoob para Pagamentos a Licenciados (Sandbox)

Este guia resume como realizar pagamentos aos licenciados usando a API Pix Pagamentos v2 do Sicoob em ambiente de sandbox, com exemplos prontos para cURL e uma coleção Postman mínima.

- **Ambiente**: Sandbox (dados simulados/mocks)
- **Use para pagar**: API Pix Pagamentos v2
- **Não usar para pagar**: Pix Recebimentos (é para cobrar/receber), Cobrança Bancária (boletos), ITP (iniciação pelo usuário)

### 1) Bases de URL

- **Pix Pagamentos (Sandbox)**: `https://sandbox.sicoob.com.br/sicoob/sandbox/pix-pagamentos/v2`
- (Referência) **Pix Recebimentos (Sandbox)**: `https://sandbox.sicoob.com.br/sicoob/sandbox/pix/api/v2` (não usar para pagar)
- (Alternativa) **SPB Transferências (Sandbox)**: `https://sandbox.sicoob.com.br/sicoob/sandbox/spb/v2` (TED/TEF – usar somente se PIX não for opção)

O endpoint de criação de pagamento PIX fica sob o recurso `/pagamentos` quando a base já contém `/pix-pagamentos/v2`.

### 2) Autenticação

Para o sandbox, você pode usar um token Bearer fornecido previamente (Access Token). Em produção, o fluxo é OAuth2 Client Credentials (possivelmente com mTLS).

- Header: `Authorization: Bearer {{access_token}}`
- Header: `Content-Type: application/json`
- Header: `Accept: application/json`

Exemplo (opcional) para obter um token via OAuth2 Client Credentials (produção/homolog):

```bash
curl -X POST "https://auth.sicoob.com.br/oauth/token" \
  -u "{{client_id}}:{{client_secret}}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&scope=pagamentos.pix.write pagamentos.pix.read"
```

No sandbox deste projeto, substitua `{{access_token}}` pelo token que você possui.

### 3) Criar pagamento via PIX (Pix Pagamentos v2)

- **POST** `{{base_url}}/pagamentos`
- `{{base_url}}` no sandbox: `https://sandbox.sicoob.com.br/sicoob/sandbox/pix-pagamentos/v2`

Body (exemplo simples – ajuste aos campos exigidos pelo contrato/homologação):

```json
{
  "txid": "1234567890abcdef1234567",
  "valor": { "original": "100.00" },
  "chave": "12345678909",
  "recebedor": { "nome": "Nome do Recebedor" }
}
```

Campos:
- **txid**: identificador até 25 caracteres.
- **valor.original**: valor com 2 casas decimais.
- **chave**: chave PIX (CPF/CNPJ/EVP) apenas dígitos no caso de CPF/CNPJ.
- **recebedor.nome**: nome do recebedor (respeitar limite de caracteres).

#### Exemplo cURL (Sandbox)

```bash
ACCESS_TOKEN="{{SEU_ACCESS_TOKEN_SANDBOX}}"
BASE_URL="https://sandbox.sicoob.com.br/sicoob/sandbox/pix-pagamentos/v2"

curl -X POST "$BASE_URL/pagamentos" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "txid": "abc123def456ghi789jkl01",
    "valor": { "original": "150.00" },
    "chave": "12345678909",
    "recebedor": { "nome": "Licenciado Teste" }
  }'
```

Resposta esperada (exemplo ilustrativo):

```json
{
  "txid": "abc123def456ghi789jkl01",
  "situacao": "EM_PROCESSAMENTO",
  "detalhes": { "protocolo": "..." }
}
```

Obs.: campos reais podem variar conforme versão e contrato; consulte o catálogo do Sicoob.

### 4) Coleção Postman (mínima) – Importar e testar

Salve o JSON abaixo em um arquivo (ex.: `Sicoob-Pix-Pagamentos.postman_collection.json`) e importe no Postman. Depois, defina a variável de ambiente `access_token` com seu token do sandbox.

```json
{
  "info": {
    "name": "Sicoob - Pix Pagamentos (Sandbox)",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "PIX - Criar Pagamento",
      "request": {
        "method": "POST",
        "header": [
          { "key": "Authorization", "value": "Bearer {{access_token}}" },
          { "key": "Content-Type", "value": "application/json" },
          { "key": "Accept", "value": "application/json" }
        ],
        "url": {
          "raw": "{{base_url}}/pagamentos",
          "host": ["{{base_url}}"],
          "path": ["pagamentos"]
        },
        "body": {
          "mode": "raw",
          "raw": "{\n  \"txid\": \"abc123def456ghi789jkl01\",\n  \"valor\": { \"original\": \"150.00\" },\n  \"chave\": \"12345678909\",\n  \"recebedor\": { \"nome\": \"Licenciado Teste\" }\n}"
        }
      }
    }
  ],
  "variable": [
    { "key": "base_url", "value": "https://sandbox.sicoob.com.br/sicoob/sandbox/pix-pagamentos/v2" },
    { "key": "access_token", "value": "" }
  ]
}
```

Passos no Postman:
1. Importe a coleção acima.
2. Crie um ambiente e defina `access_token` com o token do sandbox.
3. Opcional: ajuste `base_url` se necessário.
4. Execute a requisição e verifique a resposta.

### 5) Alternativa: SPB Transferências (TED/TEF)

Se o PIX não for possível, use a API SPB (`/spb/v2`). O recurso e payload exatos dependem do produto contratado (TED/TEF) e podem diferir. Consulte o catálogo do Sicoob antes de testar. Exemplo conceitual:

```bash
ACCESS_TOKEN="{{SEU_ACCESS_TOKEN_SANDBOX}}"
SPB_BASE="https://sandbox.sicoob.com.br/sicoob/sandbox/spb/v2"

curl -X POST "$SPB_BASE/transferencias" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "valor": "150.00",
    "favorecido": {
      "cpfCnpj": "12345678909",
      "nome": "Licenciado Teste",
      "banco": "756",
      "agencia": "1234",
      "conta": "567890",
      "tipoConta": "CC"
    },
    "descricao": "Saque Licenciado #123"
  }'
```

Obs.: O corpo acima é ilustrativo; siga o contrato real do endpoint do SPB.

### 6) Integração com nosso backend (FazEnergy)

Nosso backend já possui um cliente mínimo para PIX Pagamentos do Sicoob. Para alinhar com a documentação do Sicoob:
- Configure a base no registro `PixConfig` como `https://sandbox.sicoob.com.br/sicoob/sandbox/pix-pagamentos/v2`.
- Use o token do sandbox em `access_token` (ou configure OAuth2 quando aplicável).
- O cliente envia `POST {{base_url}}/pagamentos` com JSON similar aos exemplos acima.

Se necessário, ajustaremos detalhes de endpoint/payload conforme o contrato final do Sicoob.

### 7) Boas práticas e dicas

- Gere `txid` único por pagamento (até 25 caracteres).
- Trate respostas 200/201/202 como sucesso em processamento; logue o payload.
- Em erros (4xx/5xx), registre `status` e corpo da resposta para diagnóstico.
- Sandbox não exige mTLS; produção geralmente exige mTLS e controle de escopos.










