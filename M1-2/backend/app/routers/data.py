from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.dependencies import get_repository
from app.models.schedule import ScheduleCreate, ScheduleOut, ScheduleUpdate
from app.services.analysis_service import build_schedule_summary

router = APIRouter(prefix="/api/data", tags=["data"])


@router.post("", response_model=ScheduleOut, status_code=status.HTTP_201_CREATED)
def create_data(payload: ScheduleCreate, repo=Depends(get_repository)):
    return repo.create_schedule(payload.model_dump(mode="json"))


@router.get("", response_model=list[ScheduleOut])
def list_data(repo=Depends(get_repository)):
    return repo.list_schedules()


@router.get("/summary")
def get_summary(repo=Depends(get_repository)):
    return build_schedule_summary(repo.list_schedules())


@router.put("/{schedule_id}", response_model=ScheduleOut)
def update_data(schedule_id: str, payload: ScheduleUpdate, repo=Depends(get_repository)):
    current = repo.get_schedule(schedule_id)
    if current is None:
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")

    updates = payload.model_dump(mode="json", exclude_unset=True)
    candidate = {key: value for key, value in current.items() if key != "id"}
    candidate.update(updates)
    # 전체 모델로 재검증해 부분 수정 후 시간/value 불일치도 차단
    try:
        validated = ScheduleCreate(**candidate)
    except ValidationError as exc:
        errors = [{**error, "loc": ("body", *error["loc"])} for error in exc.errors()]
        raise RequestValidationError(errors) from exc
    updated = repo.update_schedule(schedule_id, validated.model_dump(mode="json"))
    return updated


@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_data(schedule_id: str, repo=Depends(get_repository)):
    if not repo.delete_schedule(schedule_id):
        raise HTTPException(status_code=404, detail="일정을 찾을 수 없습니다.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
