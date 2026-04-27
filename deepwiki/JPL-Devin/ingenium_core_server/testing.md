# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/controllers/Execution.js](api/controllers/Execution.js)

</details>



The Ingenium Core Server test suite is designed to ensure API reliability, execution engine stability, and performance under load. Testing is divided into three primary categories: automated Python-based CI tests, execution/stress examples, and JavaScript utility scripts for ad-hoc validation.

The test suite requires connectivity to several dependent services, including the Ingenium Archive and the Execution Server, as defined in the test configuration [README.md:33-34]().

### Testing Architecture

The following diagram illustrates the relationship between the test suites and the Core Server components:

**Test Suite to Code Mapping**
```mermaid
graph TD
    subgraph "Test Suites (Python/JS)"
        CI["Python CI (tests/test_ci_*.py)"]
        Stress["Stress Tests (tests/stress_tests/)"]
        JS["JS Utils (tests/js_examples/)"]
    end

    subgraph "Core Server (Node.js)"
        API["Controllers (api/controllers/)"]
        NF["node_funcs.js (Business Logic)"]
        SW["swagger.yaml (API Spec)"]
    end

    CI -->|HTTP Requests| API
    Stress -->|Bulk Execution| API
    JS -->|Ad-hoc API/S3 Calls| API
    API --> NF
    NF -->|Validates against| SW
```
Sources: [README.md:31-43](), [api/controllers/Execution.js:5-165]()

### Python CI Test Suite
The primary integration testing framework is built using Python's `unittest` and `xmlrunner`. These tests interact with the server via the `ingenium_client` to validate end-to-end workflows, including authentication, procedure creation, and execution management.

*   **Framework**: Utilizes `unittest` and `config.py` to manage service URLs like `CORE_SERVER_URL` and `ARCHIVE_ING_URL`.
*   **Coverage**: Includes dedicated files for health checks, logging, API keys, and comprehensive step-type validation (e.g., `test_ci_executions.py`, `test_ci_procedures.py`).
*   **Authentication**: Supports JWT-based authentication via `with_jwt.py` and `auth_example.py`.

For details, see [Python CI Test Suite](#5.1).

### Execution Examples and Stress Tests
Beyond standard CI, the repository contains scripts for complex execution scenarios and performance benchmarking.

*   **Execution Examples**: Located in `tests/execution_examples/`, these scripts demonstrate asynchronous execution, EIP procedure creation, and conductor role changes.
*   **Stress Testing**: Located in `tests/stress_tests/`, the `run_procedures.py` tool allows for load testing by simulating multiple concurrent procedure runs across various venues.

For details, see [Execution Examples and Stress Tests](#5.2).

### JavaScript Test Utilities
A collection of Node.js and browser-compatible scripts are maintained for testing specific integrations and utility functions.

*   **HTTP & Storage**: Examples using `axios` and `request` for API calls, and `s3_test.js` for verifying MinIO/S3 connectivity.
*   **Regex Validation**: Specialized tests in `tests/node/regex/` ensure that HTML content and image URLs are correctly transformed during procedure rendering or export.

For details, see [JavaScript Test Utilities](#5.3).

### Execution Flow in Tests
When a test triggers an execution, it follows the standard API lifecycle within the Core Server.

**Execution Lifecycle Mapping**
```mermaid
sequenceDiagram
    participant T as Test Script (Python/JS)
    participant C as Execution Controller
    participant S as Execution Service
    participant NF as node_funcs.js

    T->>C: POST /execution (create_execution)
    C->>S: create_execution(params)
    S->>NF: createExecution(data)
    NF-->>T: 201 Created (execution_id)
    
    T->>C: PUT /execution/{id}/run (run_execution)
    C->>S: run_execution(id)
    S->>NF: runStep(id)
    NF-->>T: 200 OK
```
Sources: [api/controllers/Execution.js:5-7](), [api/controllers/Execution.js:137-139](), [README.md:39-42]()

### Summary Table of Test Locations

| Category | Location | Purpose |
| :--- | :--- | :--- |
| **CI Integration** | `tests/test_ci_*.py` | Automated validation of all API endpoints and step types. |
| **Scenarios** | `tests/execution_examples/` | Demonstrations of specific execution workflows (Async, EIP). |
| **Load Testing** | `tests/stress_tests/` | High-concurrency execution and venue creation. |
| **Regex/Utilities** | `tests/node/` & `tests/js_examples/` | Ad-hoc testing for S3, regex, and JS HTTP clients. |

Sources: [README.md:31-43]()
