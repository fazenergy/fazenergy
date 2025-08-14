from django.db import models
from django.conf import settings
from core.choices import *
from collections import deque
from django.utils import timezone

# #################################################################################################
# Tabela de Detalhes de Usuarios do tipo licensed: endereço, plano, carreira, etc
#################################################################################################
class Licensed(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Login desse Licenciado")

    original_indicator = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, 
        blank=True, related_name='referrals', verbose_name="Indicado por")
    
    person_type = models.CharField(
        max_length=2,
        choices=[('pf', 'PF'), ('pj', 'PJ')] # TO DO: levar pro dicionario de choices.py depois
    , verbose_name="Pessoa")

    cpf_cnpj    = models.CharField(max_length=20, unique=True, verbose_name="CPF/CNPJ")
    cep         = models.CharField(max_length=8, blank=True, null=True, verbose_name="CEP")

    city_lookup = models.ForeignKey('location.City', on_delete=models.SET_NULL, null=True, blank=True)
        
    address     = models.CharField(max_length=300, blank=True, null=True, verbose_name="Endereço")
    number      = models.CharField(max_length=8, blank=True, null=True, verbose_name="Número")
    complement  = models.CharField(max_length=100, blank=True, null=True, verbose_name="Complemento")
    district    = models.CharField(max_length=300, blank=True, null=True, verbose_name="Bairro")
    phone       = models.CharField(max_length=14, blank=True, null=True, verbose_name="Telefone")

    plan        = models.ForeignKey('plans.Plan', on_delete=models.PROTECT, verbose_name="Plano") # 

     # FK - Conecta com PlanCareer
    previous_career = models.ForeignKey(
        'plans.PlanCareer',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='previous_licensed',
        verbose_name="Carreira Anterior")

    current_career = models.ForeignKey(
        'plans.PlanCareer',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='current_licensed',
        verbose_name="Carreira Atual")

    dtt_previous_career     = models.DateTimeField(blank=True, null=True, verbose_name="Data Carreira Anterior")
    dtt_current_career      = models.DateTimeField(blank=True, null=True, verbose_name="Data Carreira Atual")

    is_root                 = models.BooleanField(default=False, verbose_name="É Raiz ? ")
    root_network_name       = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nome Rede Raiz")
    stt_record              = models.BooleanField(default=True, verbose_name="Ativo")
    is_in_network           = models.BooleanField(default=True, verbose_name="Está na Rede ?")
    accept_lgpd             = models.BooleanField(default=False, verbose_name="Aceita LGPD")
    comment                 = models.TextField(blank=True, null=True, verbose_name="Comentário")
    dtt_activation          = models.DateTimeField(default=timezone.now, verbose_name="Data Ativação")
    dtt_payment_received    = models.DateTimeField(blank=True, null=True, verbose_name="Data Recebimento Pagamento")

    dynamic_compression     = models.BooleanField(default=False, verbose_name="Compressão Dinâmica Ativa")  # Indica se o afiliado está com compressão dinâmica ativada (relacionado ao pagamento anual, se estiver em dia então ativa se naõ desativa)
    dtt_record              = models.DateTimeField(auto_now_add=True, verbose_name="Data Cadastro")
    dtt_update              = models.DateTimeField(auto_now=True, verbose_name="Data Atualização")

    class Meta:
        db_table = 'Licensed'
        verbose_name = "Licenciado"
        verbose_name_plural = "Licenciados"

    def __str__(self):
        return f'{self.user.username} ({self.cpf_cnpj})'



    # #################################################################################################
    # Métodos para verificar e atualizar plano de carreira do licenciado 
    # #################################################################################################
    def verificar_plano_de_carreira(self):
        print(f"\nLICENCIADO: {self.user.username} ###########")

        # dessa forma para evitar import circular
        from django.apps import apps 
        PlanCareer = apps.get_model('plans', 'PlanCareer')
        planos = PlanCareer.objects.filter(stt_record=True).order_by('required_points')
        # -------------------------------------------

        carreira_atual = self.current_career.required_points if self.current_career else 0

        for plano in planos:
            if carreira_atual >= plano.required_points:
                continue

            diretos = list(self.get_indicados_diretos_efetivados())
            qtd_diretos = len(diretos)
            if qtd_diretos < plano.required_directs:
                faltam = plano.required_directs - qtd_diretos
                print(f"Faltam {faltam} diretos para estágio {plano.stage_name}")
                break

            vendas_diretas = sum(1 for d in diretos if d.comprou_usina())
            if vendas_diretas < plano.required_direct_sales:
                faltam = plano.required_direct_sales - vendas_diretas
                print(f"Faltam {faltam} vendas diretas para estágio {plano.stage_name}")
                break

            pontos_equipe = 0
            fila = deque([(d, 1) for d in diretos])
            while fila:
                dist, nivel = fila.popleft()
                total = dist.get_total_pontos_acumulados_consolidados()
                pontos_equipe += min(total, plano.max_pml_per_line)
                if nivel < 5:
                    for net in dist.get_indicados_diretos_efetivados():
                        fila.append((net, nivel + 1))

            print(f"Pontos de equipe (PML={plano.max_pml_per_line}): {pontos_equipe}")
            if pontos_equipe < plano.required_points:
                faltam = plano.required_points - pontos_equipe
                print(f"Faltam {faltam} pontos para estágio {plano.stage_name}")
                break

            print(f"Parabéns! Qualificado para {plano.stage_name} — Prêmio: {plano.reward_description}")

            self.previous_career = self.current_career
            self.current_career = plano
            self.dtt_previous_career = self.dtt_current_career
            self.dtt_current_career = timezone.now()
            self.save(update_fields=['previous_career', 'current_career', 'dtt_previous_career', 'dtt_current_career'])
            break




