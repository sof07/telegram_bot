import bcrypt
import logging
from datetime import datetime
from fastapi.requests import Request
from itsdangerous.exc import BadSignature
from itsdangerous.serializer import Serializer
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.orm import aliased
from sqlalchemy.sql import select

from app.core.db import AsyncSessionLocal
from app.crud.user import user_crud
from app.models import Group, User, UserGroupAssociation
from app.core.config import settings


def is_super_admin(user_id: int) -> bool:
    if int(user_id) == int(settings.super_admin):
        return True


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
            logging.info(f'Пользователь {username} вошел в админку в {datetime.now()}')
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
        User.first_name_last_name: 'Здесь можно поменять имя пользователю',
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

    def list_query(self, request):
        """
        Вернет SQLAlchemy select выражение для списка групп,
        куда текущий пользователь имеет доступ как администратор.
        """

        token = request.session.get('token')
        user_id = token.split('.')[0].replace(
            '"', ''
        )  # ID пользователя который вошел в админку
        if is_super_admin(user_id):
            self.can_create = True
            self.can_delete = True
            self.can_view_details = True
            return select(self.model)

        user_group_alias = aliased(UserGroupAssociation)

        # Подзапрос: выбираем группы, где текущий пользователь является админом
        admin_groups_subquery = (
            select(user_group_alias.group_id)
            .where(
                user_group_alias.user_id == user_id,
                user_group_alias.is_admin.is_(True),
            )
            .subquery()
        )

        # Запрос: выбираем всех пользователей, состоящих в этих группах
        query = (
            select(User)
            .join(User.groups)  # Связь через отношение `groups` в модели User
            .where(UserGroupAssociation.group_id.in_(admin_groups_subquery))
        )

        return query


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
    can_delete = True
    can_view_details = False

    def is_visible(self, request: Request) -> bool:
        token = request.session.get('token')
        user_id = token.split('.')[0].replace('"', '')
        if is_super_admin(user_id):
            return True


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
        UserGroupAssociation.is_admin: 'Является админом в группе',
        UserGroupAssociation.can_receive_messages: 'Пользователь отметился',
        UserGroupAssociation.rceive_newsletter: 'Получать отчет от бота',
        UserGroupAssociation.not_included_in_report: 'Не учитывать в отчете',
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

    def list_query(self, request):
        """
        Вернет SQLAlchemy select выражение для списка групп,
        куда текущий пользователь имеет доступ как администратор.
        """

        token = request.session.get('token')
        user_id = token.split('.')[0].replace(
            '"', ''
        )  # ID пользователя который вошел в админку
        if is_super_admin(user_id):
            self.can_create = True
            self.can_delete = True
            self.can_view_details = True
            return select(self.model)

        user_group_alias = aliased(self.model)

        # Выбираем группы, где текущий пользователь является админом
        admin_groups_subquery = (
            select(user_group_alias.group_id)
            .where(
                user_group_alias.user_id == user_id, user_group_alias.is_admin.is_(True)
            )
            .subquery()
        )

        # Выбираем пользователей из этих групп
        query = select(self.model).where(self.model.group_id.in_(admin_groups_subquery))

        return query
