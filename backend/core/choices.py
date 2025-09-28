# Choices para Gender
GENDER_CHOICES = [
    ('M', 'Male'),
    ('F', 'Female'),
    ('O', 'Other'),
]

# Choices para Marital Status
MARITAL_STATUS_CHOICES = [
    ('single', 'Single'),
    ('married', 'Married'),
    ('divorced', 'Divorced'),
    ('widowed', 'Widowed'),
    ('separated', 'Separated'),
    ('other', 'Other'),
]

# Choices para tipos de documentos de Licensed
DOCUMENT_TYPE_CHOICES = [
    ('cpf', 'CPF'),
    ('rg', 'RG'),
    ('comprovante_endereco', 'Comprovante de Endereço'),
    ('pis', 'PIS'),
    # Empresa (PJ)
    ('cnpj_card', 'Cartão CNPJ'),
    ('social_contract', 'Contrato Social'),
]

# Choices para status de validação de documentos
DOCUMENT_STATUS_CHOICES = [
    ('pending', 'Pendente'),
    ('rejected', 'Reprovado'),
    ('approved', 'Aprovado'),
]

# Owner type para LicensedDocument
DOCUMENT_OWNER_TYPE_CHOICES = [
    ('pf', 'Pessoa Física'),
    ('pj', 'Pessoa Jurídica'),
]