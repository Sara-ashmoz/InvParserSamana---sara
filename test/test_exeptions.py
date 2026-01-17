import unittest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient



class TestInvoiceExtraction(unittest.TestCase):

    def setUp(self):
        from db import Base, engine
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        from app import app
        from fastapi.testclient import TestClient
        self.client = TestClient(app)

    def build_mock_oci_response(self):
        return type('obj', (object,), {
            'data': type('obj', (object,), {
                'pages': [
                    type('obj', (object,), {
                        'document_fields': [
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'VendorName', 'confidence': 0.9})(),
                                'field_value': type('obj', (object,), {'value': 'SuperStore'})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'InvoiceId', 'confidence': 0.9})(),
                                'field_value': type('obj', (object,), {'value': '36259'})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'SubTotal', 'confidence': 0.9})(),
                                'field_value': type('obj', (object,), {'value': 53.82})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'ShippingCost', 'confidence': 0.9})(),
                                'field_value': type('obj', (object,), {'value': 4.29})()
                            })(),
                            type('obj', (object,), {
                                'field_type': 'KEY_VALUE',
                                'field_label': type('obj', (object,), {'name': 'InvoiceTotal', 'confidence': 0.9})(),
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
                                                        'field_value': type('obj', (object,), {'value': 'Item'})()
                                                    })(),
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'Name'})(),
                                                        'field_value': type('obj', (object,), {'value': 'Item'})()
                                                    })(),
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'Quantity'})(),
                                                        'field_value': type('obj', (object,), {'value': 1})()
                                                    })(),
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'UnitPrice'})(),
                                                        'field_value': type('obj', (object,), {'value': 1.0})()
                                                    })(),
                                                    type('obj', (object,), {
                                                        'field_label': type('obj', (object,), {'name': 'Amount'})(),
                                                        'field_value': type('obj', (object,), {'value': 1.0})()
                                                    })()
                                                ]
                                            })()
                                        })()
                                    ]
                                })()
                            })(),
                        ]
                    })()
                ]
            })()
        })()


    @patch("app.data_excute.save_invoice", side_effect=Exception("DB down"))
    @patch("app.get_doc_client")
    def test_extract_db_save_invoice_exception_is_swallowed(self, mock_get_doc_client, _mock_save_invoice):
        fake_client = MagicMock()
        mock_get_doc_client.return_value = fake_client
        fake_client.analyze_document.return_value = self.build_mock_oci_response()

        with open("invoices_sample/invoice_Aaron_Bergman_36259.pdf", "rb") as f:
            res = self.client.post("/extract", files={"file": ("invoice.pdf", f, "application/pdf")})

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["InvoiceId"], "36259")


    @patch("app.confidence_crud.create_confidence", side_effect=Exception("confidence fail"))
    @patch("app.get_doc_client")
    def test_extract_confidence_fails_still_returns_200(self, mock_get_doc_client, _mock_conf):
        fake_client = MagicMock()
        mock_get_doc_client.return_value = fake_client
        fake_client.analyze_document.return_value = self.build_mock_oci_response()

        with open("invoices_sample/invoice_Aaron_Bergman_36259.pdf", "rb") as f:
            res = self.client.post("/extract", files={"file": ("invoice.pdf", f, "application/pdf")})

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["InvoiceId"], "36259")


    @patch("app.item_crud.create_item", side_effect=Exception("item fail"))
    @patch("app.get_doc_client")
    def test_extract_item_create_fails_still_returns_200(self, mock_get_doc_client, _mock_item):
        fake_client = MagicMock()
        mock_get_doc_client.return_value = fake_client
        fake_client.analyze_document.return_value = self.build_mock_oci_response()

        with open("invoices_sample/invoice_Aaron_Bergman_36259.pdf", "rb") as f:
            res = self.client.post("/extract", files={"file": ("invoice.pdf", f, "application/pdf")})

        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["data"]["InvoiceId"], "36259")
