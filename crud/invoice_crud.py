from sqlalchemy.orm import Session
from models import Invoice


# CREATE
def create_invoice(db: Session, data: dict) -> Invoice:
    invoice = Invoice(**data)
    db.add(invoice)
    db.commit()
    db.refresh(invoice)
    return invoice


# READ
def get_invoice_by_id(db: Session, invoice_id: str):
    return db.query(Invoice).filter(Invoice.InvoiceId == invoice_id).first()


def get_all_invoices(db: Session):
    return db.query(Invoice).all()


def get_invoices_by_vendor(db: Session, vendor_name: str):
    return db.query(Invoice).filter(Invoice.VendorName == vendor_name).all()


# UPDATE
def update_invoice(db: Session, invoice_id: str, data: dict):
    invoice = get_invoice_by_id(db, invoice_id)
    if not invoice:
        return None

    for key, value in data.items():
        setattr(invoice, key, value)

    db.commit()
    db.refresh(invoice)
    return invoice


# DELETE
def delete_invoice(db: Session, invoice_id: str) -> bool:
    invoice = get_invoice_by_id(db, invoice_id)
    if not invoice:
        return False

    db.delete(invoice)
    db.commit()
    return True
