import unittest
from fastapi.testclient import TestClient
from app import app
from db_util import init_db

class TestInvoicesByVendorEndpoint(unittest.TestCase):

    def setUp(self):
        init_db()
        self.client = TestClient(app)
        

    def test_get_invoices_by_vendor_not_found(self):
        response = self.client.get("/invoices/vendor/NO_VENDOR")

        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(body["VendorName"], "Unknown Vendor")
        self.assertEqual(body["TotalInvoices"], 0)
        self.assertEqual(body["invoices"], [])




    def test_get_invoices_by_vendor_success(self):
        vendor_name = "SuperStore"

        response = self.client.get(f"/invoices/vendor/{vendor_name}")

        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(body["VendorName"], vendor_name)
        self.assertGreater(body["TotalInvoices"], 0)
        self.assertEqual(body["TotalInvoices"], 5)
        self.assertIsInstance(body["invoices"], list)
