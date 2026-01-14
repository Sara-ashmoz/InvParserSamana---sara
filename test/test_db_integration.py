import unittest

from db import Base, engine, SessionLocal
from crud import invoice_crud, item_crud, confidence_crud


class TestDBIntegration(unittest.TestCase):
    def setUp(self):
        # Fresh DB schema per test (simple & clear for course grading)
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    # -------- Invoice CRUD --------
    def test_invoice_create_and_read(self):
        payload = {
            "InvoiceId": "INT-100",
            "VendorName": "TestVendor",
            "InvoiceDate": "2026-01-01",
            "BillingAddressRecipient": "Alice",
            "ShippingAddress": "123 Lane",
            "SubTotal": 10.0,
            "ShippingCost": 1.0,
            "InvoiceTotal": 11.0,
        }

        invoice_crud.create_invoice(self.db, payload)

        got = invoice_crud.get_invoice_by_id(self.db, "INT-100")
        self.assertIsNotNone(got)
        self.assertEqual(got.InvoiceId, "INT-100")
        self.assertEqual(got.VendorName, "TestVendor")
        self.assertEqual(got.InvoiceTotal, 11.0)

    def test_invoice_update(self):
        invoice_crud.create_invoice(self.db, {"InvoiceId": "INT-101", "VendorName": "OldVendor"})

        updated = invoice_crud.update_invoice(self.db, "INT-101", {"VendorName": "NewVendor", "InvoiceTotal": 99.9})
        self.assertIsNotNone(updated)

        got = invoice_crud.get_invoice_by_id(self.db, "INT-101")
        self.assertEqual(got.VendorName, "NewVendor")
        self.assertEqual(got.InvoiceTotal, 99.9)

    def test_invoice_delete(self):
        invoice_crud.create_invoice(self.db, {"InvoiceId": "INT-102", "VendorName": "X"})
        ok = invoice_crud.delete_invoice(self.db, "INT-102")
        self.assertTrue(ok)

        got = invoice_crud.get_invoice_by_id(self.db, "INT-102")
        self.assertIsNone(got)

    # -------- Item CRUD + relationship via FK --------
    def test_item_create_and_read_by_invoice(self):
        # FK requires invoice exists
        invoice_crud.create_invoice(self.db, {"InvoiceId": "INT-200", "VendorName": "Vendor2"})

        item_crud.create_item(self.db, {
            "InvoiceId": "INT-200",
            "Description": "Item A",
            "Name": "Item A",
            "Quantity": 2.0,
            "UnitPrice": 5.5,
            "Amount": 11.0,
        })
        item_crud.create_item(self.db, {
            "InvoiceId": "INT-200",
            "Description": "Item B",
            "Name": "Item B",
            "Quantity": 1.0,
            "UnitPrice": 3.0,
            "Amount": 3.0,
        })

        items = item_crud.get_items_by_invoice_id(self.db, "INT-200")
        self.assertEqual(len(items), 2)
        self.assertTrue(any(i.Description == "Item A" for i in items))
        self.assertTrue(any(i.Description == "Item B" for i in items))

    # -------- Confidence CRUD + relationship via PK/FK --------
    def test_confidence_create_and_read(self):
        invoice_crud.create_invoice(self.db, {"InvoiceId": "INT-300", "VendorName": "Vendor3"})

        confidence_crud.create_confidence(self.db, {
            "InvoiceId": "INT-300",
            "VendorName": 0.98,
            "InvoiceDate": 0.95,
            "BillingAddressRecipient": 0.90,
            "ShippingAddress": 0.88,
            "SubTotal": 0.80,
            "ShippingCost": 0.70,
            "InvoiceTotal": 0.99,
        })

        conf = confidence_crud.get_confidence_by_invoice_id(self.db, "INT-300")
        self.assertIsNotNone(conf)
        self.assertEqual(conf.InvoiceId, "INT-300")
        self.assertAlmostEqual(conf.InvoiceTotal, 0.99, places=6)

    def test_confidence_update_and_delete(self):
        invoice_crud.create_invoice(self.db, {"InvoiceId": "INT-301", "VendorName": "VendorX"})
        confidence_crud.create_confidence(self.db, {"InvoiceId": "INT-301", "InvoiceTotal": 0.5})

        updated = confidence_crud.update_confidence(self.db, "INT-301", {"InvoiceTotal": 0.77})
        self.assertIsNotNone(updated)

        conf = confidence_crud.get_confidence_by_invoice_id(self.db, "INT-301")
        self.assertAlmostEqual(conf.InvoiceTotal, 0.77, places=6)

        ok = confidence_crud.delete_confidence(self.db, "INT-301")
        self.assertTrue(ok)

        conf2 = confidence_crud.get_confidence_by_invoice_id(self.db, "INT-301")
        self.assertIsNone(conf2)


if __name__ == "__main__":
    unittest.main()
