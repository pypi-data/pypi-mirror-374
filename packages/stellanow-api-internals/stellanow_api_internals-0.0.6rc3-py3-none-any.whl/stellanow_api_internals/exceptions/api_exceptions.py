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

from bs4 import BeautifulSoup
from click import ClickException
from keycloak import KeycloakError
from loguru import logger


class StellaNowException(ClickException):
    """Exception raised for errors in the Stella Now CLI."""

    def __init__(self, message, details):
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} {self.details}"


class StellaAPIError(StellaNowException):
    """Exception raised for errors in the Stella API."""

    def __init__(self, message, details=None):
        if details:
            logger.debug(f"Error: {details}")

        super().__init__(message, details)


class StellaAPIBadRequestError(StellaAPIError):
    """Exception raised for when a requested object does not exist in the Stella API."""

    def __init__(self, details):
        super().__init__("Bad Request", details)


class StellaAPIForbiddenError(StellaAPIError):
    """Exception raised for when trying to access the Stella API from blacklisted address."""

    def __init__(self, details):
        super().__init__("Forbidden", details)


class StellaAPINotFoundError(StellaAPIError):
    """Exception raised for when a requested object does not exist in the Stella API."""

    def __init__(self, details):
        super().__init__("Not Found", details)


class StellaAPIUnauthorisedError(StellaAPIError):
    """Exception raised for when request is not authorised to be performed by requesting entity in the Stella API."""

    def __init__(self, details):
        super().__init__("Unauthorised", details)


class StellaAPIWrongCredentialsError(StellaAPIError):
    """Exception raised for wrong credentials during auth in the Stella API."""

    def __init__(self):
        super().__init__("Unauthorized: Provided username or password is invalid.", {})


class StellaAPIConflictError(StellaAPIError):
    """Exception raised for when a requested object does exist in the Stella API."""

    def __init__(self, details):
        super().__init__("Conflict, object already exist.", details)


class StellaAPIInternalServerError(StellaAPIError):
    """Exception raised for when Internal Server Error."""

    def __init__(self, details):
        super().__init__("Internal Server Error.", details)


def parse_keycloak_error_response(error: KeycloakError):
    soup = BeautifulSoup(str(error), "html.parser")
    what_happened = soup.find_all("h2", text="What happened?")
    if what_happened:
        return what_happened[0].find_next("p").text
    h1_error = soup.find("h1")
    if h1_error:
        return h1_error.text
    return str(error)


class StellaNowApiKeycloakException(StellaAPIError):
    """Exception raised for Keycloak errors in the Stella Now API."""

    def __init__(self, message, details=None):
        if details:
            error_message = parse_keycloak_error_response(error=details)
            logger.debug(f"KeycloakError: {error_message}")

        super().__init__(message, details)


class StellaNowKeycloakCommunicationException(StellaNowApiKeycloakException):
    def __init__(self, details):
        super().__init__(f"An error occurred while trying to communicate with the authentication server", details)
