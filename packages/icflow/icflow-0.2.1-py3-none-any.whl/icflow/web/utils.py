from sqlmodel import Session, select


def db_create(item, model_t, session: Session):
    db_item = model_t.model_validate(item)
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def db_select_all(model_t, session: Session):
    return session.exec(select(model_t)).all()
