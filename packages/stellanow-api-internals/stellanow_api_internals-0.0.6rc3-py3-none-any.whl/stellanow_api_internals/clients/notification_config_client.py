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
from stellanow_api_internals.core.enums import FilterIncludeInactive
from stellanow_api_internals.datatypes.notification_config import (
    StellaChannel,
    StellaChannelCreate,
    StellaChannelDetailed,
    StellaDestination,
    StellaDestinationCreate,
    StellaDestinationDetailed,
    StellaNotificationService,
    StellaNotificationServiceDetailed,
)

NOTIFICATION_CONFIG_API_BASE = "/notification-config/"
NOTIFICATION_CONFIG_API_PROJECT_CONTEXT = "/notification-config/projects/"


class NotificationConfigClient(StellanowBaseAPIClient):
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
        return NOTIFICATION_CONFIG_API_PROJECT_CONTEXT

    @property
    def _services_url(self):
        return f"{self.base_url}{NOTIFICATION_CONFIG_API_BASE}services"

    @property
    def _service_url(self):
        return f"{self.base_url}{NOTIFICATION_CONFIG_API_BASE}services/{{serviceId}}"

    @property
    def _channels_url(self):
        return self._build_url_project_required("/channels")

    @property
    def _channel_url(self):
        return self._build_url_project_required("/channels/{channelId}")

    @property
    def _destinations_url(self):
        return self._build_url_project_required("/channels/{channelId}/destinations")

    @property
    def _destination_url(self):
        return self._build_url_project_required("/channels/{channelId}/destinations/{destinationId}")

    def create_channel(self, channel_data: Dict) -> StellaChannelDetailed:
        return self._create_or_update_resource(
            url=self._channels_url,
            data_model_class=StellaChannelCreate,
            return_class=StellaChannelDetailed,
            resource_data=channel_data,
        )

    def create_destination(self, destination_data: Dict, channel_id: str) -> StellaDestination:
        return self._create_or_update_resource(
            url=self._destinations_url.format(channelId=channel_id),
            data_model_class=StellaDestinationCreate,
            return_class=StellaDestination,
            resource_data=destination_data,
        )

    def get_services(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: Optional[bool] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = "services:created:asc",
    ) -> List[StellaNotificationService]:
        filter_query = FilterIncludeInactive.INCLUDE_INACTIVE.value if include_inactive else None

        return self._get_list_resource(
            url=self._services_url,
            result_class=StellaNotificationService,
            page=page,
            page_size=page_size,
            filter=filter_query,
            search=search,
            sorting=sorting,
        )

    def get_service_details(self, service_id: str) -> StellaNotificationServiceDetailed:
        return self._get_resource(
            url=self._service_url.format(serviceId=service_id),
            result_class=StellaNotificationServiceDetailed,
        )

    def get_channels(
        self,
        page: int = 1,
        page_size: int = 20,
        include_inactive: Optional[bool] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = "channels:created:asc",
    ) -> List[StellaChannel]:
        filter_query = FilterIncludeInactive.INCLUDE_INACTIVE.value if include_inactive else None

        return self._get_list_resource(
            url=self._channels_url,
            result_class=StellaChannel,
            page=page,
            page_size=page_size,
            filter=filter_query,
            search=search,
            sorting=sorting,
        )

    def get_channel_details(self, channel_id: str) -> StellaChannelDetailed:
        return self._get_resource(
            url=self._channel_url.format(channelId=channel_id), result_class=StellaChannelDetailed
        )

    def get_destinations(
        self,
        channel_id: str,
        page: int = 1,
        page_size: int = 20,
        include_inactive: Optional[bool] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = "destinations:created:asc",
    ) -> List[StellaDestination]:
        filter_query = FilterIncludeInactive.INCLUDE_INACTIVE.value if include_inactive else None

        return self._get_list_resource(
            url=self._destinations_url.format(channelId=channel_id),
            result_class=StellaDestination,
            page=page,
            page_size=page_size,
            filter=filter_query,
            search=search,
            sorting=sorting,
        )

    def get_destination_details(self, channel_id: str, destination_id: str) -> StellaDestinationDetailed:
        return self._get_resource(
            url=self._destination_url.format(channelId=channel_id, destinationId=destination_id),
            result_class=StellaDestinationDetailed,
        )
