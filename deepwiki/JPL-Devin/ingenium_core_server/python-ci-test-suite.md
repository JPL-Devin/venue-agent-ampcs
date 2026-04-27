# Page: Python CI Test Suite

# Python CI Test Suite

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [api/controllers/Execution.js](api/controllers/Execution.js)
- [api/controllers/ExecutionService.js](api/controllers/ExecutionService.js)

</details>



The Python CI Test Suite provides comprehensive integration testing for the Ingenium Core Server. It utilizes the `unittest` framework to validate the entire lifecycle of procedures and executions, ensuring that the middleware, business logic in `node_funcs.js`, and downstream service integrations (Archive, Execution Server) function correctly.

## Test Framework Architecture

The suite is built on a layered architecture that abstracts API communication and authentication, allowing test cases to focus on functional validation.

### Core Components
*   **`unittest` + `xmlrunner`**: The standard Python testing framework, extended with `xmlrunner` to produce machine-readable reports for Jenkins CI pipelines.
*   **`ingenium_client`**: A custom Python client library used to interact with the Core Server's REST API endpoints defined in `swagger.yaml`.
*   **`config.py`**: Centralized configuration for service URLs and environment settings.
*   **`utils.py`**: Shared helper functions for common tasks like creating test procedures, generating unique identifiers, and polling for execution status.

### Data Flow Diagram: CI Test Execution
This diagram illustrates how a test case interacts with the Core Server and its dependencies.

Title: CI Test Execution Flow
```mermaid
graph TD
    subgraph "Test Environment"
        [test_ci_*.py] -- "uses" --> [utils.py]
        [test_ci_*.py] -- "calls" --> [ingenium_client]
        [ingenium_client] -- "reads" --> [config.py]
    end

    subgraph "Ingenium Core Server"
        [ingenium_client] -- "HTTP Request (JWT)" --> [index.js]
        [index.js] -- "Route" --> [Execution.js]
        [Execution.js] -- "Logic" --> [node_funcs.js]
    end

    subgraph "Downstream Services"
        [node_funcs.js] -- "REST" --> [Archive_Service]
        [node_funcs.js] -- "REST" --> [Execution_Server]
        [node_funcs.js] -- "Redis" --> [Redis_Store]
    end
```
**Sources:** [README.md:31-43](), [api/node_funcs.js:1-10](), [api/controllers/Execution.js:1-10]()

---

## Configuration and Utilities

### Service Configuration (`config.py`)
The suite relies on several environment-specific URLs to target the correct deployment of the Ingenium stack.
*   `CORE_SERVER_URL`: The entry point for the Core Server (defaulting to `http://localhost:8080/api/v5`).
*   `ARCHIVE_ING_URL`: The URL for the Archive service.
*   `VENUE_CONFIG_URL`: The URL for venue management.

**Sources:** [README.md:21-29](), [README.md:33-34]()

### Authentication Handling
Tests handle authentication through two primary mechanisms:
1.  **`with_jwt.py`**: A decorator or utility used to inject JWT tokens into request headers.
2.  **`auth_example.py`**: Demonstrates the pattern for obtaining a token from the Ingenium Auth Server and passing it to `node_funcs.get_auth_key` [api/controllers/ExecutionService.js:15-15]().

### Common Utilities (`utils.py`)
`utils.py` provides high-level abstractions to reduce boilerplate in `test_ci_*.py` files:
*   **`create_test_procedure()`**: Wraps calls to `node_funcs.createArchiveElement` [api/controllers/ExecutionService.js:45-45]() to set up a procedure structure (Sections -> Steps).
*   **`wait_for_execution_status()`**: Polls the `get_execution_status` endpoint [api/controllers/Execution.js:45-47]() until a desired state (e.g., `COMPLETED`, `HALTED`) is reached.

---

## Test Suite Coverage

The suite is divided into specialized files (`test_ci_*.py`), each targeting a specific functional domain of the Core Server.

### 1. Execution Lifecycle (`test_ci_executions.py`)
Validates the creation, state transitions, and deletion of executions.
*   **Creation**: Calls `create_execution` [api/controllers/Execution.js:5-7]() and verifies the returned `ExecutionInfo`.
*   **Control**: Tests `halt_execution`, `pause_execution`, and `resume_execution` [api/controllers/Execution.js:57-67]().
*   **Cleanup**: Ensures `delete_execution` [api/controllers/Execution.js:13-15]() removes state from Redis and the Archive.

### 2. Procedure Management (`test_ci_procedures.py`)
Focuses on the authoring and versioning of procedures.
*   **Structure**: Tests the nested hierarchy of `SECTION`, `STEP`, `PARAGRAPH`, and `TOC` elements managed by `node_funcs.createArchiveElement` [api/controllers/ExecutionService.js:45-45]().
*   **Ordering**: Validates `move_execution_element` [api/controllers/Execution.js:85-87]() and the `insert_after_id` logic.

### 3. Step Type Integration
Individual test files verify the specific logic for different step types defined in `step_definitions.js`.

| Test File | Step Types Covered | Key Endpoints Tested |
| :--- | :--- | :--- |
| `test_ci_commands.py` | `CMD`, `CMD_FILE`, `CMD_SCMF` | `run_execution` [api/controllers/Execution.js:137-139]() |
| `test_ci_verifications.py` | `VERIFY_EHA`, `WAIT_EVR`, `CHECK_CONFIG` | `execution_compute_element` [api/controllers/Execution.js:101-103]() |
| `test_ci_manual.py` | `MANUAL_INPUT`, `MANUAL_EIP` | `execution_update_element` [api/controllers/Execution.js:97-99]() |
| `test_ci_data.py` | `LIST_DATA_PRODUCTS`, `ANALYSIS` | `get_execution_data_paths` [api/controllers/Execution.js:41-43]() |

### 4. Infrastructure and Metadata
*   **`test_ci_health.py`**: Checks server uptime and connectivity to Redis/S3.
*   **`test_ci_logging.py`**: Validates that execution logs are correctly captured and retrievable.
*   **`test_ci_labels.py`**: Tests the labeling and categorization of executions and procedures.
*   **`test_ci_files.py`**: Verifies file upload/download functionality via the File Server integration in `node_funcs.js`.

**Sources:** [api/controllers/Execution.js:5-166](), [api/controllers/ExecutionService.js:7-156]()

---

## Entity Mapping: Test to Code

This diagram maps the conceptual test actions to the specific JavaScript functions and routes they exercise within the codebase.

Title: Test Action to Code Entity Mapping
```mermaid
graph LR
    subgraph "Python Test Suite"
        [test_run_step] -- "calls" --> [run_execution]
        [test_update_input] -- "calls" --> [execution_update_element]
        [test_check_status] -- "calls" --> [get_execution_status]
    end

    subgraph "Core Server Controller (Execution.js)"
        [run_execution] -- "delegates" --> [ExecService.run_execution]
        [execution_update_element] -- "delegates" --> [ExecService.execution_update_element]
        [get_execution_status] -- "delegates" --> [ExecService.get_execution_status]
    end

    subgraph "Business Logic (node_funcs.js)"
        [ExecService.run_execution] -- "invokes" --> [node_funcs.runStep]
        [ExecService.execution_update_element] -- "invokes" --> [node_funcs.updateStep]
        [ExecService.get_execution_status] -- "queries" --> [Redis_Execution_Key]
    end
```
**Sources:** [api/controllers/Execution.js:137-147](), [api/controllers/ExecutionService.js:7-25](), [api/node_funcs.js:1-10]()

## Running the Tests

To execute the suite locally, the Core Server and its dependencies must be running.

1.  **Set Environment**: Ensure `ARCHIVE` and `EXECUTION` environment variables are set [README.md:21-29]().
2.  **Install Requirements**: Python 3.x with `unittest` and `xmlrunner`.
3.  **Execute**:
    ```bash
    cd tests
    python -m unittest discover -p "test_ci_*.py"
    ```
    Or run specific files:
    ```bash
    python executions_test.py
    python venues_test.py
    ```

**Sources:** [README.md:31-43]()
