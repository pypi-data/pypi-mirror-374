from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from iccore.data import Unit, UnitCreate, UnitPublic

from icflow.web.dependencies import get_session
from icflow.web.utils import db_create, db_select_all

router = APIRouter(prefix="/units", tags=["units"])


@router.post("/", response_model=UnitPublic)
def create(*, session: Session = Depends(get_session), item: UnitCreate):
    return db_create(item.to_model(), Unit, session)


@router.get("/", response_model=list[UnitPublic])
def list_items(session: Session = Depends(get_session)):
    return [UnitPublic.from_model(m) for m in db_select_all(Unit, session)]


@router.get("/{item_id}", response_model=UnitPublic)
def get(*, session: Session = Depends(get_session), item_id: int):
    item = session.get(Unit, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return UnitPublic.from_model(item)
