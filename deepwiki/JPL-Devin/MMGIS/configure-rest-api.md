# Page: Configure REST API

# Configure REST API

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/bump-version.yml](.github/workflows/bump-version.yml)
- [API/Backend/Accounts/routes/accounts.js](API/Backend/Accounts/routes/accounts.js)
- [API/Backend/Config/routes/configs.js](API/Backend/Config/routes/configs.js)
- [API/Backend/Config/setup.js](API/Backend/Config/setup.js)
- [API/Backend/Config/uuids.js](API/Backend/Config/uuids.js)
- [API/Backend/Users/models/user.js](API/Backend/Users/models/user.js)
- [configure/src/components/Panel/Panel.js](configure/src/components/Panel/Panel.js)
- [configure/src/index.css](configure/src/index.css)
- [configure/src/pages/APITokens/APITokens.js](configure/src/pages/APITokens/APITokens.js)
- [configure/src/pages/Users/Modals/UpdateUserModal/UpdateUserModal.js](configure/src/pages/Users/Modals/UpdateUserModal/UpdateUserModal.js)
- [configure/src/pages/Users/Users.js](configure/src/pages/Users/Users.js)
- [docs/mmgis-openapi.json](docs/mmgis-openapi.json)
- [docs/pages/APIs/Configure/Configure_REST_API.md](docs/pages/APIs/Configure/Configure_REST_API.md)
- [src/essence/essence.js](src/essence/essence.js)

</details>



The Configure REST API provides programmatic control over MMGIS mission configurations. It enables administrators and automated systems to create missions, manage layer hierarchies, and update system settings without using the graphical `/configure` interface.

**Root Path:** `/api/configure` [docs/pages/APIs/Configure/Configure_REST_API.md:12-12]()

## Authentication & Authorization

To interact with the Configure API, requests must include a Bearer token in the `Authorization` header [docs/pages/APIs/Configure/Configure_REST_API.md:38-38](). These tokens are managed within the `/configure` UI under the "API Tokens" page [docs/pages/APIs/Configure/Configure_REST_API.md:30-37]().

### Permission Levels
The API enforces strict permission checks via the `checkMissionPermission` middleware in the `configs.js` router [API/Backend/Config/routes/configs.js:60-60]():
*   **SuperAdmins (111):** Have unrestricted access to all missions and configuration endpoints [API/Backend/Config/routes/configs.js:77-80]().
*   **Admins (110):** Can only access missions explicitly listed in their `missions_managing` database field [API/Backend/Config/routes/configs.js:91-134]().
*   **Users/None:** Denied access to all configuration endpoints [API/Backend/Config/routes/configs.js:83-89]().

### Data Flow: Configuration Request Authorization
This diagram illustrates how the `configs.js` router validates a request against the `User` model and session state.

Title: "Configure API Authorization Flow"
```mermaid
graph TD
    subgraph "Request_Entry"
        ["REQ (HTTP Request)"] --> ["MW (checkMissionPermission Middleware)"]
    end

    subgraph "Logic_configs_js"
        ["MW"] --> ["AUTH_TYPE (isLongTermToken?)"]
        ["AUTH_TYPE"] -- "Yes" --> ["LT_PERM (Use tokenUserPermission)"]
        ["AUTH_TYPE"] -- "No" --> ["SS_PERM (Use session.permission)"]
        
        ["LT_PERM"] --> ["LVL_CHECK (Permission Level?)"]
        ["SS_PERM"] --> ["LVL_CHECK"]
        
        ["LVL_CHECK"] -- "111 (SuperAdmin)" --> ["NEXT (next() - Authorized)"]
        ["LVL_CHECK"] -- "110 (Admin)" --> ["DB_CHECK (User.findOne missions_managing)"]
        ["LVL_CHECK"] -- "Other" --> ["REJECT (403 Unauthorized)"]
        
        ["DB_CHECK"] --> ["MIS_CHECK (Mission in list?)"]
        ["MIS_CHECK"] -- "Yes" --> ["NEXT"]
        ["MIS_CHECK"] -- "No" --> ["REJECT"]
    end

    subgraph "Database_Entities"
        ["DB_CHECK"] -.-> ["USER_TBL (User Table)"]
    end
```
Sources: [API/Backend/Config/routes/configs.js:59-149](), [API/Backend/Config/routes/configs.js:15-16](), [API/Backend/Users/models/user.js:10-53]()

---

## Key Endpoints

### GET `/missions`
Returns a list of all missions configured in the system.
*   **Query Parameter:** `full=true` returns the complete configuration object and version for every mission [docs/pages/APIs/Configure/Configure_REST_API.md:44-50]().

### GET `/get`
Retrieves a specific mission configuration.
*   **Parameters:** `mission` (required), `version` (optional, defaults to latest) [docs/pages/APIs/Configure/Configure_REST_API.md:86-94]().
*   **Implementation:** The `get` function queries the `Config` model using `mission` and `version` as filters [API/Backend/Config/routes/configs.js:151-186](). It also handles fallback logic for `missionFolderName` if it is missing from the configuration, defaulting it to the mission name [API/Backend/Config/routes/configs.js:189-195]().

### POST `/upsert`
Sets the entire configuration object for a mission. This endpoint creates a new entry in the `configs` table, incrementing the version number [docs/pages/APIs/Configure/Configure_REST_API.md:116-125](). It uses the `populateUUIDs` utility to ensure all layers in the new configuration have valid identifiers [API/Backend/Config/routes/configs.js:43-43]().

### POST `/addLayer`
Adds one or more layers to a mission.
*   **Placement:** Supports `placement.path` (header name) and `placement.index` for precise positioning within the layer tree [docs/pages/APIs/Configure/Configure_REST_API.md:136-142]().
*   **Implementation:** A wrapping helper to `upsert` that modifies the existing layer array before saving a new version [docs/pages/APIs/Configure/Configure_REST_API.md:132-134]().

### POST `/updateLayer`
Performs a deep merge of the provided `layer` object with the existing layer identified by `layerUUID` [docs/pages/APIs/Configure/Configure_REST_API.md:150-158](). This allows updating specific properties (like URLs or symbology) without resubmitting the entire configuration.

### POST `/removeLayer`
Removes a layer by its `layerUUID` [docs/pages/APIs/Configure/Configure_REST_API.md:175-181]().

Sources: [docs/pages/APIs/Configure/Configure_REST_API.md:44-181](), [API/Backend/Config/routes/configs.js:151-232]()

---

## Layer UUID Management

MMGIS uses UUIDs to track layers across versions. When a configuration is updated via the API, the system ensures every layer has a valid UUID via `uuids.js`.

1.  **Traversal:** The `populateUUIDs` function traverses the entire `layers` array using `Utils.traverseLayers` [API/Backend/Config/uuids.js:5-11]().
2.  **Validation:** If a layer lacks a UUID or has a numeric placeholder, a new `v4` UUID is generated using the `uuid` package [API/Backend/Config/uuids.js:22-23]().
3.  **Conflict Resolution:** If a `proposed_uuid` conflicts with an existing layer or the existing UUID fails `uuidValidate`, it is regenerated to ensure uniqueness [API/Backend/Config/uuids.js:32-46]().

Sources: [API/Backend/Config/uuids.js:1-65]()

---

## Real-time Updates

The Configure API supports immediate synchronization with active clients using WebSockets and the `forceClientUpdate` mechanism.

### forceClientUpdate
When calling `addLayer`, `updateLayer`, or `removeLayer`, setting `forceClientUpdate: true` triggers a system-wide notification [docs/pages/APIs/Configure/Configure_REST_API.md:142-142]().

### Implementation Logic
Title: "Real-time Configuration Update Flow"
```mermaid
graph LR
    subgraph "Server_Node_js"
        ["API (POST /updateLayer)"] --> ["DB (Config.create New Version)"]
        ["DB"] --> ["WS_CHECK (forceClientUpdate == true?)"]
        ["WS_CHECK"] -- "Yes" --> ["WS_SEND (websocket.send 'update' data)"]
    end

    subgraph "Clients_Browser"
        ["WS_SEND"] -.->|WebSocket| ["ESS (essence.js)"]
        ["ESS"] --> ["WS_ON (ws.onmessage)"]
        ["WS_ON"] --> ["UI_NOTIFY (UserInterface_.addLayerUpdateButton())"]
    end
```
Sources: [API/Backend/Config/routes/configs.js:46-47](), [src/essence/essence.js:162-200](), [docs/pages/APIs/Configure/Configure_REST_API.md:142-142]()

### WebSocket Connection
The client-side `essence.js` manages the WebSocket lifecycle:
*   **Initialization:** `essence.initWebSocket(path)` creates the connection using `isomorphic-ws` [src/essence/essence.js:162-163]().
*   **Retry Logic:** If the connection fails, it doubles the `webSocketRetryInterval` (starting at 60 seconds) before attempting to reconnect [src/essence/essence.js:135-158]().
*   **Message Handling:** When an `update` message is received, the client UI is notified. If the connection is healthy, `UserInterface_.removeLayerUpdateButton()` is called [src/essence/essence.js:180-184]().

Sources: [src/essence/essence.js:21-21](), [src/essence/essence.js:131-200]()

---

## Configuration Integration

The API is served via the `configs.js` router, which is mounted in `setup.js` [API/Backend/Config/setup.js:47-53]().

### Environment Variables
The following variables in `.env` affect the Configure API behavior:
*   `HIDE_CONFIG`: If set to `"true"`, the `/configure` route and `/api/configure` endpoints are disabled [API/Backend/Config/setup.js:8-11]().
*   `ENABLE_CONFIG_WEBSOCKETS`: Toggles the WebSocket synchronization feature [API/Backend/Config/setup.js:26-26]().
*   `AUTH`: Determines the authentication strategy (e.g., `csso`, `local`) used to identify users [API/Backend/Config/setup.js:17-17]().

Sources: [API/Backend/Config/setup.js:1-63]()
