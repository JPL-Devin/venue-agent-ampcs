# Page: ArangoDB Plugin and Data Layer

# ArangoDB Plugin and Data Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/config/env.js](src/config/env.js)
- [src/plugins/arangodb.js](src/plugins/arangodb.js)

</details>



The Ingenium Dictionary Service uses **ArangoDB** as its primary multi-model data store. The data layer is managed via a custom Fastify plugin that handles the lifecycle of the database connection, automatic schema provisioning (databases and collections), and the enforcement of persistent indexes for data integrity and query performance.

## Connection and Database Provisioning

The ArangoDB integration is encapsulated in the `arangoPlugin` function [src/plugins/arangodb.js:11-117](). Upon server startup, the plugin establishes a connection using the `arangojs` driver.

### Connection Lifecycle
1.  **System Connection**: The plugin first connects to the `_system` database [src/plugins/arangodb.js:23-23]() to perform administrative tasks.
2.  **Database Check**: It retrieves the list of existing databases [src/plugins/arangodb.js:24-24]().
3.  **Auto-Provisioning**: If the database specified by `ARANGO_DB_NAME` (defaulting to `project_config`) does not exist, the plugin creates it automatically [src/plugins/arangodb.js:26-30]().
4.  **Target Database Selection**: The plugin then switches the connection context to the specific application database [src/plugins/arangodb.js:32-32]().

### Collection Initialization
The plugin iterates through a predefined list of collection names: `dictionary`, `command`, `channel`, `evr`, `mil1553`, `vnv`, and `custom_script` [src/config/env.js:18-18](). For each name, it checks for existence and creates the collection if missing [src/plugins/arangodb.js:36-46]().

### Connection Flow
The following diagram illustrates the transition from the "Natural Language" intent of connecting to a database to the specific "Code Entities" that execute the logic.

**Database Initialization Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        "Connect to ArangoDB"
        "Provision Schema"
        "Expose DB to App"
    end

    subgraph "Code Entity Space"
        A["Database Class (arangojs)"] 
        B["arangoPlugin()"]
        C["systemDb.createDatabase()"]
        D["db.collection().create()"]
        E["fastify.decorate('db')"]
    end

    "Connect to ArangoDB" --> B
    B --> A
    "Provision Schema" --> C
    "Provision Schema" --> D
    "Expose DB to App" --> E
```
Sources: [src/plugins/arangodb.js:11-117](), [src/config/env.js:11-18]()

## Index Definitions and Data Integrity

To ensure fast lookups and prevent duplicate entries (especially during bulk uploads), the plugin defines `persistent` indexes for every collection. These indexes are applied during the plugin registration phase using `db.collection().ensureIndex()` [src/plugins/arangodb.js:98-103]().

### Index Configuration Table

| Collection | Fields | Unique | Sparse | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `dictionary` | `dictionary_type`, `dictionary_version` | Yes | No | Prevents duplicate versioning for a specific type. |
| `command` | `dictionary_type`, `dictionary_version`, `command_stem` | Yes | Yes | Ensures unique command stems within a version. |
| `evr` | `dictionary_type`, `dictionary_version`, `evr_id`, `evr_name` | Yes | Yes | Identifies unique Event Records. |
| `channel` | `dictionary_type`, `dictionary_version`, `channel_id`, `channel_name` | Yes | Yes | Identifies unique Telemetry Channels. |
| `mil1553` | `dictionary_type`, `dictionary_version`, `mil1553_name` | Yes | Yes | Uniqueness for MIL-STD-1553 definitions. |
| `vnv` | `vi_id` | Yes | Yes | Unique identifier for Verification Items. |
| `custom_script` | `script_id` | Yes | Yes | Unique identifier (SHA256) for scripts. |

Sources: [src/plugins/arangodb.js:49-104]()

## Fastify Integration

The plugin follows the standard Fastify decorator pattern to make the database instance globally accessible to routes.

### Decorator Pattern
By calling `fastify.decorate('db', db)` [src/plugins/arangodb.js:106-106](), the ArangoDB `Database` instance becomes available on the Fastify instance. This allows route handlers to access the database via `request.server.db` or `fastify.db` without re-initializing connections.

### Graceful Teardown
The plugin registers an `onClose` hook [src/plugins/arangodb.js:108-112]() to handle graceful shutdowns. When the Fastify server stops, the plugin attempts to close the ArangoDB connection, ensuring no hanging sockets remain.

**Data Layer Access Pattern**
```mermaid
graph LR
    subgraph "Code Entity Space"
        F["fastify-arangodb (Plugin)"]
        D["fastify.decorate('db')"]
        R["Route Handlers"]
        C["onClose Hook"]
    end

    subgraph "Natural Language Space"
        "Register DB Plugin"
        "Access DB in Routes"
        "Graceful Shutdown"
    end

    "Register DB Plugin" --> F
    F --> D
    D --> "Access DB in Routes"
    "Access DB in Routes" --> R
    "Graceful Shutdown" --> C
```
Sources: [src/plugins/arangodb.js:106-112](), [src/plugins/arangodb.js:119-121]()

## Configuration Parameters

The plugin relies on environment variables defined in the configuration layer to establish connectivity.

| Variable | Source | Default | Description |
| :--- | :--- | :--- | :--- |
| `ARANGO_URL` | [src/config/env.js:11]() | `http://localhost:8529` | Connection string for the ArangoDB instance. |
| `ARANGO_DB_NAME` | [src/config/env.js:12]() | `project_config` | The specific database used by the service. |
| `ARANGO_USERNAME` | [src/config/env.js:13]() | `""` | Authentication username. |
| `ARANGO_PASSWORD` | [src/config/env.js:14]() | `""` | Authentication password. |

Sources: [src/config/env.js:11-14](), [src/plugins/arangodb.js:14-20]()
