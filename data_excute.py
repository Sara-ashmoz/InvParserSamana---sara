#data excute.py

from sqlalchemy.orm import Session
from models import Invoice

def save_invoice(db: Session, data: dict):
    """
    Persist an Invoice using an existing SQLAlchemy Session.
    Call from endpoints as: save_invoice(db, invoice_payload)
    """
    invoice = Invoice(
        InvoiceId=data.get("InvoiceId"),
        VendorName=data.get("VendorName"),
        InvoiceDate=data.get("InvoiceDate"),
        BillingAddressRecipient=data.get("BillingAddressRecipient"),
        ShippingAddress=data.get("ShippingAddress"),
        SubTotal=data.get("SubTotal"),
        ShippingCost=data.get("ShippingCost"),
        InvoiceTotal=data.get("InvoiceTotal")
    )

    db.add(invoice)
    try:
        db.commit()
        db.refresh(invoice)
    except Exception:
        db.rollback()
        raise

    return invoice