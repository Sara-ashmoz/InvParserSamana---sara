import unittest
from unittest.mock import patch, MagicMock
from db_util import init_db
from fastapi.testclient import TestClient
import oci 


class TestInvoiceExtraction(unittest.TestCase):

    def setUp(self):
        init_db()
        from app import app
        self.client = TestClient(app)
    
    @patch("app.get_doc_client")
    def test_extract_endpoint(self, mock_get_doc_client):
        """Test the /extract endpoint with invoice_Aaron_Bergman_36259.pdf"""
       
        # Setup mock client instance
        mock_client_instance = MagicMock()
        mock_get_doc_client.return_value = mock_client_instance
        mock_analyze = mock_client_instance.analyze_document
        
        # Mock OCI response - return the exact expected result structure
        mock_analyze.return_value = type('obj', (object,), {
            'data': type('obj', (object,), {
                'detected_document_types': [
                    type('obj', (object,), {
                        'document_type': 'INVOICE',
                        'confidence': 1
                    })()
                ],
                'pages': [
                    type('obj', (object,), {
                        'document_fields': [
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'VendorName', 'confidence': 0.9491271})(),
                                'field_value': type('obj', (object,), {'value': 'SuperStore'})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'VendorNameLogo', 'confidence': 0.9491271})(),
                                'field_value': type('obj', (object,), {'value': 'SuperStore'})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'InvoiceId', 'confidence': 0.9995704})(),
                                'field_value': type('obj', (object,), {'value': '36259'})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'InvoiceDate', 'confidence': 0.9999474})(),
                                'field_value': type('obj', (object,), {'value': '2012-03-06T00:00:00+00:00'})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'ShippingAddress', 'confidence': 0.9818857})(),
                                'field_value': type('obj', (object,), {'value': '98103, Seattle, Washington, United States'})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'BillingAddressRecipient', 'confidence': 0.9970944})(),
                                'field_value': type('obj', (object,), {'value': 'Aaron Bergman'})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'AmountDue', 'confidence': 0.9994609})(),
                                'field_value': type('obj', (object,), {'value': 58.11})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'SubTotal', 'confidence': 0.90709054})(),
                                'field_value': type('obj', (object,), {'value': 53.82})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'ShippingCost', 'confidence': 0.98618066})(),
                                'field_value': type('obj', (object,), {'value': 4.29})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'InvoiceTotal', 'confidence': 0.9974165})(),
                                'field_value': type('obj', (object,), {'value': 58.11})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'LINE_ITEM_GROUP',
                                'field_label': type('obj', (object,), {'name': 'Items', 'confidence': None})(),
                                'field_value': type('obj', (object,), {
                                    'items': [
                                        type('obj', (object,), {
                                            'field_value': type('obj', (object,), {
                                                'items': [
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'Description'})(),
                                                        'field_value': type('obj', (object,), {'value': 'Newell 330 Art, Office Supplies, OFF-AR-5309'})()
                                                    })(),
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'Name'})(),
                                                        'field_value': type('obj', (object,), {'value': 'Newell 330 Art, Office Supplies, OFF-AR-5309'})()
                                                    })(),
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'Quantity'})(),
                                                        'field_value': type('obj', (object,), {'value': 3})()
                                                    })(),
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'UnitPrice'})(),
                                                        'field_value': type('obj', (object,), {'value': 17.94})()
                                                    })(),
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'Amount'})(),
                                                        'field_value': type('obj', (object,), {'value': 53.82})()
                                                    })()
                                                ]
                                            })()
                                        })()
                                    ]
                                })()
                            })()
                        ]
                    })()
                ]
            })()
        })()
        
        # Import app and dependencies after patching
        from app import app
        from fastapi.testclient import TestClient
        import json
        
        
        # Load the test invoice file
        with open("invoices_sample/invoice_Aaron_Bergman_36259.pdf", "rb") as f:
            response = self.client.post(
                "/extract",
                files={"file": ("invoice_Aaron_Bergman_36259.pdf", f, "application/pdf")}
            )
        
        # Check response status
        self.assertEqual(response.status_code, 200)
        
        # Parse response
        result = response.json()
        
        # Expected data structure
        expected_data = {
            "VendorName": "SuperStore",
            "VendorNameLogo": "SuperStore",
            "InvoiceId": "36259",
            "InvoiceDate": "2012-03-06T00:00:00+00:00",
            "ShippingAddress": "98103, Seattle, Washington, United States",
            "BillingAddressRecipient": "Aaron Bergman",
            "AmountDue": 58.11,
            "SubTotal": 53.82,
            "ShippingCost": 4.29,
            "InvoiceTotal": 58.11,
            "Items": [
                {
                    "Description": "Newell 330 Art, Office Supplies, OFF-AR-5309",
                    "Name": "Newell 330 Art, Office Supplies, OFF-AR-5309",
                    "Quantity": 3,
                    "UnitPrice": 17.94,
                    "Amount": 53.82
                }
            ]
        }
        
        # Validate response structure and values
        self.assertEqual(result["data"], expected_data)
        
        print("✓ All assertions passed!")
        print(f"Response: {json.dumps(result, indent=2)}")


    def test_upload_not_a_pdf(self):
        """
        Error case: upload not a PDF -> should return 400
        """
        fake_bytes = b"hello this is not a pdf"

        response = self.client.post(
            "/extract",
            files={"file": ("not_pdf.txt", fake_bytes, "text/plain")}
        )

        self.assertEqual(response.status_code, 400)

        body = response.json()
        self.assertIn("error", body)
        self.assertEqual(
            body["error"],
            "Invalid document. Please upload a valid PDF invoice with high confidence."
        )

    @patch("app.get_doc_client")
    def test_of_unavailable_service(self, mock_get_doc_client):
        # יוצרים client מזויף שהמתודה analyze_document שלו זורקת ServiceError
        fake_client = MagicMock()
        fake_client.analyze_document.side_effect = oci.exceptions.ServiceError(
            status=503,
            code="ServiceError",
            headers={},
            message="OCI down"
        )
        mock_get_doc_client.return_value = fake_client

        with open("invoices_sample/invoice_Aaron_Bergman_36259.pdf", "rb") as f:
            response = self.client.post(
                "/extract",
                files={"file": ("invoice.pdf", f, "application/pdf")}
            )

        self.assertEqual(response.status_code, 503)
        body = response.json()
        self.assertIn("error", body)
        self.assertEqual(
            body["error"],
            "The service is currently unavailable. Please try again later."
        )


if __name__ == '__main__':
    unittest.main()
