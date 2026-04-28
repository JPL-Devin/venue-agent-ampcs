# Page: Ingenium VenueServer — Overview

# Ingenium VenueServer — Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [main.py](main.py)
- [openapi.yaml](openapi.yaml)

</details>



The **Ingenium VenueServer** is a high-performance web service built with **FastAPI** that acts as a bridge between the Ingenium automation framework and the **AMMOS/AMPCS** (Advanced Multi-Mission Operations System / Advanced Multi-Mission Project Control System) ground data system. It provides a standardized REST API for commanding, telemetry retrieval, and custom script execution, supporting critical missions such as **Europa Clipper** and **Psyche**.

The server is designed to operate within the JPL WSTS (Workstation Test Set) environment, abstracting the complexities of MTAK (Mission Tool Agile Kit) and AMPCS CLI tools into a unified, secure interface.

### System Architecture

The VenueServer follows a layered architecture to ensure isolation between the web interface and the mission-critical ground system processes.

#### High-Level Data Flow
The system utilizes **NGINX** as a reverse proxy for SSL termination and port mapping, **FastAPI** for request handling and business logic, and **REDIS** for state persistence (specifically for custom script execution).

"VenueServer System Context"
```mermaid
graph TD
    subgraph "External Clients"
        [Client] -- "HTTPS (9443-9445)" --> [NGINX]
    end

    subgraph "GDS Host (VenueServer Node)"
        [NGINX] -- "HTTP (19443-19445)" --> [FastAPI_App]
        [FastAPI_App] -- "Persistence" --> [REDIS_Server]
        
        subgraph "Core Logic"
            [FastAPI_App] --> [venue_core]
            [venue_core] --> [mtak_cmd]
            [venue_core] --> [lad_query]
            [venue_core] --> [chill_query]
        end
    end

    subgraph "AMPCS Ecosystem"
        [mtak_cmd] --> [MTAK_Worker_Process]
        [lad_query] --> [GlobalLAD]
        [chill_query] --> [AMPCS_CLI_Tools]
    end
```
**Sources:** [README.md:37-75](), [main.py:96-104](), [core/venue_core.py:1-50]()

### Mission Support
The codebase is parameterized to support multiple missions through environment configuration files.
*   **Europa Clipper:** Configured via `config/europa_dev_envs.sh` [README.md:18-21]().
*   **Psyche:** Configured via `config/psyche_dev_envs.sh` [README.md:23-26]().

### Core Components and Entities

The following diagram bridges the high-level system components to the specific code entities defined in the repository.

"Code Entity Mapping"
```mermaid
graph LR
    subgraph "API Layer (main.py)"
        [Route_MTAK] --> [start_mtak]
        [Route_CMD] --> [fsw_cmd]
        [Route_TLM] --> [get_evr_rt]
    end

    subgraph "Logic Layer (core/)"
        [venue_core] --> [core_start_mtak]
        [venue_core] --> [core_send_fsw_cmd]
        [venue_core] --> [core_get_evr_rt]
    end

    subgraph "Schema & Models (core/schema.py)"
        [MtakStartBodyModel]
        [FswCmdBodyModel]
        [EVRObjectResp]
    end

    [start_mtak] -- "Uses" --> [MtakStartBodyModel]
    [fsw_cmd] -- "Calls" --> [core_send_fsw_cmd]
    [core_get_evr_rt] -- "Returns" --> [EVRObjectResp]
```
**Sources:** [main.py:120-146](), [main.py:169-195](), [core/venue_core.py:53-100](), [core/schema.py:1-100]()

### Key Functional Areas

| Component | Description | Primary Code Entry Point |
| :--- | :--- | :--- |
| **MTAK Management** | Orchestrates AMPCS sessions and MTAK process lifecycles. | `core/venue_core.py:core_start_mtak` |
| **Commanding** | Dispatches FSW, HW, and SSE commands, including binary file uploads. | `core/venue_core.py:core_send_fsw_cmd` |
| **Telemetry (RT)** | Real-time queries against `GlobalLAD` for EVRs and EHA channels. | `core/lad_query.py` |
| **Telemetry (Historical)** | Historical queries using AMPCS `CHILL` command-line utilities. | `core/chill_query.py` |
| **1553 Bus Decoding** | Parses and decodes MIL-STD-1553 bus logs using XML dictionaries. | `core/decode_1553.py` |
| **Custom Scripts** | Asynchronous execution of user-defined Python scripts with artifact tracking. | `main.py` (Custom Script Endpoints) |

**Sources:** [main.py:78-89](), [core/venue_core.py:15-40]()

---

### Detailed Documentation Sections

For in-depth technical details, refer to the following child pages:

*   **[Getting Started: Installation and Deployment](#1.1)**
    How to set up the `venv3` environment, initialize the server using `setup_venueserver.sh`, and manage the NGINX/REDIS services.
*   **[Environment Configuration](#1.2)**
    Detailed breakdown of mission-specific environment variables (e.g., `ING_VENUE_DIR`, `CHILL_GDS`, `LAD_HOST`) and how they influence system behavior.
*   **[Infrastructure: NGINX, REDIS, and Logging](#1.3)**
    Technical specifications for the reverse proxy setup, the use of REDIS for script state, and the `log_config.yaml` rotating log system.
