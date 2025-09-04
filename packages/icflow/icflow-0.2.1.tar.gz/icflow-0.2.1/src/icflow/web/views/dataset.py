from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from iccore.data import Dataset, DatasetCreate, DatasetPublic

from icflow.web.dependencies import get_session
from icflow.web.utils import db_create, db_select_all

router = APIRouter(prefix="/datasets", tags=["datasets"])


@router.post("/", response_model=DatasetPublic)
def create(*, session: Session = Depends(get_session), item: DatasetCreate):
    return db_create(item, Dataset, session)


@router.get("/", response_model=list[DatasetPublic])
def list_items(*, session: Session = Depends(get_session)):
    return db_select_all(Dataset, session)


@router.get("/{item_id}", response_model=DatasetPublic)
def get(*, session: Session = Depends(get_session), item_id: int):
    item = session.get(Dataset, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
