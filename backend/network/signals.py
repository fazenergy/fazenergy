# # backend/network/signals.py
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from core.models import Affiliate
# from .models import UnilevelNetwork

# @receiver(post_save, sender=Affiliate)
# def create_unilevel_structure(sender, instance, created, **kwargs):
#     """
#     Cria o vínculo na estrutura Unilevel quando um novo Affiliate é cadastrado com um indicador.
#     """
#     if created and instance.original_indicator:
#         # Cria o vínculo do nível 1 (direto)
#         UnilevelNetwork.objects.create(
#             parent_affiliate=instance.original_indicator,
#             child_affiliate=instance,
#             level=1
#         )
        
#         # Se quiser montar lógica para níveis indiretos, pode fazer aqui
#         # Exemplo básico para ilustrar:
#         """
#         parent_node = instance.original_indicator
#         level = 2
#         while parent_node.original_indicator:
#             UnilevelNetwork.objects.create(
#                 parent_affiliate=parent_node.original_indicator,
#                 child_affiliate=instance,
#                 level=level
#             )
#             parent_node = parent_node.original_indicator
#             level += 1
#         """
# # Nota: A lógica acima para níveis indiretos é apenas um exemplo.
# # Você pode expandir conforme a necessidade do seu modelo de negócios.  