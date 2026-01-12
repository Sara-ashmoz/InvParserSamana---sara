from sqlalchemy.orm import Session
from models import Item


# CREATE
def create_item(db: Session, data: dict) -> Item:
    item = Item(**data)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


# READ
def get_item_by_id(db: Session, item_id: int) -> Item | None:
    return db.query(Item).filter(Item.id == item_id).first()


def get_items_by_invoice_id(db: Session, invoice_id: str):
    return db.query(Item).filter(Item.InvoiceId == invoice_id).all()


# UPDATE
def update_item(db: Session, item_id: int, data: dict) -> Item | None:
    item = get_item_by_id(db, item_id)
    if not item:
        return None

    for key, value in data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


# DELETE
def delete_item(db: Session, item_id: int) -> bool:
    item = get_item_by_id(db, item_id)
    if not item:
        return False

    db.delete(item)
    db.commit()
    return True
