import unittest
from fastapi.testclient import TestClient
from app import app
from db import Base, engine, SessionLocal
from models import Invoice, Item

class TestInvoicesByVendorEndpoint(unittest.TestCase):

    def setUp(self):
        # recreate SQLAlchemy tables for a clean test DB
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        self.client = TestClient(app)

    def test_get_invoices_by_vendor_not_found(self):
        response = self.client.get("/invoices/vendor/NO_VENDOR")

        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(body["VendorName"], "Unknown Vendor")
        self.assertEqual(body["TotalInvoices"], 0)
        self.assertEqual(body["invoices"], [])

    def test_get_invoices_by_vendor_success(self):
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
            session.flush()

            it = Item(
                InvoiceId="36259",
                Description="Newell 330 Art, Office Supplies, OFF-AR-5309",
                Name="Newell 330 Art, Office Supplies, OFF-AR-5309",
                Quantity=3,
                UnitPrice=17.94,
                Amount=53.82
            )
            session.add(it)
            session.commit()
        finally:
            session.close()

        vendor_name = "SuperStore"

        response = self.client.get(f"/invoices/vendor/{vendor_name}")

        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(body["VendorName"], vendor_name)
        self.assertGreater(body["TotalInvoices"], 0)
        self.assertIsInstance(body["invoices"], list)
