from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from core.choices import *

# --------------------------------------------------------------------------------------------------
# USUÁRIO
# --------------------------------------------------------------------------------------------------
class User(AbstractUser):
    is_operator = models.BooleanField(default=False, verbose_name="É Operador?")
    is_affiliate = models.BooleanField(default=False, verbose_name="É Afiliado?")
    image_profile = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        verbose_name="Foto de Perfil"
    )

    #original de auth_user_groups do django
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',
        blank=True,
        verbose_name="Grupo de Usuários",
        db_table='tb_UserGroup'
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_set',
        blank=True,
        verbose_name="Permissões",
        db_table='tb_UserPermission'
    )

    class Meta:
        db_table = 'tb_User'
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.username
