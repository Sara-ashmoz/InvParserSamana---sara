from fastapi import FastAPI, UploadFile, File, Depends
import oci
import base64
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import time
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Backend is running",
        "api_base_url": "http://localhost:8080"
    }

def get_doc_client():
    config = oci.config.from_file()
    return oci.ai_document.AIServiceDocumentClient(config)


# create tables on startup (safe single place)
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


def _safe_float(v):
    try:
        return float(v) if v is not None and v != "" else None
    except Exception:
        return None


@app.post("/extract")
async def extract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    pdf_bytes = await file.read()

    # Base64 encode PDF
    encoded_pdf = base64.b64encode(pdf_bytes).decode("utf-8")

    # 1. Validate PDF
    if file.content_type != "application/pdf":
        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid document. Please upload a valid PDF invoice with high confidence."
            }
        )

    document = oci.ai_document.models.InlineDocumentDetails(
        data=encoded_pdf
    )

    request = oci.ai_document.models.AnalyzeDocumentDetails(
        document=document,
        features=[
            oci.ai_document.models.DocumentFeature(
                feature_type="KEY_VALUE_EXTRACTION"
            ),
            oci.ai_document.models.DocumentClassificationFeature(
                max_results=5
            )
        ]
    )
    time_1 = time.time()

    try:
        doc_client = get_doc_client()
        response = doc_client.analyze_document(request)
    except oci.exceptions.ServiceError:
        return JSONResponse(
            status_code=503,
            content={
                "error": "The service is currently unavailable. Please try again later."
            }
        )
    time_2 = time.time()

    data = {}
    data_confidence = {}
    data_items = []

    for page in response.data.pages:
        if page.document_fields:
            for field in page.document_fields:
                field_name = field.field_label.name if field.field_label else None
                if field_name == 'Items':
                    # each item is a dict of item fields
                    for texts in field.field_value.items:
                        item_dict = {}
                        # texts likely contains a group of fields per item; iterate sub-items
                        for sub in texts.field_value.items:
                            key = sub.field_label.name if sub.field_label else None
                            val = sub.field_value.value
                            item_dict[key] = val
                        data_items.append(item_dict)
                else:
                    field_confidence = field.field_label.confidence if field.field_label else None
                    field_value = field.field_value.value if field.field_value else None

                    data[field_name] = field_value
                    data_confidence[field_name] = field_confidence

    data["Items"] = data_items

    prediction_time = time_2 - time_1

    result = {
        "confidence": 1.0,
        "data": data,
        "dataConfidence": data_confidence,
        "predictionTime": prediction_time
    }

    # Persist using CRUD layer (SQLAlchemy session via Depends(get_db))
    invoice_payload = {
        "InvoiceId": data.get("InvoiceId"),
        "VendorName": data.get("VendorName"),
        "InvoiceDate": data.get("InvoiceDate"),
        "BillingAddressRecipient": data.get("BillingAddressRecipient"),
        "ShippingAddress": data.get("ShippingAddress"),
        "SubTotal": _safe_float(data.get("SubTotal")),
        "ShippingCost": _safe_float(data.get("ShippingCost")),
        "InvoiceTotal": _safe_float(data.get("InvoiceTotal")),
    }

    # create invoice
    try:
        data_excute.save_invoice(db, invoice_payload)
    except Exception:
        pass

    # create confidences (if present)
    try:
        confidence_payload = {
            "InvoiceId": invoice_payload.get("InvoiceId"),
            "VendorName": _safe_float(data_confidence.get("VendorName")),
            "InvoiceDate": _safe_float(data_confidence.get("InvoiceDate")),
            "BillingAddressRecipient": _safe_float(data_confidence.get("BillingAddressRecipient")),
            "ShippingAddress": _safe_float(data_confidence.get("ShippingAddress")),
            "SubTotal": _safe_float(data_confidence.get("SubTotal")),
            "ShippingCost": _safe_float(data_confidence.get("ShippingCost")),
            "InvoiceTotal": _safe_float(data_confidence.get("InvoiceTotal")),
        }
        confidence_crud.create_confidence(db, confidence_payload)
    except Exception:
        pass

    # create items
    for it in data_items:
        try:
            item_payload = {
                "InvoiceId": invoice_payload.get("InvoiceId"),
                "Description": it.get("Description"),
                "Name": it.get("Name"),
                "Quantity": _safe_float(it.get("Quantity")),
                "UnitPrice": _safe_float(it.get("UnitPrice")),
                "Amount": _safe_float(it.get("Amount")),
            }
            item_crud.create_item(db, item_payload)
        except Exception:
            continue

    return result


@app.get("/invoice/{invoice_id}")
def invoice(invoice_id: str, db: Session = Depends(get_db)):
    invoice = invoice_crud.get_invoice_by_id(db, invoice_id)

    if not invoice:
        return JSONResponse(
            status_code=404,
            content={"error": "Invoice not found"}
        )

    return {
        "InvoiceId": invoice.InvoiceId,
        "VendorName": invoice.VendorName,
        "InvoiceDate": invoice.InvoiceDate,
        "BillingAddressRecipient": invoice.BillingAddressRecipient,
        "ShippingAddress": invoice.ShippingAddress,
        "SubTotal": invoice.SubTotal,
        "ShippingCost": invoice.ShippingCost,
        "InvoiceTotal": invoice.InvoiceTotal,
        "Items": [
            {
                "Description": it.Description,
                "Name": it.Name,
                "Quantity": it.Quantity,
                "UnitPrice": it.UnitPrice,
                "Amount": it.Amount,
            }
            for it in invoice.items
        ]
    }


@app.get("/invoices/vendor/{vendor_name}")
def get_invoices_by_vendor_endpoint(vendor_name: str, db: Session = Depends(get_db)):
    invoices = invoice_crud.get_invoices_by_vendor(db, vendor_name)

    if not invoices:
        return {
            "VendorName": "Unknown Vendor",
            "TotalInvoices": 0,
            "invoices": []
        }

    return {
        "VendorName": vendor_name,
        "TotalInvoices": len(invoices),
        "invoices": invoices
    }


@app.get("/")
def home():
    return {"msg": "Hello World"}



if __name__ == "__main__":
    import uvicorn

    # ensure tables when running directly
    Base.metadata.create_all(bind=engine)
    uvicorn.run(app, host="0.0.0.0", port=8080)