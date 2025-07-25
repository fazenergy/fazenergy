# core/models/__init__.py

# Modelos de autenticação
from .user_manager import User
from django.contrib.auth.models import Group, Permission 

# Perfis/roles
from .affiliate import Affiliate
from .operations_manager import OperationsManager  
# from .auth_customer import Customer  # descomente quando existir

__all__ = [
    "User",
    "Group",
    "Permission",
    "Affiliate",
    "OperationsManager",  # ou "Operator"
    # "Customer",
]
