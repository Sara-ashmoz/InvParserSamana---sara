from sqlalchemy.orm import Session
from models import Confidence


# CREATE
def create_confidence(db: Session, data: dict) -> Confidence:
    confidence = Confidence(**data)
    db.add(confidence)
    db.commit()
    db.refresh(confidence)
    return confidence


# READ
def get_confidence_by_invoice_id(db: Session, invoice_id: str):
    return db.query(Confidence).filter(
        Confidence.InvoiceId == invoice_id
    ).first()


# UPDATE
def update_confidence(db: Session, invoice_id: str, data: dict):
    confidence = get_confidence_by_invoice_id(db, invoice_id)
    if not confidence:
        return None

    for key, value in data.items():
        setattr(confidence, key, value)

    db.commit()
    db.refresh(confidence)
    return confidence


# DELETE
def delete_confidence(db: Session, invoice_id: str) -> bool:
    confidence = get_confidence_by_invoice_id(db, invoice_id)
    if not confidence:
        return False

    db.delete(confidence)
    db.commit()
    return True
