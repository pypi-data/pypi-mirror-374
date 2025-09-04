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

from typing import Optional

from keycloak import KeycloakError, KeycloakOpenID
from loguru import logger

from stellanow_api_internals.exceptions.api_exceptions import StellaNowKeycloakCommunicationException


class KeycloakAuth:
    def __init__(self, server_url: str, client_id: str, realm_name: str, verify: bool = True):
        self.keycloak_openid = KeycloakOpenID(
            server_url=server_url,
            client_id=client_id,
            realm_name=realm_name,
            verify=verify,
        )

    def get_token(self, username: str, password: str, totp_code: Optional[int] = None) -> dict:
        try:
            return self.keycloak_openid.token(username=username, password=password, totp=totp_code)
        except KeycloakError as exc:
            logger.error("Operation failed", exc)
            raise StellaNowKeycloakCommunicationException(details=exc)

    def refresh_token(self, refresh_token: str):
        try:
            return self.keycloak_openid.refresh_token(refresh_token)
        except KeycloakError as exc:
            logger.error("Operation failed", exc)
            raise StellaNowKeycloakCommunicationException(details=exc)
