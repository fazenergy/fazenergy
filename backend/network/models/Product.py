from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name='Nome do Produto')
    dtt_record = models.DateTimeField(auto_now_add=True, verbose_name='Data Cadastro')
    dtt_update = models.DateTimeField(auto_now=True, verbose_name='Data Atualização')

    class Meta:
        db_table = 'Product'
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'

    def __str__(self) -> str:
        return self.name

