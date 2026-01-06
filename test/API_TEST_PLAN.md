# API Test Plan – InvParser Application

## 1. What to Test

The purpose of this test plan is to validate the InvParser API endpoints.
The following aspects will be tested:

- All public API endpoints exposed by the FastAPI application.
- Successful request handling (HTTP 200 responses).
- Correct response structure and JSON format.
- Proper interaction between the API layer and the SQLite database.
- Correct handling of input files and request payloads.
- Error-free execution of business logic inside each endpoint.

Each API endpoint will have at least one corresponding integration test to ensure full API coverage.

---

## 2. Test Design Strategy

The chosen testing strategy is **Integration Testing**, as required by the project guidelines.

### Rationale:
- Integration tests validate the interaction between the API endpoints and the database layer.
- FastAPI’s `TestClient` is used to simulate HTTP requests without running a real server (Uvicorn).
- The SQLite database is real and initialized for each test.
- External services (OCI Document AI) are **mocked** using `unittest.mock` to avoid dependency on external systems.

This approach ensures the API logic is tested in a realistic but controlled environment.

---

## 3. Test Environment

The tests will be executed in the following environments:

- **Local development environment**
  - Python
  - pytest / unittest
  - FastAPI TestClient
- **CI environment (GitHub Actions)**
  - Automated execution on each pull request
  - Test results and coverage reported automatically

---

## 4. Success Criteria

The test execution will be considered successful when:

- All API endpoints are covered by integration tests (100% API endpoint coverage).
- All tests pass without errors.
- API responses return expected HTTP status codes.
- Response payloads match the expected structure.
- Code coverage for the API layer is as close as possible to 100%.
- Continuous Integration (CI) checks pass successfully.

---

## 5. Reporting

Test results and quality metrics will be reported using the following tools:

- **pytest** – for test execution and assertions.
- **pytest-cov** – for generating code coverage reports.
- **HTML coverage report** – generated locally for detailed inspection.
- **Codecov** – integrated with GitHub to display coverage metrics in pull requests.
- **GitHub Actions** – used to automatically run tests and enforce quality gates.

All reports will be accessible directly from the GitHub repository and CI pipeline.
