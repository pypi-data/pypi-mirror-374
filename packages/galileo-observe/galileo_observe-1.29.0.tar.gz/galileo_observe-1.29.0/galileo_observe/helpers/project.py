from typing import Optional

from pydantic import UUID4

from galileo_core.helpers.project import get_project as core_get_project
from galileo_core.helpers.project import get_projects
from galileo_core.helpers.project import update_project as core_update_project
from galileo_core.schemas.core.project import ProjectResponse, ProjectType
from galileo_core.schemas.shared.scorers.scorer_configuration import ScorerConfiguration
from galileo_observe.schema.config import ObserveConfig
from galileo_observe.schema.project import ProjectSettings
from galileo_observe.utils.api_client import ApiClient


def list_projects(project_type: Optional[ProjectType] = None) -> list[ProjectResponse]:
    config = ObserveConfig.get()
    return get_projects(project_type=project_type, config=config)


def get_project(project_id: Optional[UUID4] = None, project_name: Optional[str] = None) -> Optional[ProjectResponse]:
    config = ObserveConfig.get()
    return core_get_project(
        project_id=project_id, project_name=project_name, project_type=ProjectType.llm_monitor, config=config
    )


def update_project(project_id: UUID4, project_name: str) -> ProjectResponse:
    config = ObserveConfig.get()
    return core_update_project(project_id=project_id, project_name=project_name, config=config)


def update_project_settings(project_name: str, scorers_config: ScorerConfiguration) -> ProjectSettings:
    api_client = ApiClient(project_name=project_name)
    return api_client.update_project_settings(scorers_config)
