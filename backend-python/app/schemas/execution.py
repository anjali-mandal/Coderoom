from typing import Literal

from pydantic import BaseModel, Field


SupportedLanguage = Literal[
    "javascript",
    "typescript",
    "python",
    "java",
    "csharp",
    "css",
]


class RunCodeRequest(BaseModel):
    language: SupportedLanguage
    code: str = Field(max_length=50_000)

