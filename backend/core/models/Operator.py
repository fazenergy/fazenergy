from django.db import models
from django.conf import settings
from core.choices import *

# #################################################################################################
# Tabela Detalhes de Usuarios do tipo Operador: endereço, telefone, etc
# #################################################################################################
class Operator(models.Model):
    username            = models.CharField(max_length=150, unique=True, verbose_name="Operador")
    user                = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Login Operador")
    cpf_cnpj            = models.CharField(max_length=20, unique=True, verbose_name="CPF/CNPJ")
    gender              = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')], verbose_name="Sexo")
    birth_date          = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")
    marital_status      = models.CharField(max_length=20, choices=[('single', 'Solteiro(a)'), ('married', 'Casado(a)'), ('divorced', 'Divorciado(a)')], verbose_name="Estado Civil")
    id_document_number  = models.CharField(max_length=50, blank=True, null=True, verbose_name="RG")
    id_document_issuer  = models.CharField(max_length=20, blank=True, null=True, verbose_name="Órgão Emissor")
    
    city_lookup         = models.ForeignKey('location.City', on_delete=models.SET_NULL, null=True, blank=True)
            
    cep                 = models.CharField(max_length=8, blank=True, null=True, verbose_name="CEP")
    address             = models.CharField(max_length=300, blank=True, null=True, verbose_name="Endereço")
    number              = models.CharField(max_length=8, blank=True, null=True, verbose_name="Número")
    complement          = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    district            = models.CharField(max_length=300, blank=True, null=True, verbose_name="Bairro")
    phone               = models.CharField(max_length=14, blank=True, null=True, verbose_name="Telefone")
    comment             = models.TextField(blank=True, null=True, verbose_name="Comentário")
    user_permission_type = models.CharField(max_length=50, blank=True, null=True, verbose_name="Permissão do Usuário") # TO DO ENTENDER DO QUE SE TRATA
    stt_record          = models.BooleanField(default=True, verbose_name="Ativo")
    dtt_record          = models.DateTimeField(auto_now_add=True, verbose_name="Data Cadastro")
    dtt_update          = models.DateTimeField(auto_now=True, verbose_name="Data Atualização")

    class Meta:
        db_table = 'Operator'
        verbose_name = "Operador"
        verbose_name_plural = "Operadores"

    def __str__(self):
        return self.username
