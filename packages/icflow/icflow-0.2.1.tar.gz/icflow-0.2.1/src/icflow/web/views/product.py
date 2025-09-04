from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from iccore.data import (
    Product,
    ProductCreate,
    ProductPublic,
    ProductPublicWithMeasurements,
)
from iccore.data import Measurement, MeasurementCreate, MeasurementPublic  # NOQA

from icflow.web.dependencies import get_session
from icflow.web.utils import db_create, db_select_all

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductPublic)
def create(*, session: Session = Depends(get_session), item: ProductCreate):
    return db_create(item, Product, session)


@router.get("/", response_model=list[ProductPublic])
def list_items(*, session: Session = Depends(get_session)):
    return db_select_all(Product, session)


@router.get("/{item_id}", response_model=ProductPublicWithMeasurements)
def get(*, session: Session = Depends(get_session), item_id: str):
    item = session.get(Product, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
