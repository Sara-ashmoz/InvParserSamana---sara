# API Traceability Matrix

This document maps each API endpoint to the integration tests that cover it.

## Endpoints Coverage

This table shows which integration tests cover each API endpoint.

| API Endpoint | HTTP Method | Tested? | Test File | Test Name |
|-------------|------------|---------|-----------|-----------|
| `/extract` | POST | Yes | test_extract.py | test_extract_endpoint |

| `/extract` | POST (invalid file) | Yes | test_extract.py | test_extract_invalid_file_type_returns_400 |

| `/extract` | POST (OCI failure)  | Yes | test_extract.py | test_extract_oci_failure_returns_503 |

| `/invoice/{invoice_id}` | GET (not found) | Yes | test_invoice.py | test_get_invoice_not_found_returns_404 |

| `/invoice/{invoice_id}` | GET (success) | Yes | test_invoice.py | test_get_invoice_success |

| `/invoices/vendor/{vendor_name}` | GET (no invoices) | Yes | test_invoices_by_vendor.py | test_get_invoices_by_vendor_not_found |

| `/invoices/vendor/{vendor_name}` | GET (success) | Yes | test_invoices_by_vendor.py | test_get_invoices_by_vendor_success |


## Notes
- All tests are integration tests using FastAPI `TestClient` with a real SQLite DB.
- External OCI calls are mocked in `/extract` tests to avoid dependency on external services.
