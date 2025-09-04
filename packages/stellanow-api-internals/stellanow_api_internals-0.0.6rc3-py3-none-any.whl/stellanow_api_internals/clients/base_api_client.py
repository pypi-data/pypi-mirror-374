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

import json
from http import HTTPStatus
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

import httpx
from loguru import logger

from stellanow_api_internals.auth.keycloak_auth import KeycloakAuth
from stellanow_api_internals.core.enums import CreateOrUpdateTypes
from stellanow_api_internals.exceptions.api_exceptions import (
    StellaAPIBadRequestError,
    StellaAPIConflictError,
    StellaAPIForbiddenError,
    StellaAPINotFoundError,
    StellaAPIUnauthorisedError,
    StellaAPIWrongCredentialsError,
)

T = TypeVar("T")


class StellanowBaseAPIClient(Generic[T]):
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        organization_id: str,
        client: Optional[httpx.Client] = None,
        totp_code: Optional[str] = None,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        auto_authenticate: bool = True,
    ) -> None:
        self.base_url = base_url
        self.username = username
        self.password = password
        self.organization_id = organization_id
        self.auth_token = access_token
        self.refresh_token = refresh_token
        self.client = client or httpx.Client()
        self.totp_code = totp_code

        self.keycloak = KeycloakAuth(
            server_url=self._auth_url, client_id="tools-cli", realm_name=self.organization_id, verify=True
        )

        if auto_authenticate and not (self.auth_token and self.refresh_token):
            self.authenticate()

    def set_tokens(self, access_token: str, refresh_token: str) -> None:  # <<< NEW
        self.auth_token = access_token
        self.refresh_token = refresh_token

    @property
    def _auth_url(self):
        return f"{self.base_url}/auth/"

    def _handle_response(self, response, url, method=None) -> None:
        """
        Handle the API response and raise appropriate exceptions for error status codes.

        :param response: The HTTP response object.
        :param url: The URL that was called.
        :param method: The HTTP method used (optional, for logging purposes).
        """
        try:
            details = response.json().get("details", {})
            if not isinstance(details, dict):
                details = {}
        except json.JSONDecodeError:
            details = {}

        status_code = response.status_code
        error_message = details.get("errorMessage", "No error details provided")
        request_info = f"{method or 'REQUEST'} to {url}"

        if status_code >= HTTPStatus.BAD_REQUEST:
            logger.error(f"API request failed with status {status_code} for {request_info}: {error_message}")

        match status_code:
            case HTTPStatus.BAD_REQUEST:
                raise StellaAPIBadRequestError(f"Bad Request: {error_message}")
            case HTTPStatus.UNAUTHORIZED:
                errors = details.get("errors", [])
                if not isinstance(errors, list):
                    errors = []

                for error in errors:
                    match error.get("errorCode"):
                        case "inactiveAuthToken":
                            self.auth_refresh()
                            return
                        case "wrongUsernameOrPassword":
                            raise StellaAPIWrongCredentialsError()
                        case _:
                            raise StellaAPIUnauthorisedError(f"Unauthorized: {error_message}")
                else:
                    response.raise_for_status()
            case HTTPStatus.FORBIDDEN:
                raise StellaAPIForbiddenError(f"Forbidden: {error_message}")
            case HTTPStatus.NOT_FOUND:
                raise StellaAPINotFoundError(f"Not Found: {error_message}")
            case HTTPStatus.CONFLICT:
                raise StellaAPIConflictError(f"Conflict: {error_message}")
            case _:
                response.raise_for_status()

    def authenticate(self):
        logger.info(f"Authenticating to the {self.__class__.__name__} API ... ")

        if self.refresh_token is not None:
            self.auth_refresh()
        else:
            self.auth_token = None
            self.refresh_token = None

            response = self.keycloak.get_token(username=self.username, password=self.password, totp_code=self.totp_code)

            self.auth_token = response.get("access_token")
            self.refresh_token = response.get("refresh_token")

        logger.info("Authentication Successful")

    def auth_refresh(self):
        if self.refresh_token is None:
            self.authenticate()
        else:
            logger.info("API Token Refreshing ...")

            refresh_token = self.refresh_token

            self.auth_token = None
            self.refresh_token = None

            response = self.keycloak.refresh_token(refresh_token)

            self.auth_token = response.get("access_token")
            self.refresh_token = response.get("refresh_token")

            logger.info("API Token Refresh Successful")

    def _make_request(
        self,
        url: str,
        method: Optional[str] = "GET",
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        method = method or "GET"
        response = self.client.request(method=method, url=url, headers=headers, json=data, params=params)
        self._handle_response(response=response, url=url, method=method)
        return response.json().get("details", {})

    def _create_or_update_resource(
        self,
        url: str,
        data_model_class: Type[Any],
        return_class: Type[Any],
        resource_data: Dict,
        method: Optional[CreateOrUpdateTypes] = CreateOrUpdateTypes.POST,
    ) -> Any:
        """
        Helper method to make requests (POST/PATCH) and validate that the response is a dict.

        :param url: The API endpoint URL.
        :param data_model_class: The Pydantic model class for the request data.
        :param return_class: The Pydantic model class for the response data.
        :param resource_data: The data to be sent in the request.
        :param method: The HTTP method ('POST' or 'PATCH').
        :return: An instance of the return_class containing the parsed response.
        """
        data_model_instance = data_model_class(**resource_data)
        details = self._make_request(url=url, method=method.value, data=data_model_instance.model_dump())

        if isinstance(details, List):
            raise TypeError(f"Expected a dict but got a list for {return_class.__name__} details.")

        return return_class(**details)

    def _get_resource(
        self,
        url: str,
        result_class: Type[T],
    ) -> T:
        """
        Fetch a single resource from the API.

        :param url: The API endpoint URL.
        :param result_class: The Pydantic model class for the expected result.
        :return: An instance of result_class.
        """
        details = self._make_request(url=url)

        if not isinstance(details, Dict):
            raise TypeError(f"Expected a dict but got {type(details)}")

        return result_class(**details)

    def _get_list_resource(
        self,
        url: str,
        result_class: Type[T],
        page: int = 1,
        page_size: int = 20,
        filter: Optional[str] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[T]:
        """
        Fetch a list of resources (paginated) from the API.
        This method handles pagination and returns a list of resources.
        """
        params = self._build_query_params(page=page, page_size=page_size, filter=filter, search=search, sorting=sorting)
        details = self._make_request(url=url, params=params)

        return self._handle_paginated_results(
            initial_details=details,
            result_class=result_class,
            url=url,
            filter=filter,
            search=search,
            sorting=sorting,
        )

    def _handle_paginated_results(
        self,
        initial_details: Dict[str, Any],
        result_class: Type[T],
        url: str,
        filter: Optional[str] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> List[T]:
        """
        Helper method to handle paginated results based on the initial response.

        :param initial_details: The initial details from the first paginated response.
        :param result_class: The Pydantic model class for the response data.
        :param url: The API endpoint URL.
        :param filter: An optional filter string.
        :param search: An optional search string.
        :param sorting: An optional sorting string.
        :return: A list of result_class instances.
        """
        results: List[T] = []

        page_results = initial_details.get("results", [])
        results.extend(result_class(**item) for item in page_results)

        page_number = initial_details.get("pageNumber", 1)
        number_of_pages = initial_details.get("numberOfPages", 1)
        page_size = initial_details.get("pageSize", 20)

        while page_number < number_of_pages:
            page_number += 1
            params = self._build_query_params(
                page=page_number, page_size=page_size, filter=filter, search=search, sorting=sorting
            )
            details = self._make_request(url, params=params)

            page_results = details.get("results", [])
            results.extend(result_class(**item) for item in page_results)

        return results

    @staticmethod
    def _build_query_params(
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        filter: Optional[str] = None,
        search: Optional[str] = None,
        sorting: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Helper method to build query parameters for GET requests.

        :param page: The page number (optional).
        :param page_size: The number of items per page (optional).
        :param filter: An optional filter string.
        :param search: An optional search string.
        :param sorting: An optional sorting string.
        :return: A dictionary of query parameters.
        """
        params = {
            "filter": filter,
            "search": search,
            "sorting": sorting,
            "page": page,
            "pageSize": page_size,
        }
        return {k: v for k, v in params.items() if v is not None}

    def set_project_id(self, project_id: str) -> None:
        self.project_id = project_id

    def _validate_project_id(self) -> None:
        if not self.project_id:
            raise ValueError("Project ID is not set. Please set the project_id before making this request.")

    def _build_url_project_required(self, path: str) -> str:
        """Builds the URL that requires a project ID, using the client-specific base path."""
        self._validate_project_id()
        return f"{self.base_url}{self.base_path}{self.project_id}{path}"

    @property
    def base_path(self) -> str:
        """To be overridden by subclasses to provide the base path for each client."""
        raise NotImplementedError("Subclasses must define 'base_path'.")

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = httpx.get(url, headers=headers, params=params)
        self._handle_response(response=response, url=url, method="GET")
        return response.json()

    def post(self, endpoint: str, data: Dict) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = httpx.post(url, headers=headers, json=data)
        self._handle_response(response=response, url=url, method="POST")
        return response.json()

    def put(self, endpoint: str, data: Dict) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = httpx.put(url, headers=headers, json=data)
        self._handle_response(response=response, url=url, method="PUT")
        return response.json()

    def delete(self, endpoint: str) -> Dict:
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        response = httpx.delete(url, headers=headers)
        self._handle_response(response=response, url=url, method="DELETE")
        return response.json()
