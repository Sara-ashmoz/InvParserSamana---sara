import unittest
from fastapi.testclient import TestClient
from app import app
from db import Base, engine, SessionLocal
from models import Invoice, Item

class TestInvoiceEndpoint(unittest.TestCase):

    def setUp(self):
        # recreate SQLAlchemy tables for a clean test DB
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        self.client = TestClient(app)

    def test_invoice_when_NOT_EXIST(self):
        response = self.client.get("/invoice/NOT_EXIST")

        self.assertEqual(response.status_code, 404)

        body = response.json()
        self.assertIn("error", body)
        self.assertEqual(body["error"], "Invoice not found")

    def test_get_invoice_success(self):
        # insert test invoice + item via SQLAlchemy session
        session = SessionLocal()
        try:
            inv = Invoice(
                InvoiceId="36259",
                VendorName="SuperStore",
                InvoiceDate="2012-03-06T00:00:00+00:00",
                BillingAddressRecipient="Aaron Bergman",
                ShippingAddress="98103, Seattle, Washington, United States",
                SubTotal=53.82,
                ShippingCost=4.29,
                InvoiceTotal=58.11
            )
            session.add(inv)
            session.flush()  # ensure InvoiceId exists

            it = Item(
                InvoiceId="36259",
                Description="Newell 330 Art, Office Supplies, OFF-AR-5309",
                Name="Newell 330 Art, Office Supplies, OFF-AR-5309",
                Quantity=3.0,
                UnitPrice=17.94,
                Amount=53.82
            )
            session.add(it)
            session.commit()
        finally:
            session.close()

        invoice_id = "36259"
        response = self.client.get(f"/invoice/{invoice_id}")

        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertIn("InvoiceId", body)
        self.assertEqual(body["InvoiceId"], invoice_id)

        self.assertIn("Items", body)
        self.assertIsInstance(body["Items"], list)

if __name__ == '__main__':
    unittest.main()

