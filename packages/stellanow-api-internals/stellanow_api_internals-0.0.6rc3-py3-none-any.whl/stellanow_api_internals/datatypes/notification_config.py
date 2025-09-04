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

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, RootModel

from stellanow_api_internals.datatypes.core import StellaFormattedDateTime


class MessageTemplate(BaseModel):
    summary: str
    body: str


class StellaNotificationServiceShort(BaseModel):
    serviceId: str
    name: str
    serviceType: str

    model_config = ConfigDict(extra="ignore")


class StellaNotificationService(StellaFormattedDateTime):
    serviceId: str
    name: str
    description: Optional[str] = None
    isActive: bool
    serviceType: str
    url: Optional[str] = None
    auth: Optional[str] = None

    model_config = ConfigDict(extra="ignore")


class StellaNotificationServiceList(RootModel):
    root: List[StellaNotificationService]


class StellaNotificationServiceDetailed(StellaNotificationService):
    pass


class StellaNotificationServiceDetailedList(RootModel):
    root: List[StellaNotificationServiceDetailed]


class PlaceholderResponse(StellaFormattedDateTime):
    placeholderId: str
    name: str
    type: str


class PlaceholderResponseList(RootModel):
    root: List[PlaceholderResponse]


class PlaceholderCreate(BaseModel):
    name: str
    type: str


class PlaceholderCreateList(RootModel):
    root: List[PlaceholderCreate]


class StellaChannel(StellaFormattedDateTime):
    name: str
    description: Optional[str] = None
    isActive: bool
    realmId: str
    projectId: str
    channelId: str
    placeholders: Optional[PlaceholderResponseList] = None


class StellaChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None
    isActive: bool
    placeholders: Optional[PlaceholderCreateList]

    model_config = ConfigDict(extra="ignore")


class StellaDestinationChannel(StellaFormattedDateTime):
    name: str
    description: Optional[str] = None
    isActive: bool
    destinationId: str
    urlTemplate: Optional[str] = None
    requestType: Optional[str] = None


class StellaDestinationChannelList(RootModel):
    root: List[StellaDestinationChannel]


class StellaChannelDetailed(StellaChannel):
    destinationChannel: Optional[StellaDestinationChannelList] = None


class StellaChannelDetailedList(RootModel):
    root: List[StellaChannelDetailed]


class StellaDestination(StellaFormattedDateTime):
    name: str
    description: Optional[str] = None
    isActive: bool
    destinationId: str
    urlTemplate: Optional[str] = None
    requestType: Optional[str] = None
    messageTemplate: Optional[MessageTemplate] = None
    bodyTemplate: Optional[str] = None
    jiraProject: Optional[str] = None
    jiraIssueType: Optional[int] = None


class StellaDestinationList(RootModel):
    root: List[StellaDestination]


class StellaDestinationDetailed(StellaDestination):
    service: StellaNotificationServiceShort


class StellaDestinationDetailedList(RootModel):
    root: List[StellaDestinationDetailed]


class StellaDestinationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    isActive: bool
    urlTemplate: Optional[str] = None
    requestType: Optional[str] = None
    messageTemplate: Optional[MessageTemplate] = None
    bodyTemplate: Optional[str] = None
    jiraProject: Optional[str] = None
    jiraIssueType: Optional[int] = None
    serviceId: str

    model_config = ConfigDict(extra="ignore")
