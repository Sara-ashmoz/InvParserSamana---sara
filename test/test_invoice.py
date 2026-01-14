import unittest
from fastapi.testclient import TestClient
from app import app
from db_util import init_db, get_db
from db_util import save_inv_extraction


class TestInvoiceEndpoint(unittest.TestCase):

    def setUp(self):
        init_db()

        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM items")
            cur.execute("DELETE FROM confidences")
            cur.execute("DELETE FROM invoices")


        self.client = TestClient(app)


    
    def test_invoice_when_NOT_EXIST(self):
        response = self.client.get("/invoice/NOT_EXIST")

        self.assertEqual(response.status_code, 404)

        body = response.json()
        self.assertIn("error", body)
        self.assertEqual(body["error"], "Invoice not found")
    

    
    
    def test_get_invoice_success(self):
        save_inv_extraction({
        "data": {
            "InvoiceId": "36259",
            "VendorName": "SuperStore",
            "InvoiceDate": "2012-03-06T00:00:00+00:00",
            "BillingAddressRecipient": "Aaron Bergman",
            "ShippingAddress": "98103, Seattle, Washington, United States",
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
        },
        "dataConfidence": {}
    })
        
        invoice_id = "36259"

        response = self.client.get(f"/invoice/{invoice_id}")

        self.assertEqual(response.status_code, 200)

        body = response.json()
        print(body)

        self.assertIn("InvoiceId", body)
        self.assertEqual(body["InvoiceId"], invoice_id)

        expected_data = {
            "InvoiceId": "36259",
            "VendorName": "SuperStore",
            "InvoiceDate": "2012-03-06T00:00:00+00:00",
            "BillingAddressRecipient": "Aaron Bergman",
            "ShippingAddress": "98103, Seattle, Washington, United States",
            "SubTotal": 53.82,
            "ShippingCost": 4.29,
            "InvoiceTotal": 58.11,
            "Items": [
                {
                    "Description": "Newell 330 Art, Office Supplies, OFF-AR-5309",
                    "Name": "Newell 330 Art, Office Supplies, OFF-AR-5309",
                    "Quantity": 3.0,
                    "UnitPrice": 17.94,
                    "Amount": 53.82
                }
            ]
        }

        self.assertEqual(body, expected_data)

        self.assertIn("Items", body)
        self.assertIsInstance(body["Items"], list)

