from app.models.user import User
from app.crud.base import CRUDBase


class CRUDUser(CRUDBase):
    pass


user_crud = CRUDUser(User)
