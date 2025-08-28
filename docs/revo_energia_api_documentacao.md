# Revo Energia API - DocumentaÃ§Ã£o Completa com Schemas

## ð AutenticaÃ§Ã£o

### Endpoint
```
POST https://sandbox.revoenergia.com.br/api/partners/auth
```

### Headers
- Authorization: Basic <username:password>

### Exemplo de requisiÃ§Ã£o (cURL)
```bash
curl --location --request POST 'https://sandbox.revoenergia.com.br/api/partners/auth'
```

### Exemplo de resposta
```json
{
  "success": true,
  "data": [
    {
      "token": "31|tVbTPeUHAm1PgcLbr8pj5QdWrE4qaIxsUOk1Mgcq2867fd75"
    }
  ],
  "message": ["OperaÃ§Ã£o realizada com sucesso."]
}
```

---

## ð Consulta CEP

### Endpoint
```
GET https://sandbox.revoenergia.com.br/api/partners/v3/cep/{zipcode}/{propertyType?}
```

### Headers
- Authorization: Bearer <token>

### Exemplo de requisiÃ§Ã£o (cURL)
```bash
curl --location 'https://sandbox.revoenergia.com.br/api/partners/v3/cep/44444444/casa'
```

### Exemplo de resposta
```json
{
  "success": true,
  "data": [
    {
      "id": 11,
      "name": "COELBA",
      "tariff_type": "RES / COM"
    }
  ],
  "message": ["OperaÃ§Ã£o realizada com sucesso."]
}
```

---

## âï¸ SimulaÃ§Ã£o - CriaÃ§Ã£o

### Endpoint
```
POST https://sandbox.revoenergia.com.br/api/partners/v3/simulation
```

### Headers
- Authorization: Bearer <token>
- Content-Type: application/json

### Exemplo de body
```json
{
  "property_type": "Casa",
  "zip_code": "06663460",
  "electric_bill": 503.91,
  "consumer_unit": "A300000",
  "consumer_group": "B1",
  "cellphone": "92976517529",
  "contract_person": "PF",
  "owner": "PrÃ³prio",
  "fiscal_number": "99999999999",
  "seller_email": "vendedor@gmail.com",
  "energy_provider_id": 1,
  "monthly_consumption": {
    "january": 320,
    "february": 280,
    "march": 310,
    "april": 290,
    "may": 330,
    "june": 340,
    "july": 360,
    "august": 350,
    "september": 300,
    "october": 310,
    "november": 295,
    "december": 325
  },
  "lead_actors": [
    {
      "actor": "contractor",
      "legal_name": "SmartTech S.A.",
      "name": "Bruna Silva",
      "cellphone": "99999999999",
      "email": "mhs@gmail.com",
      "zip_code": "99999999",
      "address": "Rua dos Navegantes",
      "number": "150",
      "complement": "AP 503",
      "neighborhood": "Margarida",
      "city": "Canoas",
      "st": "RS"
    },
    {
      "actor": "owner",
      "name": "Richard Santos",
      "cellphone": "99999999999",
      "email": "mhs@gmail.com",
      "cpf": "99999999999",
      "zip_code": "99999999",
      "address": "Rua das Tulipas",
      "number": "548",
      "complement": "AP 504",
      "neighborhood": "Fluvial",
      "city": "Atlas",
      "st": "SP"
    },
    {
      "actor": "legal_responsible",
      "name": "AnastÃ¡cio Teste",
      "cellphone": "99999999999",
      "email": "mhs@gmail.com",
      "cpf": "99999999999",
      "zip_code": "99999999",
      "address": "Rua das LamentaÃ§Ãµes",
      "number": "569",
      "complement": "AP 12",
      "neighborhood": "Pastoreio",
      "city": "Atlas",
      "st": "SP"
    }
  ]
}
```

```json
{
  "success": true,
  "data": [
    {
      "reference": "17492391003481478",
      "contract_type": "Revo Simples",
      "contract_duration": 12,
      "property_type": "Casa",
      "electric_bill": {
        "value": "503.91",
        "consumer_unit": null,
        "consumer_group": null
      },
      "installation_address": {
        "zip_code": "06663-460",
        "address": "Alaide Silveira de Barcelos",
        "number": "18",
        "complement": "Quadra B",
        "neighborhood": "SÃ£o JoÃ£o do Rio Vermelho",
        "city": "FlorianÃ³polis",
        "st": "SP"
      },
      "option_plans": [
        {
          "contract_duration": 6,
          "discount_percentage": 10,
          "energy_revo_costs": 360.81
        },
        {
          "contract_duration": 8,
          "discount_percentage": 8,
          "energy_revo_costs": 360.81
        },
        {
          "contract_duration": 10,
          "discount_percentage": 7,
          "energy_revo_costs": 360.81
        },
        {
          "contract_duration": 12,
          "discount_percentage": 10,
          "energy_revo_costs": 360.81
        }
      ],
      "discount_percentage": 3.43,
      "energy_provider_electric_bill": "503.91",
      "discount_amount": 17.27,
      "energy_provider_costs": 503.91,
      "energy_revo_costs": 360.81,
      "energy_provider_id": 32,
      "energy_provider_name": "ENEL SP",
      "economy_thirty_years": 148124.64,
      "kwp": 5.16,
      "kWh_annual": 7004.46,
      "required_area": 31,
      "quantity_modules": 10,
      "proposal_expiration_date": "2025-06-21T19:45:00.000000Z"
    }
  ],
  "message": ["OperaÃ§Ã£o realizada com sucesso."]
}
```

### Exemplo de resposta
```json
{
  "property_type": "Casa",
  "zip_code": "06663460",
  "electric_bill": 503.91,
  "consumer_unit": "A300000",
  "consumer_group": "B1",
  "cellphone": "92976517529",
  "contract_person": "PF",
  "owner": "PrÃ³prio",
  "fiscal_number": "99999999999",
  "seller_email": "vendedor@gmail.com",
  "energy_provider_id": 1,
  "monthly_consumption": {
    "january": 320,
    "february": 280,
    "march": 310,
    "april": 290,
    "may": 330,
    "june": 340,
    "july": 360,
    "august": 350,
    "september": 300,
    "october": 310,
    "november": 295,
    "december": 325
  },
  "lead_actors": [
    {
      "actor": "contractor",
      "legal_name": "SmartTech S.A.",
      "name": "Bruna Silva",
      "cellphone": "99999999999",
      "email": "mhs@gmail.com",
      "zip_code": "99999999",
      "address": "Rua dos Navegantes",
      "number": "150",
      "complement": "AP 503",
      "neighborhood": "Margarida",
      "city": "Canoas",
      "st": "RS"
    },
    {
      "actor": "owner",
      "name": "Richard Santos",
      "cellphone": "99999999999",
      "email": "mhs@gmail.com",
      "cpf": "99999999999",
      "zip_code": "99999999",
      "address": "Rua das Tulipas",
      "number": "548",
      "complement": "AP 504",
      "neighborhood": "Fluvial",
      "city": "Atlas",
      "st": "SP"
    },
    {
      "actor": "legal_responsible",
      "name": "AnastÃ¡cio Teste",
      "cellphone": "99999999999",
      "email": "mhs@gmail.com",
      "cpf": "99999999999",
      "zip_code": "99999999",
      "address": "Rua das LamentaÃ§Ãµes",
      "number": "569",
      "complement": "AP 12",
      "neighborhood": "Pastoreio",
      "city": "Atlas",
      "st": "SP"
    }
  ]
}
```

```json
{
  "success": true,
  "data": [
    {
      "reference": "17492391003481478",
      "contract_type": "Revo Simples",
      "contract_duration": 12,
      "property_type": "Casa",
      "electric_bill": {
        "value": "503.91",
        "consumer_unit": null,
        "consumer_group": null
      },
      "installation_address": {
        "zip_code": "06663-460",
        "address": "Alaide Silveira de Barcelos",
        "number": "18",
        "complement": "Quadra B",
        "neighborhood": "SÃ£o JoÃ£o do Rio Vermelho",
        "city": "FlorianÃ³polis",
        "st": "SP"
      },
      "option_plans": [
        {
          "contract_duration": 6,
          "discount_percentage": 10,
          "energy_revo_costs": 360.81
        },
        {
          "contract_duration": 8,
          "discount_percentage": 8,
          "energy_revo_costs": 360.81
        },
        {
          "contract_duration": 10,
          "discount_percentage": 7,
          "energy_revo_costs": 360.81
        },
        {
          "contract_duration": 12,
          "discount_percentage": 10,
          "energy_revo_costs": 360.81
        }
      ],
      "discount_percentage": 3.43,
      "energy_provider_electric_bill": "503.91",
      "discount_amount": 17.27,
      "energy_provider_costs": 503.91,
      "energy_revo_costs": 360.81,
      "energy_provider_id": 32,
      "energy_provider_name": "ENEL SP",
      "economy_thirty_years": 148124.64,
      "kwp": 5.16,
      "kWh_annual": 7004.46,
      "required_area": 31,
      "quantity_modules": 10,
      "proposal_expiration_date": "2025-06-21T19:45:00.000000Z"
    }
  ],
  "message": ["OperaÃ§Ã£o realizada com sucesso."]
}
```

---

## ð SimulaÃ§Ã£o - AtualizaÃ§Ã£o

### Endpoint
```
PUT https://sandbox.revoenergia.com.br/api/partners/v3/simulation
```

### Headers
- Authorization: Bearer <token>
- Content-Type: application/json

### Body e resposta disponÃ­veis na mesma estrutura da criaÃ§Ã£o, com obrigatoriedade do campo `reference`.

> DocumentaÃ§Ã£o finalizada com todos os endpoints conhecidos da API Revo Energia.
