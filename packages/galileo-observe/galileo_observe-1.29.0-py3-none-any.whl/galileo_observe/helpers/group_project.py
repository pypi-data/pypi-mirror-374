from pydantic import UUID4

from galileo_core.helpers.group_project import list_group_project_collaborators as core_list_group_project_collaborators
from galileo_core.helpers.group_project import share_project_with_group as core_share_project_with_group
from galileo_core.helpers.group_project import unshare_project_with_group as core_unshare_project_with_group
from galileo_core.helpers.group_project import (
    update_group_project_collaborator as core_update_group_project_collaborator,
)
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.group_project import GroupProjectCollaboratorResponse
from galileo_observe.schema.config import ObserveConfig


def share_project_with_group(
    project_id: UUID4, group_id: UUID4, role: CollaboratorRole = CollaboratorRole.viewer
) -> GroupProjectCollaboratorResponse:
    config = ObserveConfig.get()
    return core_share_project_with_group(project_id=project_id, group_id=group_id, role=role, config=config)


def unshare_project_with_group(project_id: UUID4, group_id: UUID4) -> None:
    config = ObserveConfig.get()
    return core_unshare_project_with_group(project_id=project_id, group_id=group_id, config=config)


def list_group_project_collaborators(project_id: UUID4) -> list[GroupProjectCollaboratorResponse]:
    config = ObserveConfig.get()
    return core_list_group_project_collaborators(project_id=project_id, config=config)


def update_group_project_collaborator(
    project_id: UUID4, group_id: UUID4, role: CollaboratorRole = CollaboratorRole.viewer
) -> GroupProjectCollaboratorResponse:
    config = ObserveConfig.get()
    return core_update_group_project_collaborator(project_id=project_id, group_id=group_id, role=role, config=config)
