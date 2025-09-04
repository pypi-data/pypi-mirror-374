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

from pydantic import BaseModel

from stellanow_api_internals.core.helpers import StellaDateFormatter


class IterableMixin:
    def __iter__(self):
        return iter(self.root())


class StellaBaseName(BaseModel):
    name: str


class StellaBaseIdName(StellaBaseName):
    id: str


class StellaFormattedDateTime(BaseModel, StellaDateFormatter):
    createdAt: str
    updatedAt: str

    def __init__(self, **data):
        super().__init__(**data)
        self.createdAt = self.format_date(self.createdAt)
        self.updatedAt = self.format_date(self.updatedAt)

    def model_dump(self, **kwargs):  # noqa
        return super().model_dump(exclude_none=True)


class StellaExcludeNone(BaseModel):
    def model_dump(self, **kwargs):  # noqa
        return super().model_dump(exclude_none=True)
