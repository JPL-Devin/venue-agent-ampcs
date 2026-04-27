# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [main.py](main.py)
- [openapi.yaml](openapi.yaml)

</details>



The **Ingenium VenueServer** is a high-performance ground data system (GDS) interface designed to bridge external mission operations software with JPL's Advanced Multi-Mission Operations System (AMMOS) Mission Planning and Control Subsystem (AMPCS). It provides a unified RESTful API for commanding, telemetry retrieval, and data product management, abstracting the complexities of underlying GDS components like MTAK, GlobalLAD, and CHILL.

## System Purpose and Role
VenueServer acts as the primary gateway for automated testing and mission operations tools to interact with the spacecraft GDS. It manages mission-specific sessions and provides a standardized interface for:
*   **Commanding:** Dispatching FSW, HW, and SSE commands via the Mission Test Automation Kit (MTAK) [main.py:169-243]().
*   **Telemetry:** Querying real-time Event Records (EVR) and Engineering Health Analysis (EHA) data via GlobalLAD, or historical data via CHILL [main.py:347-495]().
*   **Automation:** Executing and monitoring custom Python scripts within the GDS environment [main.py:615-728]().
*   **Bus Analysis:** Decoding MIL-STD-1553 bus logs into human-readable signals [main.py:581-613]().

### Ground System Ecosystem
The following diagram illustrates how VenueServer sits between external clients and the internal JPL GDS ecosystem.

**VenueServer Integration Context**
```mermaid
graph TD
    subgraph "External Client Space"
        [Client_App] -->|HTTPS/JSON| [NGINX_Proxy]
    end

    subgraph "VenueServer Tier"
        [NGINX_Proxy] -->|Proxy_Pass| [FastAPI_VenueServer_Instance]
        [FastAPI_VenueServer_Instance] <--> [Redis_State_Store]
    end

    subgraph "JPL GDS Tier (AMPCS/MTAK)"
        [FastAPI_VenueServer_Instance] -->|Subprocess/RPC| [MTAK_Engine]
        [FastAPI_VenueServer_Instance] -->|TCP/HTTPS| [GlobalLAD]
        [FastAPI_VenueServer_Instance] -->|CLI_Execution| [CHILL_Tools]
        [MTAK_Engine] <--> [AMPCS_Session]
    end

    [GlobalLAD] -.-> [AMPCS_Session]
    [CHILL_Tools] -.-> [AMPCS_Session]
```
Sources: [README.md:37-76](), [main.py:96-104](), [core/venue_core.py:1-50]()

---

## Key Architectural Concepts

### Multi-Instance Scalability
The VenueServer is designed to run as multiple independent FastAPI instances (typically on ports 19443, 19444, etc.) behind an NGINX reverse proxy [README.md:37-46](). This allows for high availability and isolation between different mission sessions or user groups.

### Worker Process Isolation
To prevent blocking the main FastAPI event loop during long-running GDS operations (like command dispatching), VenueServer utilizes a `WorkerProcess` pattern [core/mtak_cmd.py:1-20](). This ensures that MTAK interactions, which may involve synchronous waits or signal handling conflicts, are isolated from the web server's execution context.

### Bridging Natural Language to Code Entities
The following diagram maps high-level GDS concepts to their specific implementations within the codebase.

**Code Entity Mapping**
```mermaid
graph LR
    subgraph "Natural Language Concept"
        A["REST API Gateway"]
        B["Command Dispatcher"]
        C["Telemetry Provider"]
        D["1553 Decoder"]
    end

    subgraph "Code Entity Space"
        A --- [main.py_APIRouter]
        B --- [core/mtak_cmd.py]
        C --- [core/lad_query.py]
        C --- [core/chill_query.py]
        D --- [core/decode_1553.py]
    end

    [main.py_APIRouter] --> [core/venue_core.py_Orchestrator]
    [core/venue_core.py_Orchestrator] --> [core/mtak_cmd.py]
    [core/venue_core.py_Orchestrator] --> [core/lad_query.py]
```
Sources: [main.py:96-98](), [core/venue_core.py:10-30](), [core/mtak_cmd.py:22-45]()

---

## Child Pages

For detailed technical information, refer to the following sub-pages:

### [System Architecture](#1.1)
Detailed breakdown of the multi-tier deployment involving NGINX, FastAPI, and Redis. It covers the request lifecycle and how the server maintains state across mission sessions.

### [Getting Started & Deployment](#1.2)
Instructions for setting up the Python virtual environment (`venv3`), configuring mission-specific environment variables (e.g., `ING_VENUE_DIR`, `CHILL_GDS`), and starting the services for Europa or Psyche missions [README.md:8-35]().

---

## Core Technologies
| Component | Technology | Role |
| :--- | :--- | :--- |
| **Web Framework** | `FastAPI` | Provides the REST API and OpenAPI documentation [main.py:73-74]() |
| **State Management** | `Redis` | Stores session information and global state [README.md:28-35]() |
| **Data Validation** | `Pydantic` | Ensures request/response integrity via `schema.py` [main.py:79-88]() |
| **Reverse Proxy** | `NGINX` | Handles SSL termination and load balancing [README.md:50-72]() |
| **GDS Interface** | `MTAK` | Underlying library for mission command and control [README.md:139-139]() |

Sources: [main.py:1-90](), [README.md:1-150]()
