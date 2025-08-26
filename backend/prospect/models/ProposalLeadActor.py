from django.db import models


class ProposalLeadActor(models.Model):
    ACTOR_CHOICES = [
        ('contractor', 'Contratante'),
        ('owner', 'Proprietário'),
        ('legal_responsible', 'Responsável Legal'),
    ]

    proposal = models.ForeignKey('contractor.Proposal', on_delete=models.CASCADE, related_name='lead_actors', verbose_name='Proposta')
    actor = models.CharField(max_length=20, choices=ACTOR_CHOICES, verbose_name='Ator')

    # Identificação
    legal_name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Razão Social')
    name = models.CharField(max_length=255, null=True, blank=True, verbose_name='Nome')
    cpf_cnpj = models.CharField(max_length=20, null=True, blank=True, verbose_name='CPF/CNPJ')

    # Contato
    cellphone = models.CharField(max_length=20, null=True, blank=True, verbose_name='Celular')
    email = models.EmailField(null=True, blank=True, verbose_name='E-mail')

    # Endereço
    zip_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='CEP')
    address = models.CharField(max_length=255, null=True, blank=True, verbose_name='Endereço')
    number = models.CharField(max_length=20, null=True, blank=True, verbose_name='Número')
    complement = models.CharField(max_length=255, null=True, blank=True, verbose_name='Complemento')
    neighborhood = models.CharField(max_length=255, null=True, blank=True, verbose_name='Bairro')
    city = models.CharField(max_length=255, null=True, blank=True, verbose_name='Cidade')
    st = models.CharField(max_length=2, null=True, blank=True, verbose_name='UF')

    class Meta:
        db_table = 'ContractorProposalLeadActor'
        verbose_name = 'Ator da Proposta'
        verbose_name_plural = 'Atores da Proposta'
        unique_together = [('proposal', 'actor')]
        indexes = [
            models.Index(fields=['proposal', 'actor']),
        ]

    def __str__(self):
        return f"{self.actor} - {self.proposal_id}"


