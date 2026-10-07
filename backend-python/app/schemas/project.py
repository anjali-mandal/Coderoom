from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    projectName: str


class AddMemberRequest(BaseModel):
    email: str
