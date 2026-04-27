# Page: Core Systems

# Core Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.env](.env)
- [src/core/constants.js](src/core/constants.js)
- [src/core/redux/actions/actions.js](src/core/redux/actions/actions.js)
- [src/core/redux/reducers/reducers.js](src/core/redux/reducers/reducers.js)
- [src/core/redux/store/initial.js](src/core/redux/store/initial.js)
- [src/pages/FileExplorer/Columns/Columns.js](src/pages/FileExplorer/Columns/Columns.js)

</details>



The **Core Systems** module provides the foundational infrastructure for the Atlas application. It encompasses global state management, centralized application constants, utility functions for data manipulation, and the routing logic that connects the primary functional pages. These systems are designed to be environment-agnostic through a runtime configuration injection pattern, allowing the same build to be deployed across various NASA/JPL environments by checking `window.APP_CONFIG` before falling back to build-time environment variables.

### System Architecture Overview

The following diagram illustrates how core modules interact with the React application lifecycle and external services.

**Core System Dependencies**
```mermaid
graph TD
    subgraph "External Space"
        "window.APP_CONFIG"["window.APP_CONFIG (Runtime)"]
        "process.env"["process.env (Build-time)"]
        "ES"["Elasticsearch API"]
    end

    subgraph "Core Systems"
        "runtimeConfig"["runtimeConfig.js"]
        "constants"["constants.js"]
        "utils"["utils.js"]
        "ReduxStore"["Redux Store (Immutable.js)"]
    end

    subgraph "Routing & UI"
        "AppRoutes"["AppRoutes (routes.js)"]
        "Search"["Search Page"]
        "Record"["Record Page"]
        "Cart"["Cart Page"]
        "FileExplorer"["Archive Explorer"]
    end

    "window.APP_CONFIG" --> "runtimeConfig"
    "process.env" --> "runtimeConfig"
    "runtimeConfig" --> "constants"
    "constants" --> "utils"
    "constants" --> "AppRoutes"
    
    "AppRoutes" --> "Search"
    "AppRoutes" --> "Record"
    "AppRoutes" --> "Cart"
    "AppRoutes" --> "FileExplorer"
    
    "Search" --> "ReduxStore"
    "ReduxStore" -- "loadMappings" --> "ES"
```
**Sources:** [src/core/runtimeConfig.js:15-114](), [src/core/constants.js:1-41](), [src/core/redux/actions/actions.js:127-152]()

---

### Redux State Management
Atlas uses Redux for global state management, leveraging **Immutable.js** to ensure state transitions are predictable and efficient. The store, initialized in `src/core/redux/store/initial.js`, manages several critical domains:
*   **Search State:** Active filters, facet counts, and search results [src/core/redux/actions/actions.js:34-64]().
*   **Cart State:** Items selected for download, persisted via `localStorage` [src/core/constants.js:43](), with actions like `ADD_TO_CART` and `REMOVE_FROM_CART` [src/core/redux/actions/actions.js:80-84]().
*   **Archive State:** Column-based navigation history for the `FileExplorer` managed via `ADD_FILEX_COLUMN` and `QUERY_FILEX_COLUMN` [src/core/redux/actions/actions.js:70-79]().
*   **Mappings:** Elasticsearch index schemas loaded during application initialization via `loadMappings` to build dynamic facets [src/core/redux/actions/actions.js:127-152]().

For details, see [Redux State Management](#2.1).

**Sources:** [src/core/redux/store/initial.js:27-155](), [src/core/redux/actions/actions.js:33-92](), [src/core/redux/reducers/reducers.js:7-62]()

---

### Constants and Configuration
The application maintains a centralized repository of constants in `src/core/constants.js`. This includes:
*   **Service Endpoints:** Resolved via `runtimeConfig.js` to support dynamic environment switching, including `search`, `pit`, and `scroll` [src/core/constants.js:21-30]().
*   **ES_PATHS:** A comprehensive mapping of application logic keys (e.g., `mission`, `instrument`, `geo_location`) to their specific paths within the Elasticsearch JSON document [src/core/constants.js:45-105]().
*   **Route Definitions:** Defined in `HASH_PATHS` to ensure consistent internal linking [src/core/constants.js:34-41]().
*   **Domain Mappings:** `DISPLAY_NAME_MAPPINGS` provides human-readable labels for mission and spacecraft IDs (e.g., mapping `cas` to `Cassini`) [src/core/constants.js:221-232]().

**Code Entity Mapping: Configuration**
```mermaid
graph LR
    subgraph "Code Entity Space"
        "ES_PATHS"["ES_PATHS Object"]
        "HASH_PATHS"["HASH_PATHS Object"]
        "runtimeConfig"["getRuntimeConfig()"]
        "DISPLAY_NAME_MAPPINGS"["DISPLAY_NAME_MAPPINGS"]
    end

    subgraph "Natural Language Space"
        "Metadata"["Metadata Field Mappings"]
        "Routing"["URL Route Definitions"]
        "Env"["Environment Variables"]
        "Labels"["Human Readable Labels"]
    end

    "ES_PATHS" --- "Metadata"
    "HASH_PATHS" --- "Routing"
    "runtimeConfig" --- "Env"
    "DISPLAY_NAME_MAPPINGS" --- "Labels"
```
**Sources:** [src/core/constants.js:45-105](), [src/core/constants.js:34-41](), [src/core/constants.js:221-232](), [src/core/runtimeConfig.js:103-114]()

For details, see [Constants and Configuration](#2.2).

---

### Utilities and URL Handling
The `src/core/utils.js` module provides essential helpers for interacting with PDS data and the Atlas API.
*   **URI Parsing:** `splitUri()` decomposes internal Atlas URIs into mission, spacecraft, and bundle components [src/core/utils.js:76-96]().
*   **PDS URL Resolution:** `getPDSUrl()` constructs valid data access URLs, handling `release_id` and image resizing parameters defined in `AVAILABLE_URI_SIZES` [src/core/utils.js:50-57](), [src/core/constants.js:130]().
*   **Object Traversal:** `getIn()` and `setIn()` provide safe access to deeply nested objects, similar to Immutable.js patterns but for standard JS objects [src/core/utils.js:112-133]().
*   **Field Merging:** `mergeFields()` allows filter field states to update dynamically based on new Elasticsearch responses while preserving user selection states [src/core/utils.js:138-173]().

For details, see [Utilities and URL Handling](#2.3).

---

### Routing
The application uses `react-router-dom` for navigation. The `HASH_PATHS` constant defines the primary entry points:
*   `/search`: The main faceted search interface [src/core/constants.js:36]().
*   `/record`: Detailed view for individual PDS products [src/core/constants.js:37]().
*   `/cart`: Management of items queued for download [src/core/constants.js:38]().
*   `/archive-explorer`: Columnar browsing of the PDS archive [src/core/constants.js:39]().

The application `basename` is dynamically determined by `getPublicUrl()` to support hosting the application under subdirectories (e.g., `/beta` as defined in `.env`) [src/core/constants.js:18](), [.env:6]().

**Sources:** [src/core/constants.js:34-41](), [src/core/runtimeConfig.js:15-20](), [.env:6-14]()
