# core/models/CoreGroup.py
from django.contrib.auth.models import Group


class CoreGroup(Group):
    """
    Proxy model para Group que aparece na seção Core do admin
    """
    class Meta:
        proxy = True
        verbose_name = "Grupo de Usuários"
        verbose_name_plural = "Grupos de Usuários"
        app_label = 'core'
        
    def __str__(self):
        return f"Grupo: {self.name}"

    def save(self, *args, **kwargs):
        # Garante que o proxy model funcione corretamente
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Garante que o proxy model funcione corretamente
        super().delete(*args, **kwargs)
