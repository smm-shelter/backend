# порядок импортов здесь - это порядок списка моделей

# управление менеджерами
from src.admin.models.manager import ManagerAdmin
from src.admin.models.news import NewsAdmin
from src.admin.models.pet import PetAdmin
from src.admin.models.transaction import TransactionAdmin
from src.admin.models.pet_status import PetStatusAdmin
from src.admin.models.pet_type import PetTypeAdmin

__all__ = [
    "ManagerAdmin",
    "NewsAdmin",
    "PetAdmin",
    "TransactionAdmin",
    "PetStatusAdmin",
    "PetTypeAdmin",
]