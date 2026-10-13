from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_current_user
from app.schemas.execution import RunCodeRequest
from app.services.code_runner import CodeRunnerError, run_code

router = APIRouter()


@router.post("/run")
async def run(
    payload: RunCodeRequest,
    current_user: dict = Depends(get_current_user),
):
    del current_user
    try:
        output = await run_code(payload.language, payload.code)
        return {"status": "success", "data": {"output": output}}
    except CodeRunnerError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

