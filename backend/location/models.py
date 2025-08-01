# location/models.py
from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100)
    iso_code = models.CharField(max_length=3, unique=True)

    class Meta:
        db_table = 'Country'
        verbose_name = "País"
        verbose_name_plural = "Países"

    def __str__(self):
        return self.name

class State(models.Model):
    name = models.CharField(max_length=100)
    uf = models.CharField(max_length=2)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')

    class Meta:
            db_table = 'State'
            verbose_name = "Estado"
            verbose_name_plural = "Estados"

    def __str__(self):
        return f"{self.uf} - {self.name}"


class City(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_capital = models.BooleanField(default=False)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    
    class Meta:
        db_table = 'City'
        verbose_name = "Cidade"
        verbose_name_plural = "Cidades"

    def __str__(self):
        return f"{self.name} - {self.state.uf}"
