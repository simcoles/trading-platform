from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.db import get_session

router = APIRouter(prefix="/health")


@router.get("/db")
def check_database(session: Annotated[Session, Depends(get_session)]) -> dict[str, str]:
    session.execute(text("SELECT 1"))
    return {"database": "ok"}
