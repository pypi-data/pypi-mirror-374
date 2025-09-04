from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from iccore.auth import User, UserCreate, UserPublic

from icflow.web.dependencies import get_session
from icflow.web.utils import db_create, db_select_all

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserPublic)
def create(*, session: Session = Depends(get_session), user: UserCreate):
    return db_create(user, User, session)


@router.get("/", response_model=list[UserPublic])
def list_items(session: Session = Depends(get_session)):
    return db_select_all(User, session)


@router.get("/{item_id}", response_model=UserPublic)
def get(*, session: Session = Depends(get_session), item_id: int):
    user = session.get(User, item_id)
    if not user:
        raise HTTPException(status_code=404, detail="Item not found")
    return user
