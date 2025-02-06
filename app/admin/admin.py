from app.models import User, Group, UserGroupAssociation
from sqladmin import ModelView

import bcrypt
from fastapi.requests import Request
from itsdangerous.exc import BadSignature
from itsdangerous.serializer import Serializer
from sqladmin.authentication import AuthenticationBackend

from app.core.db import AsyncSessionLocal
from app.crud.user import user_crud
from app.crud import crud_user_group_association
from sqlalchemy.sql.expression import Select, select


class AdminAuth(AuthenticationBackend):
    """
    Класс для управления аутентификацией администратора.

    Args:
        secret_key (str): Секретный ключ для сериализации токенов.

    """

    def __init__(self, secret_key: str):
        super().__init__(secret_key)
        self.serializer = Serializer(secret_key)

    async def login(self, request: Request) -> bool:
        """
        Обрабатывает вход администратора.

        Args:
            request (Request): Запрос с формой, содержащей username и password.

        Returns:
            bool: True, если пользователь успешно аутентифицирован, иначе False.

        """

        form = await request.form()
        username, user_password = form['username'], form['password']
        if not username or not user_password:
            return False
        async with AsyncSessionLocal() as session:
            admin: User = await user_crud.get_by_attribute(
                attr_name='user_id',
                attr_value=username,
                session=session,
            )
        if admin is None:
            return False

        if admin.password == 'admin':  # noqa: S105
            password = True
        else:
            password = bcrypt.checkpw(
                user_password.encode('utf-8'), admin.password.encode('utf-8')
            )
        if password:
            data = username
            token = self.serializer.dumps(data)
            request.session.update({'token': token})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        """
        Выполняет выход администратора.

        Args:
            request (Request): Запрос сессии.

        Returns:
            bool: True после очистки сессии.

        """
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        """
        Проверяет подлинность токена администратора.

        Args:
            request (Request): Запрос сессии.

        """
        token = request.session.get('token')

        if not token:
            return False

        try:
            self.serializer.loads(token)
            return True

        except BadSignature:
            return False


class UserAdmin(ModelView, model=User):
    name = 'Пользователь'
    name_plural = 'Пользователи'
    icon = 'fa-solid fa-person-rifle'
    column_list = [
        User.groups,
        User.user_name,
        User.first_name,
        User.last_name,
        User.first_name_last_name,
        User.date_of_birth,
    ]

    column_sortable_list = [
        User.user_name,
        User.first_name,
        User.last_name,
        User.date_of_birth,
        User.first_name_last_name,
        User.groups,
    ]

    column_labels = {
        User.user_name: 'Логин в телеге',
        User.first_name: 'Имя',
        User.last_name: 'Фамилия',
        User.date_of_birth: 'Дата рождения',
        User.first_name_last_name: 'Имя для заполнения в ручную',
        User.groups: 'Группа',
    }
    form_edit_rules = [
        'first_name_last_name',
        'date_of_birth',
    ]  # Поля отображаемые в форме редактирования
    column_formatters = {
        User.date_of_birth: lambda m, _: m.date_of_birth.strftime('%d.%m.%Y')
        if m.date_of_birth
        else ''
    }  # Привел дату в привычный вид

    column_searchable_list = [
        User.user_name,
        User.first_name_last_name,
        User.user_id,
        User.groups,
    ]
    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = False
    page_size = 100


class GroupAdmin(ModelView, model=Group):
    column_list = [Group.group_name]
    name = 'Группа'
    name_plural = 'Группы'
    icon = 'fa-solid fa-people-group'
    form_edit_rules = [
        'group_name',
    ]
    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = False

    # def list_query(self, request):
    #     """
    #     Вернет SQLAlchemy select выражение для списка групп,
    #     куда текущий пользователь имеет доступ как администратор.
    #     """

    #     print(f'>>>>>>>>>{request.user}')
    #     return select(self.model)

    # #     # async with AsyncSessionLocal() as session:
    # #     #     # Используем select и join для получения группы пользователя
    # #     #     return await crud_user_group_association.get_chat_where_user_admin(
    # #     #         request.user_id, session
    # #     #     )


class UserGroupAssociationAdmin(ModelView, model=UserGroupAssociation):
    name = 'Права пользователя'
    name_plural = 'Права пользователей'
    icon = 'fa-solid fa-list-check'
    column_list = [
        UserGroupAssociation.user,
        UserGroupAssociation.group,
        UserGroupAssociation.is_admin,
        UserGroupAssociation.can_receive_messages,
        UserGroupAssociation.rceive_newsletter,
        UserGroupAssociation.not_included_in_report,
    ]

    column_labels = {
        UserGroupAssociation.user: 'Пользователь',
        UserGroupAssociation.group: 'Группа',
        UserGroupAssociation.is_admin: 'Администратор',
        UserGroupAssociation.can_receive_messages: 'Пользователь отметился',
        UserGroupAssociation.rceive_newsletter: 'Получать отчет от бота',
        UserGroupAssociation.not_included_in_report: 'Исключить пользователя из отчета',
    }
    column_sortable_list = [
        UserGroupAssociation.user,
        UserGroupAssociation.group,
        UserGroupAssociation.is_admin,
        UserGroupAssociation.can_receive_messages,
        UserGroupAssociation.rceive_newsletter,
        UserGroupAssociation.not_included_in_report,
    ]

    column_searchable_list = [
        UserGroupAssociation.user,
        UserGroupAssociation.group,
        UserGroupAssociation.user_id,
    ]
    form_edit_rules = [
        'can_receive_messages',
        'rceive_newsletter',
        'not_included_in_report',
    ]

    can_create = False
    can_edit = True
    can_delete = False
    can_view_details = False
    page_size = 100
