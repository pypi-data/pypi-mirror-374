"""
Copyright (C) 2022-2024 Stella Technologies (UK) Limited.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

from typing import Dict, List, Optional

import httpx

from stellanow_api_internals.clients.base_api_client import StellanowBaseAPIClient
from stellanow_api_internals.core.enums import CreateOrUpdateTypes, FilterIncludeArchived, FilterIncludeInactive
from stellanow_api_internals.datatypes.workflow_mgmt import (
    StellaEntity,
    StellaEntityCreate,
    StellaEntityDetailed,
    StellaEntityUpdate,
    StellaEvent,
    StellaEventCreate,
    StellaEventDetailed,
    StellaModel,
    StellaModelCreate,
    StellaModelDetailed,
    StellaProject,
    StellaProjectCreate,
    StellaProjectDetailed,
    StellaWorkflow,
    StellaWorkflowCreate,
    StellaWorkflowDAG,
    StellaWorkflowDagCreate,
    StellaWorkflowDetailed,
)

WORKFLOW_MANAGEMENT_API = "/workflow-management/projects/"


class WorkflowManagerClient(StellanowBaseAPIClient):
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        organization_id: str,
        project_id: Optional[str] = None,
        client: Optional[httpx.Client] = None,
        totp_code: Optional[int] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        auto_authenticate: bool = True,
    ) -> None:
        super().__init__(
            base_url=base_url,
            username=username,
            password=password,
            organization_id=organization_id,
            client=client,
            totp_code=totp_code,
            access_token=access_token,
            refresh_token=refresh_token,
            auto_authenticate=auto_authenticate,
        )
        self.project_id = project_id or ""

    @property
    def base_path(self) -> str:
        return WORKFLOW_MANAGEMENT_API

    @property
    def _projects_url(self):
        return f"{self.base_url}{WORKFLOW_MANAGEMENT_API}"

    @property
    def _project_url(self):
        return self._build_url_project_required("")

    @property
    def _events_url(self):
        return self._build_url_project_required("/events")

    @property
    def _event_url(self):
        return self._build_url_project_required("/events/{eventId}")

    @property
    def _entities_url(self):
        return self._build_url_project_required("/entities")

    @property
    def _entity_url(self):
        return self._build_url_project_required("/entities/{entityId}")

    @property
    def _models_url(self):
        return self._build_url_project_required("/models")

    @property
    def _model_url(self):
        return self._build_url_project_required("/models/{modelId}")

    @property
    def _workflows_url(self):
        return self._build_url_project_required("/workflows")

    @property
    def _workflow_url(self):
        return self._build_url_project_required("/workflows/{workflowId}")

    @property
    def _workflow_dag_latest_url(self):
        return self._build_url_project_required("/workflows/{workflowId}/dag/latest")

    @property
    def _workflow_dag_version_url(self):
        return self._build_url_project_required("/workflows/{workflowId}/dag/versions/{versionId}")

    def create_project(self, project_data: Dict) -> StellaProjectDetailed:
        return self._create_or_update_resource(
            url=self._projects_url,
            data_model_class=StellaProjectCreate,
            return_class=StellaProjectDetailed,
            resource_data=project_data,
        )

    def create_model(self, model_data: Dict) -> StellaModelDetailed:
        return self._create_or_update_resource(
            url=self._models_url,
            data_model_class=StellaModelCreate,
            return_class=StellaModelDetailed,
            resource_data=model_data,
        )

    def create_event(self, event_data: Dict) -> StellaEventDetailed:
        return self._create_or_update_resource(
            url=self._events_url,
            data_model_class=StellaEventCreate,
            return_class=StellaEventDetailed,
            resource_data=event_data,
        )

    def create_entity(self, entity_data: Dict) -> StellaEntityDetailed:
        return self._create_or_update_resource(
            url=self._entities_url,
            data_model_class=StellaEntityCreate,
            return_class=StellaEntityDetailed,
            resource_data=entity_data,
        )

    def update_entity(self, entity_data: Dict, entity_id: str) -> StellaEntityDetailed:
        return self._create_or_update_resource(
            url=self._entity_url.format(entityId=entity_id),
            data_model_class=StellaEntityUpdate,
            return_class=StellaEntityDetailed,
            resource_data=entity_data,
            method=CreateOrUpdateTypes.PATCH,
        )

    def create_workflow(self, workflow_data: Dict) -> StellaWorkflowDetailed:
        return self._create_or_update_resource(
            url=self._workflows_url,
            data_model_class=StellaWorkflowCreate,
            return_class=StellaWorkflowDetailed,
            resource_data=workflow_data,
        )

    def create_workflow_dag(self, workflow_id: str, dag_data: Dict) -> StellaWorkflowDAG:
        return self._create_or_update_resource(
            url=f"{self._workflows_url}/{workflow_id}/dag",
            data_model_class=StellaWorkflowDagCreate,
            return_class=StellaWorkflowDAG,
            resource_data=dag_data,
        )

    def get_projects(
        self,
        page: int = 1,
        page_size: int = 20,
        include_archived: Optional[bool] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = "projects:created:asc",
    ) -> List[StellaProject]:
        filter_query = FilterIncludeArchived.INCLUDE_ARCHIVED.value if include_archived else None

        return self._get_list_resource(
            url=self._projects_url,
            result_class=StellaProject,
            page=page,
            page_size=page_size,
            filter=filter_query,
            search=search,
            sorting=sorting,
        )

    def get_project_details(self) -> StellaProjectDetailed:
        return self._get_resource(url=self._project_url, result_class=StellaProjectDetailed)

    def get_events(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: Optional[bool] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = "events:created:asc",
    ) -> List[StellaEvent]:
        filter_query = FilterIncludeInactive.INCLUDE_INACTIVE.value if include_inactive else None

        return self._get_list_resource(
            url=self._events_url,
            result_class=StellaEvent,
            page=page,
            page_size=page_size,
            filter=filter_query,
            search=search,
            sorting=sorting,
        )

    def get_event_details(self, event_id: str) -> StellaEventDetailed:
        return self._get_resource(url=self._event_url.format(eventId=event_id), result_class=StellaEventDetailed)

    def get_entities(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: Optional[bool] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = "entities:created:asc",
    ) -> List[StellaEntity]:
        filter_query = FilterIncludeInactive.INCLUDE_INACTIVE.value if include_inactive else None

        return self._get_list_resource(
            url=self._entities_url,
            result_class=StellaEntity,
            page=page,
            page_size=page_size,
            filter=filter_query,
            search=search,
            sorting=sorting,
        )

    def get_entity_details(self, entity_id: str) -> StellaEntityDetailed:
        return self._get_resource(url=self._entity_url.format(entityId=entity_id), result_class=StellaEntityDetailed)

    def get_models(
        self,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[StellaModel]:

        return self._get_list_resource(
            url=self._models_url,
            result_class=StellaModel,
            page=page,
            page_size=page_size,
            search=search,
            sorting=sorting,
        )

    def get_model_details(self, model_id: str) -> StellaModelDetailed:
        return self._get_resource(url=self._model_url.format(modelId=model_id), result_class=StellaModelDetailed)

    def get_workflows(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: Optional[bool] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = "workflows:created:asc",
    ) -> List[StellaWorkflow]:
        filter_query = FilterIncludeInactive.INCLUDE_INACTIVE.value if include_inactive else None

        return self._get_list_resource(
            url=self._workflows_url,
            result_class=StellaWorkflow,
            page=page,
            page_size=page_size,
            filter=filter_query,
            search=search,
            sorting=sorting,
        )

    def get_workflow_details(self, workflow_id: str) -> StellaWorkflowDetailed:
        return self._get_resource(
            url=self._workflow_url.format(workflowId=workflow_id),
            result_class=StellaWorkflowDetailed,
        )

    def get_latest_workflow_dag(self, workflow_id: str) -> StellaWorkflowDAG:
        details = self._get_resource(
            url=self._workflow_dag_latest_url.format(workflowId=workflow_id),
            result_class=StellaWorkflowDAG,
        )
        return details

    def get_workflow_dag_version(self, workflow_id: str, version_id: str) -> StellaWorkflowDAG:
        details = self._get_resource(
            url=self._workflow_dag_version_url.format(workflowId=workflow_id, versionId=version_id),
            result_class=StellaWorkflowDAG,
        )
        return details
