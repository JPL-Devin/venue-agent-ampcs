# Page: Architecture

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [package.json](package.json)
- [src/app.js](src/app.js)

</details>



The Ingenium Search Server is a Node.js microservice built on the Express framework, designed to interface between authenticated clients and an Elasticsearch backend. Its primary responsibility is translating complex, human-readable search parameters into optimized Elasticsearch Domain Specific Language (DSL) while enforcing security through JWT verification.

### System Overview

The server follows a layered architecture where requests flow through a strictly ordered middleware pipeline before reaching dynamic route handlers. These handlers delegate business logic to controllers, which interact with Elasticsearch via a centralized configuration and client.

#### High-Level Request Flow
The diagram below illustrates how a request traverses the system components, from initial entry in `app.js` to the final data retrieval from Elasticsearch.

**Request Lifecycle Diagram**
```mermaid
graph TD
    subgraph ["Entry Point (src/app.js)"]
        A["Client Request"] --> B["Middleware Pipeline"]
    end

    subgraph ["Middleware Layer (src/middlewares/)"]
        B --> C["jwtAuth.js (RS256)"]
        C --> D["addUsernameToResponse.js"]
        D --> E["OpenApiValidator"]
    end

    subgraph ["Routing & Controllers (src/routes/ & src/controllers/)"]
        E --> F["Router (Dynamic Loading)"]
        F --> G["searchController.js"]
        F --> H["queryBuilderController.js"]
        F --> I["healthController.js"]
    end

    subgraph ["Data Layer (src/config/)"]
        G --> J["elasticsearch-config.js"]
        H --> J
        J --> K[("Elasticsearch Instance")]
    end
```
**Sources:** [src/app.js:15-71](), [src/middlewares/jwtAuth.js:1-35](), [src/middlewares/addUsernameToResponse.js:1-15]()

---

### Application Bootstrap

The entry point of the application is `src/app.js`, which initializes the Express instance and coordinates the startup sequence. The bootstrap process ensures that the Elasticsearch cluster is reachable and that indices are correctly mapped before the HTTP server begins listening for requests.

*   **Service Startup**: The `startService()` function [src/app.js:64-69]() executes `initElasticsearch()` [src/config/elasticsearch-config.js:114-142]() to verify connectivity and apply index mappings before calling `app.listen()`.
*   **Middleware Ordering**: Middleware is registered in a specific sequence to ensure security (JWT) and validation (OpenAPI) occur before any business logic is executed.

For details, see [Application Bootstrap (app.js)](#2.1).

**Sources:** [src/app.js:1-71](), [src/config/elasticsearch-config.js:114-142]()

---

### Middleware Layer

The middleware layer handles cross-cutting concerns such as security, request logging, and schema validation. It acts as a gatekeeper for the routing layer.

| Middleware | File | Purpose |
| :--- | :--- | :--- |
| **JWT Auth** | `src/middlewares/jwtAuth.js` | Verifies RS256 signatures using `PUBLIC_PEM` [src/middlewares/jwtAuth.js:12-23](). |
| **User Injection** | `src/middlewares/addUsernameToResponse.js` | Extracts `username` from the decoded JWT and attaches it to `res.locals` [src/middlewares/addUsernameToResponse.js:7-12](). |
| **OpenAPI Validator** | `express-openapi-validator` | Validates request bodies and parameters against `src/api/openapi.yaml` [src/app.js:41-47](). |

For details, see [Middleware Layer](#2.2).

**Sources:** [src/middlewares/jwtAuth.js:1-35](), [src/middlewares/addUsernameToResponse.js:1-15](), [src/app.js:41-47]()

---

### Routing and Controller Layer

The server uses a dynamic routing mechanism to load endpoints from the `src/routes/` directory. Each route maps a URL path (prefixed with `/api/v1`) to a specific controller function.

**Code Entity Mapping: Routes to Controllers**
```mermaid
graph LR
    subgraph ["Routes (src/routes/)"]
        R1["searchRoutes.js"]
        R2["queryBuilderRoutes.js"]
        R3["healthRoutes.js"]
    end

    subgraph ["Controllers (src/controllers/)"]
        C1["searchController.js"]
        C2["queryBuilderController.js"]
        C3["healthController.js"]
    end

    R1 -- "POST /search" --> C1
    R2 -- "GET/POST/DELETE /querybuilders" --> C2
    R3 -- "GET /health" --> C3
```

*   **Dynamic Loading**: The `loadRoutes()` function [src/app.js:18-26]() iterates through the `routes` folder and mounts every file ending in `.js` to the Express application.
*   **Controller Logic**: Controllers are responsible for interpreting the request, interacting with the Elasticsearch `client`, and returning the appropriate HTTP response.

For details, see [Routing Layer](#2.3).

**Sources:** [src/app.js:18-26](), [src/routes/searchRoutes.js:1-10](), [src/routes/queryBuilderRoutes.js:1-15]()

---

### Logging Subsystem

The application utilizes a centralized logging system based on the `winston` library. This ensures consistent formatting across all modules and provides different log levels (info, error, etc.) for production monitoring and debugging.

*   **Logger Configuration**: Defined in `src/utils/logger.js` [src/utils/logger.js:1-25]().
*   **Usage**: The logger is imported globally and used to track service startup, Elasticsearch connection retries, and request errors.

For details, see [Logging](#2.4).

**Sources:** [src/utils/logger.js:1-25](), [src/app.js:67-67]()
