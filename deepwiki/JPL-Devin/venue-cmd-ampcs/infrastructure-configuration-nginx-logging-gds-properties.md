# Page: Infrastructure Configuration (NGINX, Logging, GDS Properties)

# Infrastructure Configuration (NGINX, Logging, GDS Properties)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [config/gds_config/ampcs.properties](config/gds_config/ampcs.properties)
- [core/config.py](core/config.py)
- [log_config.yaml](log_config.yaml)
- [nginx.conf.template](nginx.conf.template)

</details>



This page details the infrastructure components that support the VenueServer, including the NGINX reverse proxy configuration for SSL termination and port mapping, the centralized logging system, and the GDS property definitions that ensure compatibility with AMPCS data schemas.

## NGINX Reverse Proxy

The VenueServer utilizes NGINX as a front-facing reverse proxy to handle SSL/TLS termination and to route external requests to the appropriate internal FastAPI instances. The configuration is managed via a template that uses environment variables for path resolution.

### Port Mapping and Routing
The infrastructure maps external HTTPS ports (9443-9445) to internal loopback ports (19443-19445) where the Uvicorn/FastAPI instances reside. Each external port corresponds to a specific mission environment or instance [nginx.conf.template:37-127]().

| External Port (SSL) | Internal Port (HTTP) | Purpose |
| :--- | :--- | :--- |
| 9443 | 19443 | Instance 1 (e.g., Europa) |
| 9444 | 19444 | Instance 2 (e.g., Psyche) |
| 9445 | 19445 | Instance 3 (General/Test) |

### Security and Proxy Headers
The NGINX configuration enforces several security measures:
*   **SSL/TLS**: Uses TLSv1.2 with a specific suite of ECDHE ciphers [nginx.conf.template:46-47]().
*   **HSTS**: Injects `Strict-Transport-Security` headers to enforce HTTPS [nginx.conf.template:39]().
*   **Header Forwarding**: Passes critical client information to the FastAPI backend using `X-Real-IP`, `X-Forwarded-For`, and `X-Forwarded-Host` [nginx.conf.template:55-57]().
*   **Timeouts**: Configured with a 300-second (5-minute) timeout for proxy read/send operations to accommodate long-running telemetry queries [nginx.conf.template:29-31]().

### Request Flow Diagram

**Title: NGINX Request Routing Architecture**
```mermaid
graph TD
    subgraph "External_Network"
        "Client"["HTTPS Client"]
    end

    subgraph "NGINX_Reverse_Proxy"
        "N_9443"["Listen 9443 (SSL)"]
        "N_9444"["Listen 9444 (SSL)"]
        "N_9445"["Listen 9445 (SSL)"]
    end

    subgraph "VenueServer_Instances"
        "VS_1"["FastAPI (Port 19443)"]
        "VS_2"["FastAPI (Port 19444)"]
        "VS_3"["FastAPI (Port 19445)"]
    end

    "Client" -- "GET /api/v3/evr" --> "N_9443"
    "N_9443" -- "proxy_pass http://127.0.0.1:19443" --> "VS_1"
    "N_9444" -- "proxy_pass http://127.0.0.1:19444" --> "VS_2"
    "N_9445" -- "proxy_pass http://127.0.0.1:19445" --> "VS_3"

    style "N_9443" stroke-dasharray: 5 5
    style "N_9444" stroke-dasharray: 5 5
    style "N_9445" stroke-dasharray: 5 5
```
**Sources:** [nginx.conf.template:36-127]()

## Logging Configuration

Logging is centralized via `log_config.yaml`, which integrates with Python's standard `logging` library and the Uvicorn web server.

### Log Handlers and Rotation
The system employs two primary handlers:
1.  **Console Handler**: Outputs `DEBUG` level logs to `stdout` [log_config.yaml:8-12]().
2.  **Rotating File Handler**: Writes to a file defined by the `${ING_LOG_DIR}` environment variable. It is configured for a maximum size of 50MB per file with a retention of 20 backup copies [log_config.yaml:13-20]().

### Uvicorn Integration
The configuration explicitly captures Uvicorn's internal logs (`uvicorn.error` and `uvicorn.access`), ensuring that HTTP access logs and server-level errors are funneled through the same formatting and rotation logic [log_config.yaml:27-32]().

### Log Format
Logs use a timestamped format: `[%(asctime)s.%(msecs)03dZ] %(name)s %(levelname)s %(message)s` [log_config.yaml:4-6]().

**Sources:** [log_config.yaml:1-32]()

## GDS Properties (ampcs.properties)

The `ampcs.properties` file is a critical configuration for the CHILL (Historical Telemetry) subsystem. It defines the exact CSV column ordering expected when VenueServer executes CHILL CLI commands (e.g., `chill_get_evrs`).

### Schema Definitions
The VenueServer relies on these specific schemas to correctly parse the output of AMPCS queries into internal Python objects.

| Property Key | Purpose | Key Columns |
| :--- | :--- | :--- |
| `csvQuery.EvrQuery` | Event Record (EVR) schema | `sessionId`, `name`, `level`, `sclk`, `scet`, `message` [config/gds_config/ampcs.properties:3]() |
| `csvQuery.ChanvalQuery` | Channel Value (EHA) schema | `channelId`, `name`, `ert`, `sclk`, `dn`, `eu`, `status` [config/gds_config/ampcs.properties:5]() |
| `csvQuery.ProductQuery` | Data Product (DP) schema | `productType`, `scet`, `fullPath`, `fileSize`, `checksum` [config/gds_config/ampcs.properties:7]() |

### Integration with Code Entities

**Title: GDS Property to Code Mapping**
```mermaid
graph LR
    subgraph "ampcs.properties"
        "E_PROP"["csvQuery.EvrQuery"]
        "C_PROP"["csvQuery.ChanvalQuery"]
        "P_PROP"["csvQuery.ProductQuery"]
    end

    subgraph "Telemetry_Subsystem"
        "CHILL"["chill_query.py"]
        "LAD"["lad_query.py"]
    end

    "E_PROP" -- "Defines CSV columns for" --> "CHILL"
    "C_PROP" -- "Defines CSV columns for" --> "CHILL"
    "P_PROP" -- "Defines CSV columns for" --> "CHILL"
    
    "CHILL" -- "Uses" --> "SHORT_TIMEOUT"
    "LAD" -- "Uses" --> "SCLKSCET_LOOKBACK"
```
**Sources:** [config/gds_config/ampcs.properties:1-8](), [core/config.py:1-3]()

## Runtime Constants

Additional infrastructure behavior is controlled by constants in `core/config.py`:
*   `SHORT_TIMEOUT`: Default timeout (10s) for standard operations [core/config.py:1]().
*   `SCLKSCET_LOOKBACK`: The window (30s) used when correlating SCLK and SCET time systems [core/config.py:2]().
*   `REVERSE_SCMF_TIMEOUT`: A longer timeout (60s) specifically for reverse SCMF (Spacecraft Message Format) processing [core/config.py:3]().

**Sources:** [core/config.py:1-3]()
