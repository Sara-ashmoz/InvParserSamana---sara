from fastapi import FastAPI, UploadFile, File
import oci
import base64
from db_util import init_db, save_inv_extraction, get_invoice_by_id, get_invoices_by_vendor
from fastapi.responses import JSONResponse
from fastapi import HTTPException


app = FastAPI()

# Load OCI config from ~/.oci/config
config = oci.config.from_file()

doc_client = oci.ai_document.AIServiceDocumentClient(config)

@app.post("/extract")
async def extract(file: UploadFile = File(...)):
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

    try:
        response = doc_client.analyze_document(request)
    except oci.exceptions.ServiceError:
        return JSONResponse(
            status_code=503,
            content={
                "error": "The service is currently unavailable. Please try again later."
                }
            )

    data = {}
    data_confidence = {}
    data_items = []

    for page in response.data.pages:
        if page.document_fields:
            for field in page.document_fields:
                field_name = field.field_label.name if field.field_label else None
                if field_name == 'Items':
                    dict = {}
                    for texts in field.field_value.items[0].field_value.items:
                        field_valuee = texts.field_label.name
                        field_text = texts.field_value.text
                        dict[field_valuee] = field_text
                        
                    data_items.append(dict) 
  
                else:
                    field_confidence = field.field_label.confidence if field.field_label else None
                    field_value = field.field_value.text
            
                data[field_name] = field_value
                data_confidence[field_name] = field_confidence
    data["Items"] = data_items


    result = {
        "confidence": 1.0,
        "data": data,
        "dataConfidence": data_confidence
    }

    save_inv_extraction(result)

    return result



@app.get("/invoice/{invoice_id}")
def invoice(invoice_id: str):
    invoice_data = get_invoice_by_id(invoice_id)

    if not invoice_data:
        return JSONResponse(
            status_code=404,
            content={"error": "Invoice not found"}
        )

    return invoice_data

@app.get("/invoices/vendor/{vendor_name}")
def get_invoices_by_vendor_endpoint(vendor_name: str):
    invoices = get_invoices_by_vendor(vendor_name)

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




if __name__ == "__main__":
    import uvicorn

    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8080)