# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [package.json](package.json)

</details>



The **Ingenim Search Server** is a specialized Node.js microservice designed to provide advanced search capabilities within the OpenIngenium ecosystem [package.json:1-4](). It acts as an abstraction layer over **Elasticsearch**, offering a RESTful API that simplifies complex query building, manages user-scoped search configurations, and enforces secure access via JWT authentication [README.md:10-22]().

## Role in OpenIngenium
This service serves as the primary search engine for the OpenIngenium platform. It enables users to perform multi-index searches across diverse data types such as elements, procedures, and synchronized system data [README.md:128-133](). By providing a unified `queryBuilderParams` syntax, it allows frontend applications to construct sophisticated nested logical queries without needing to write raw Elasticsearch DSL [README.md:134-172]().

### Key Capabilities
*   **Complex Query Translation**: Converts high-level logical rules (AND/OR, nested groups) into optimized Elasticsearch DSL [README.md:134-149]().
*   **Secure Multi-Tenancy**: Uses RS256 JWT verification to ensure users can only access or manage their own saved search configurations (`querybuilders`) [README.md:174-182]().
*   **Automated Index Management**: Handles the lifecycle of Elasticsearch indices, including applying custom mappings for dates and wildcard strings during startup [README.md:126-133]().
*   **Standardized API**: Fully documented via OpenAPI 3.0, including an interactive Swagger UI for developer exploration [README.md:99-112]().

## System Relationship Diagram
The following diagram illustrates how the Search Server bridges the gap between client-side Natural Language/Logical requests and the underlying Elasticsearch Code Entity Space.

**Search Server Component Interaction**
```mermaid
graph TD
    subgraph "Natural Language Space (Client)"
        "ClientRequest"["User Search Request (JSON Rules)"]
    end

    subgraph "Search Server (Node.js/Express)"
        "app.js"["src/app.js (Bootstrap)"]
        "jwtAuth"["jwtAuth.js (Middleware)"]
        "searchController"["searchController.js (Logic)"]
        "queryBuilder"["Query Builder Engine"]
    end

    subgraph "Code Entity Space (Elasticsearch)"
        "esClient"["Elasticsearch @elastic/elasticsearch"]
        "idx_element"["Index: element"]
        "idx_proc"["Index: procedure_element"]
        "idx_qb"["Index: querybuilder"]
    end

    "ClientRequest" -- "POST /api/v1/search" --> "app.js"
    "app.js" --> "jwtAuth"
    "jwtAuth" -- "Authorized" --> "searchController"
    "searchController" --> "queryBuilder"
    "queryBuilder" -- "DSL Generation" --> "esClient"
    "esClient" --> "idx_element"
    "esClient" --> "idx_proc"
    "esClient" --> "idx_qb"
```
Sources: [src/app.js:1-10](), [README.md:128-133](), [package.json:37-49]()

## Major Subsystems

### 1. API & Middleware Layer
The service uses **Express** to manage the request lifecycle. It includes a strict OpenAPI validator and custom middleware to handle security.
*   **Authentication**: Every request (except `/health`) must include a Bearer token verified against a public RSA key defined in `PUBLIC_PEM` [README.md:54-57]().
*   **Validation**: Requests are validated against `src/api/openapi.yaml` before reaching the controllers [package.json:43]().

### 2. Query Builder Engine
The core logic of the server resides in its ability to translate a simplified JSON rule set into complex Elasticsearch queries.
*   **Operators**: Supports a range of operators including `=`, `==`, `>`, `<=`, and negated matches `!=` [README.md:138-143]().
*   **Nesting**: Supports recursive `condition` (AND/OR) blocks, allowing for infinite query depth [README.md:145-149]().

### 3. Data Integration (Elasticsearch)
The server maintains a persistent connection to Elasticsearch and ensures the environment is ready upon startup.
*   **Initialization**: On boot, the server checks for the existence of required indices (`element`, `procedure_element`, `querybuilder`, `syncdata`) and applies pre-defined mappings [README.md:126-133]().
*   **Mapping**: Specific fields are forced to `date` or `long` types, while strings default to `wildcard` for efficient partial matching [README.md:62-65]().

**Subsystem Code Entity Map**
```mermaid
graph LR
    subgraph "Routing & Auth"
        "R_Search"["/api/v1/search"]
        "R_QB"["/api/v1/querybuilders"]
        "M_JWT"["jwtAuth.js"]
    end

    subgraph "Controllers"
        "C_Search"["searchController.js"]
        "C_QB"["queryBuilderController.js"]
    end

    subgraph "Data Access"
        "Config"["mapping-config.js"]
        "Client"["Elasticsearch Client"]
    end

    "R_Search" --> "M_JWT"
    "R_QB" --> "M_JWT"
    "M_JWT" --> "C_Search"
    "M_JWT" --> "C_QB"
    "C_Search" --> "Client"
    "C_QB" --> "Client"
    "Client" -.-> "Config"
```
Sources: [README.md:85-97](), [package.json:5-10](), [README.md:238-250]()

## Getting Started
To begin working with the Ingenium Search Server, you will need to configure your environment variables (specifically the `PUBLIC_PEM` for JWT and the `ELASTIC_SEARCH_HOST`) and install dependencies.

For a step-by-step setup guide, see **[Getting Started (#1.1)]()**.
For a full list of configuration parameters, see **[Configuration Reference (#1.2)]()**.

---
Sources: [package.json:1-53](), [README.md:1-250]()
