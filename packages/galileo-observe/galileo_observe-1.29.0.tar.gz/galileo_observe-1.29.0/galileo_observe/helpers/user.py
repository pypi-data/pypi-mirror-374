from typing import Optional

from pydantic import UUID4

from galileo_core.helpers.user import get_current_user as core_get_current_user
from galileo_core.helpers.user import invite_users as core_invite_users
from galileo_core.helpers.user import list_users as core_list_users
from galileo_core.schemas.core.user import User
from galileo_core.schemas.core.user_role import UserRole
from galileo_observe.schema.config import ObserveConfig


def get_current_user() -> User:
    config = ObserveConfig.get()
    return core_get_current_user(config=config)


def invite_users(emails: list[str], role: UserRole = UserRole.user, group_ids: Optional[list[UUID4]] = None) -> None:
    config = ObserveConfig.get()
    return core_invite_users(emails=emails, role=role, group_ids=group_ids, config=config)


def list_users() -> list[User]:
    config = ObserveConfig.get()
    return core_list_users(config=config)
