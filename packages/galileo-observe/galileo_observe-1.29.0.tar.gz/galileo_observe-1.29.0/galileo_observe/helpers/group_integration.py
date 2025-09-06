from pydantic import UUID4

from galileo_core.helpers.group_integration import (
    delete_group_integration_collaborator as core_delete_group_integration_collaborator,
)
from galileo_core.helpers.group_integration import (
    list_group_integration_collaborators as core_list_group_integration_collaborators,
)
from galileo_core.helpers.group_integration import (
    update_group_integration_collaborator as core_update_group_integration_collaborator,
)
from galileo_core.schemas.core.collaboration_role import CollaboratorRole
from galileo_core.schemas.core.integration.group_integration import GroupIntegrationCollaboratorResponse
from galileo_observe.schema.config import ObserveConfig


def list_group_integration_collaborators(integration_id: UUID4) -> list[GroupIntegrationCollaboratorResponse]:
    config = ObserveConfig.get()
    return core_list_group_integration_collaborators(integration_id=integration_id, config=config)


def update_group_integration_collaborator(
    integration_id: UUID4, group_id: UUID4, role: CollaboratorRole = CollaboratorRole.viewer
) -> GroupIntegrationCollaboratorResponse:
    config = ObserveConfig.get()
    return core_update_group_integration_collaborator(
        integration_id=integration_id, group_id=group_id, role=role, config=config
    )


def delete_group_integration_collaborator(integration_id: UUID4, group_id: UUID4) -> None:
    config = ObserveConfig.get()
    return core_delete_group_integration_collaborator(integration_id=integration_id, group_id=group_id, config=config)
