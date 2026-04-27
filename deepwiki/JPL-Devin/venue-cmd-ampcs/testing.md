# Page: Testing

# Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/README.md](tests/README.md)
- [tests/env.csh](tests/env.csh)
- [tests/requirements.txt](tests/requirements.txt)
- [tests/venue_client.py](tests/venue_client.py)

</details>



The VenueServer test suite provides a comprehensive framework for validating the integration between the FastAPI application, the Mission Test Automation Kit (MTAK), and the Advanced Multi-Mission Operations System (AMMOS) Mission Planning and Control Subsystem (AMPCS). Testing is divided into automated integration tests and manual example scripts, both of which utilize a dedicated client helper library.

## Test Architecture Overview

The testing environment is designed to operate against live or simulated mission environments (e.g., Europa or Psyche WSTS). It relies on a pre-configured Python virtual environment and specific environment variables to target active AMPCS sessions.

### System Test Flow
The following diagram illustrates how the test infrastructure interacts with the VenueServer and the underlying GDS components.

**Test Execution Pipeline**
```mermaid
graph TD
    subgraph "Test Environment"
        [Pytest_Runner] --> [test_mtak.py]
        [Pytest_Runner] --> [test_single_session.py]
        [test_mtak.py] --> [venue_client.py]
        [Example_Scripts] --> [venue_client.py]
    end

    subgraph "VenueServer"
        [venue_client.py] -- "REST API (JWT Auth)" --> [FastAPI_Endpoints]
        [FastAPI_Endpoints] --> [venue_core.py]
    end

    subgraph "External Systems"
        [venue_core.py] -- "Process Spawning" --> [MTAK_Sessions]
        [venue_core.py] -- "CLI/Socket" --> [AMPCS_Sessions]
        [MTAK_Sessions] -- "Session ID" --> [AMPCS_Sessions]
    end

    [env.csh] -- "TEST_AMPCS_SESSION_ID_A/B" --> [Pytest_Runner]
```
**Sources:** [tests/README.md:1-40](), [tests/venue_client.py:10-14]()

## Test Infrastructure & Integration Tests

The automated test suite uses `pytest` to execute integration scenarios. These tests require live AMPCS sessions to be manually started before execution. The session identifiers are passed to the tests via the `env.csh` environment file.

*   **Virtual Environment:** A dedicated environment (`ve3`) is used to manage dependencies like `pytest`, `requests`, and `PyJWT` [tests/requirements.txt:1-4]().
*   **Session Management:** Tests reference `TEST_AMPCS_SESSION_ID_A` and `TEST_AMPCS_SESSION_ID_B` to simulate multi-session scenarios [tests/env.csh:1-2]().
*   **Integration Files:**
    *   `test_mtak.py`: Validates MTAK lifecycle (start/shutdown) and command dispatch.
    *   `test_single_session.py`: Focuses on single-stream telemetry and commanding.

For details on environment setup and running specific test cases, see **[Test Infrastructure & Integration Tests](#6.1)**.

**Sources:** [tests/README.md:1-52](), [tests/env.csh:1-3]()

## Venue Client Helper Library

The `venue_client.py` file serves as a shared library for both automated tests and example scripts. It encapsulates the complexity of JWT generation and REST communication.

### Key Components of venue_client.py
| Component | Role |
| :--- | :--- |
| `generate_exec_token()` | Generates a RS256 JWT using `exec_venue_private_pem.pem` for authentication [tests/venue_client.py:25-42](). |
| `start_mtak()` | Wraps the `/mtak/start` endpoint to initialize MTAK processes [tests/venue_client.py:64-70](). |
| `send_fsw_cmd()` | Wraps `/cmd/fsw_cmd` for Flight Software commanding [tests/venue_client.py:77-89](). |
| `query_rt_evr()` | Wraps `/evr/realtime` for GlobalLAD telemetry queries [tests/venue_client.py:102-116](). |
| `query_chill_evr()` | Wraps `/evr/chill` for historical CHILL telemetry queries [tests/venue_client.py:118-132](). |

**Sources:** [tests/venue_client.py:1-228]()

## Example Scripts

The `tests/examples/` directory contains standalone Python scripts that demonstrate how to use the VenueServer API for specific operational tasks. These serve as both documentation by example and tools for manual verification.

### Example Mapping
```mermaid
graph LR
    subgraph "Commanding Examples"
        [send_cmd.py]
        [send_sse_cmds.py]
        [send_file.py]
    end

    subgraph "Telemetry Examples"
        [check_rt_evr.py]
        [check_chill_eha.py]
        [bus_1553.py]
    end

    subgraph "Workflow Examples"
        [client_example.py]
        [run_cs.py]
    end

    [venue_client.py] --> [Commanding Examples]
    [venue_client.py] --> [Telemetry Examples]
    [venue_client.py] --> [Workflow Examples]
```

These scripts cover the full breadth of the API, including binary file uplinks, SCMF transfers, custom script execution, and 1553 bus log retrieval.

For a complete list of available scripts and their usage, see **[Example Scripts](#6.2)**.

**Sources:** [tests/venue_client.py:185-228](), [tests/README.md:47-52]()
