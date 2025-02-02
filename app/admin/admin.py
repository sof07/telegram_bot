from app.models import User, Group, UserGroupAssociation
from sqladmin import ModelView


class UserAdmin(ModelView, model=User):
    column_list = '__all__'

    column_formatters = {User.user_name: lambda m, a: m.user_name[:10]}
    column_sortable_list = [
        User.user_id,
        User.user_name,
    ]
    name = 'Пользователь'
    name_plural = 'Пользователи'
    icon = 'fa-solid fa-user'
    column_details_list = [User.user_id, User.user_name]
    form_columns = [User.user_name, User.first_name, User.last_name]


class GroupAdmin(ModelView, model=Group):
    column_list = '__all__'

    name = 'Группа'
    name_plural = 'Группы'


class UserGroupAssociationAdmin(ModelView, model=UserGroupAssociation):
    column_list = '__all__'
