from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.schemas.project import AddMemberRequest, CreateProjectRequest
from app.services.project_service import add_project_member, create_project, get_all_projects

router = APIRouter()


@router.post("/create")
async def create(payload: CreateProjectRequest, current_user: dict = Depends(get_current_user)):
    project = await create_project(payload.projectName, current_user["userId"])
    return {"status": "success", "data": project}


@router.get("/get-all")
async def get_all(current_user: dict = Depends(get_current_user)):
    projects = await get_all_projects(current_user["userId"])
    return {"status": "success", "data": projects}


@router.post("/{project_id}/members")
async def add_member(
    project_id: str,
    payload: AddMemberRequest,
    current_user: dict = Depends(get_current_user),
):
    try:
        member = await add_project_member(project_id, current_user["userId"], payload.email)
        return {"status": "success", "data": member}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
