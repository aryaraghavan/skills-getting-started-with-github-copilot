# FastAPI Tests for Mergington High School Activities API

This directory contains comprehensive test suite for the FastAPI application that manages student activities at Mergington High School.

## Test Structure

### Test Files

- **`test_api.py`**: Core API endpoint tests
  - `TestActivitiesEndpoints`: Tests for activity listing and root redirect
  - `TestSignupEndpoint`: Tests for student signup functionality  
  - `TestUnregisterEndpoint`: Tests for student unregistration functionality
  - `TestActivityDataIntegrity`: Tests for data consistency across operations

- **`test_edge_cases.py`**: Edge cases and error handling tests
  - `TestEdgeCases`: URL encoding, special characters, email validation
  - `TestDataConsistency`: Data structure integrity tests
  - `TestHttpMethods`: HTTP method validation tests

- **`test_integration.py`**: Integration and workflow tests
  - `TestStaticFiles`: Static file serving tests
  - `TestApplicationIntegration`: End-to-end user journey tests
  - `TestErrorHandling`: Application error handling tests

### Configuration Files

- **`conftest.py`**: Pytest fixtures and configuration
- **`__init__.py`**: Python package initialization

## Test Coverage

The test suite achieves **100% code coverage** of the `src/app.py` module, testing:

- ✅ All API endpoints (`/`, `/activities`, `/activities/{name}/signup`, `/activities/{name}/unregister`)
- ✅ Static file serving
- ✅ Error handling and edge cases
- ✅ Data validation and integrity
- ✅ HTTP method restrictions
- ✅ URL encoding and special characters
- ✅ Complete user workflows

## Running Tests

### Using pytest directly:
```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestSignupEndpoint

# Run specific test method
pytest tests/test_api.py::TestSignupEndpoint::test_signup_success
```

### Using the test runner script:
```bash
# Run all tests
python run_tests.py

# Run with coverage
python run_tests.py --coverage

# Run with verbose output  
python run_tests.py --verbose

# Run specific file
python run_tests.py --file tests/test_api.py

# Run specific class
python run_tests.py --class TestSignupEndpoint
```

## Test Categories

### 🟢 Core Functionality Tests
- Activity listing and retrieval
- Student signup process
- Student unregistration process
- Data persistence and consistency

### 🟡 Edge Case Tests
- URL encoding with special characters
- Various email formats (including +, ., _)
- Case sensitivity in activity names
- Long input handling
- Unicode character support

### 🔴 Error Handling Tests
- Non-existent activities
- Duplicate signups
- Missing parameters
- Invalid HTTP methods
- Malformed requests

### 🔵 Integration Tests  
- Complete user workflows
- Static file serving
- Multi-user scenarios
- Cross-endpoint data consistency

## Fixtures

### `client`
Provides a FastAPI TestClient instance for making HTTP requests to the application.

### `reset_activities`
Resets the activities database to a known initial state before each test, ensuring test isolation.

### `sample_email` / `sample_activity`
Provide consistent test data for common test scenarios.

## Key Testing Patterns

### Data Isolation
Each test that modifies data uses the `reset_activities` fixture to ensure a clean state.

### Comprehensive Coverage
Tests cover both success and failure paths, including edge cases and error conditions.

### Real-world Scenarios
Integration tests simulate actual user workflows from page load to activity signup.

### HTTP Standards Compliance
Tests verify proper HTTP status codes, method restrictions, and header handling.

## Dependencies

The test suite requires:
- `pytest`: Test framework
- `httpx`: HTTP client for async testing
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting

Install with:
```bash
pip install -r requirements.txt
```

## Continuous Testing

The test suite is designed to support continuous integration and can be easily integrated into CI/CD pipelines.

Example GitHub Actions workflow:
```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=src --cov-report=xml
```