from app.models.user_group_association import UserGroupAssociation
from app.crud.base import CRUDBase


class CRUDUserGroupAssociation(CRUDBase):
    pass


crud_user_group_association = CRUDUserGroupAssociation(UserGroupAssociation)
