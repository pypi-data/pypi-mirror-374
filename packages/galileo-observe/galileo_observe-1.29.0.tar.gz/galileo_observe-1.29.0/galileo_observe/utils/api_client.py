from importlib.metadata import version
from typing import Any, Optional

from galileo_core.constants.request_method import RequestMethod
from galileo_core.schemas.shared.scorers.scorer_configuration import ScorerConfiguration
from galileo_observe.constants.routes import Routes
from galileo_observe.schema.config import ObserveConfig
from galileo_observe.schema.project import ProjectSettings
from galileo_observe.schema.transaction import TransactionRecordBatch


class ApiClient:
    def __init__(self, project_name: str) -> None:
        self.project_id = None
        self.config = ObserveConfig.get()
        try:
            project = self.get_project_by_name(project_name)
            if project["type"] not in ["llm_monitor", "galileo_observe"]:
                raise Exception(f"Project {project_name} is not a Galileo Observe project")
            self.project_id = project["id"]
        except Exception as e:
            if "not found" in str(e):
                self.project_id = self.create_project(project_name)["id"]
                print(f"🚀 Creating new project... project {project_name} created!")
            else:
                raise e

    def _make_request(
        self,
        method: RequestMethod,
        path: str,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        return self.config.api_client.request(
            method=method, path=path, json=json, data=data, files=files, params=params
        )

    async def _make_async_request(
        self,
        method: RequestMethod,
        path: str,
        json: Optional[dict] = None,
        data: Optional[dict] = None,
        files: Optional[dict] = None,
        params: Optional[dict] = None,
    ) -> Any:
        return await self.config.api_client.arequest(
            method=method, path=path, json=json, data=data, files=files, params=params
        )

    async def ingest_batch(self, transaction_batch: TransactionRecordBatch) -> dict[str, str]:
        transaction_batch.client_version = version("galileo_observe")
        return await self._make_async_request(
            RequestMethod.POST,
            path=Routes.ingest.format(project_id=self.project_id),
            json=transaction_batch.model_dump(),
        )

    def get_project_by_name(self, project_name: str) -> Any:
        projects = self._make_request(
            RequestMethod.GET, path=Routes.projects.value, params={"project_name": project_name, "type": "llm_monitor"}
        )
        if len(projects) < 1:
            raise Exception(f"Galileo project {project_name} not found")
        return projects[0]

    def create_project(self, project_name: str) -> dict[str, str]:
        return self._make_request(
            RequestMethod.POST, path=Routes.projects.value, json={"name": project_name, "type": "llm_monitor"}
        )

    def update_project_settings(self, scorers_config: ScorerConfiguration) -> ProjectSettings:
        return self._make_request(
            RequestMethod.PATCH,
            path=Routes.project.format(project_id=self.project_id),
            json={"scorers_config": scorers_config.model_dump()},
        )

    def get_logged_data(
        self,
        start_time: Optional[str],
        end_time: Optional[str],
        chain_id: Optional[str],
        limit: Optional[int],
        offset: Optional[int],
        include_chains: Optional[bool],
        sort_spec: Optional[list[Any]],
        filters: Optional[list[Any]],
        columns: Optional[list[str]],
        redact: Optional[bool] = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        if chain_id is not None:
            params["chain_id"] = chain_id
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if include_chains is not None:
            params["include_chains"] = include_chains
        if redact is not None:
            params["redact"] = redact

        body: dict[str, Any] = {}
        if filters is not None:
            body["filters"] = filters
        if sort_spec is not None:
            body["sort_spec"] = sort_spec
        if columns is not None:
            body["columns"] = columns

        return self._make_request(
            RequestMethod.POST, path=Routes.rows.format(project_id=self.project_id), params=params, json=body
        )

    def delete_logged_data(self, filters: list[dict]) -> dict[str, Any]:
        return self._make_request(
            RequestMethod.POST, path=Routes.delete.format(project_id=self.project_id), json=dict(filters=filters)
        )

    def get_metrics(
        self,
        start_time: str,
        end_time: str,
        interval: Optional[int],
        group_by: Optional[str],
        filters: Optional[list[Any]],
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"start_time": start_time, "end_time": end_time}
        if interval is not None:
            params["interval"] = interval
        if group_by is not None:
            params["group_by"] = group_by

        body: dict[str, Any] = {}
        if filters is not None:
            body["filters"] = filters

        return self._make_request(
            RequestMethod.POST, path=Routes.metrics.format(project_id=self.project_id), params=params, json=body
        )
