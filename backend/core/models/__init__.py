# core/models/__init__.py

# Modelos de autenticação
from .User import User
from django.contrib.auth.models import Group, Permission 

# Perfis/roles
from .Licensed import Licensed
from .Operator import Operator  
# from .auth_customer import Customer  # descomente quando existir

__all__ = [
    "User",
    "Group",
    "Permission",
    "Licensed",
    "Operator",
    # "Customer",
]
