# Page: Core Architecture

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/app.js](src/app.js)
- [src/server.js](src/server.js)

</details>



The Ingenium Dictionary Service is built using the **Fastify** framework, chosen for its low overhead and powerful plugin architecture. The system follows a modular design where core concerns—such as database connectivity, authentication, and API documentation—are encapsulated in plugins and registered during the server bootstrap process.

## System Assembly Overview

The service initialization follows a linear execution path starting from the entry point, which configures the environment and starts the HTTP server. The architecture relies on the Fastify "encapsulation" model to manage the lifecycle of database connections and security middleware.

### Request Lifecycle and Code Mapping

The following diagram illustrates how an incoming HTTP request traverses the system entities defined in the codebase.

**Diagram: Request Processing Flow**
```mermaid
graph TD
    subgraph "Fastify Instance [src/server.js]"
        "HTTP_Request" --> "Logger [pino]"
        "Logger [pino]" --> "Auth_Plugin [src/plugins/auth.js]"
        "Auth_Plugin [src/plugins/auth.js]" --> "Router"
        
        subgraph "Route_Handlers"
            "Router" --> "Dictionary_Routes [src/routes/dictionary.js]"
            "Router" --> "Content_Routes [src/routes/dictionaryContent.js]"
            "Router" --> "VnV_Routes [src/routes/vnv.js]"
        end
        
        "Route_Handlers" --> "Arango_Plugin [src/plugins/arangodb.js]"
        "Arango_Plugin [src/plugins/arangodb.js]" --> "Database [ArangoDB]"
    end

    "Route_Handlers" -. "Error Thrown" .-> "Global_ErrorHandler [src/server.js:77-92]"
    "Global_ErrorHandler [src/server.js:77-92]" --> "HTTP_Response"
    "Database [ArangoDB]" --> "HTTP_Response"
```
**Sources:** [src/server.js:28-100](), [src/app.js:1-15]()

---

## Server Bootstrap and Configuration

The service entry point is `src/app.js`, which imports the configured Fastify instance and starts listening on the designated `APP_HOST` and `APP_PORT`. 

The core configuration logic resides in `src/server.js`. Key responsibilities include:
*   **Logging**: Environment-aware logging using `pino-pretty` for development and standard JSON logging for production [src/server.js:14-27]().
*   **OpenAPI/Swagger**: Automatic generation of API documentation via `@fastify/swagger`, accessible at the `/api-docs` endpoint [src/server.js:38-73]().
*   **Global Error Handling**: A centralized `setErrorHandler` that normalizes validation errors and internal server errors into a standard JSON format [src/server.js:77-92]().

For details, see [Server Bootstrap and Configuration](#2.1).

**Sources:** [src/app.js:4-15](), [src/server.js:14-31](), [src/server.js:77-92]()

---

## ArangoDB Plugin and Data Layer

The service uses **ArangoDB** as its primary data store. Connectivity is managed through a custom Fastify plugin located in `src/plugins/arangodb.js`. 

This plugin is responsible for:
*   Establishing a connection to the `_system` database using credentials from the environment.
*   Ensuring the target database and all required collections (e.g., `dictionary`, `command`, `evr`) exist upon startup.
*   Defining persistent indexes to optimize query performance for dictionary lookups.
*   Decorating the Fastify instance with a `db` object, making the database driver accessible to all route handlers.

For details, see [ArangoDB Plugin and Data Layer](#2.2).

**Sources:** [src/server.js:35](), [src/plugins/arangodb.js:1-10]() (referenced via registration)

---

## Authentication Plugin

Security is enforced via a JWT-based authentication mechanism registered as a global plugin. The `src/plugins/auth.js` module handles the extraction and verification of Bearer tokens using a public RSA key (`PUBLIC_PEM`).

Key features include:
*   **Request Decoration**: Successfully verified tokens result in the decoded payload being attached to `request.user`.
*   **Decorator Pattern**: The plugin provides a `fastify.authenticate` method, which is used as a `preHandler` hook on protected routes to restrict access.

For details, see [Authentication Plugin](#2.3).

**Sources:** [src/server.js:33](), [src/config/env.js:5]()

---

## Route Organization

All service endpoints are prefixed with `/api/v4` and are organized by functional domain. The registration order in `src/server.js` ensures that plugins (DB and Auth) are available before routes are initialized.

**Table: Route Module Mapping**

| Domain | Route File | Prefix |
| :--- | :--- | :--- |
| System Health | `src/routes/health.js` | `/api/v4` |
| Dictionary Versions | `src/routes/dictionary.js` | `/api/v4` |
| Dictionary Content | `src/routes/dictionaryContent.js` | `/api/v4` |
| V&V Items | `src/routes/vnv.js` | `/api/v4` |
| Custom Scripts | `src/routes/customScript.js` | `/api/v4` |

**Sources:** [src/server.js:95-99]()
