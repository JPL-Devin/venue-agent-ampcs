# Role-Based Access Control (RBAC)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [image/api/controllers/subscription_controller.js](image/api/controllers/subscription_controller.js)
- [tests/subscription_rbac.test.js](tests/subscription_rbac.test.js)

</details>



The Ingenium Notification Service implements a strict Role-Based Access Control (RBAC) model to ensure data isolation between users while providing administrative oversight. This logic is primarily enforced within the controller layer, utilizing security context (identity and roles) provided by the upstream JWT authentication middleware.

## Permission Model Overview

The system distinguishes between two primary roles:
1.  **Basic User**: Can only view, create, update, or delete subscriptions where the `user_name` matches their own JWT `sub` or `username` claim.
2.  **Admin**: Has global visibility and can perform operations on behalf of any user by specifying a `user_name`.

### Logic Flow Diagram
The following diagram illustrates how the `subscription_controller.js` handles requests based on the user's role.

**Controller RBAC Logic Flow**
```mermaid
graph TD
    "req[Request Object]" --> "check_isAdmin[req.isAdmin?]"
    
    "check_isAdmin" -- "No (Basic User)" --> "BasicUserPath[Enforce Ownership]"
    "check_isAdmin" -- "Yes (Admin)" --> "AdminPath[Grant Global Access]"

    subgraph "Basic User Path"
        "BasicUserPath" --> "List_Basic[Filter query by req.username]"
        "BasicUserPath" --> "Create_Basic[Force user_name = req.username]"
        "BasicUserPath" --> "Update_Basic[Strip user_name from body]"
        "BasicUserPath" --> "AuthCheck_Basic[Check subscription.user_name == req.username]"
    end

    subgraph "Admin Path"
        "AdminPath" --> "List_Admin[Optional filter by query param]"
        "AdminPath" --> "Create_Admin[Allow any user_name]"
        "AdminPath" --> "Update_Admin[Allow user_name modification]"
        "AdminPath" --> "AuthCheck_Admin[Bypass ownership check]"
    end

    "AuthCheck_Basic" --> "Decision{Match?}"
    "Decision" -- "Yes" --> "Success[Allow Operation]"
    "Decision" -- "No" --> "Error403[403 Forbidden]"
```
**Sources:** [image/api/controllers/subscription_controller.js:24-114]()

---

## Key Implementation Patterns

### 1. Scoped List Queries
In the `list_subscriptions` handler, the database query is conditionally modified. For basic users, a `.where({ user_name: req.username })` clause is mandatory. Admins see all records by default but can optionally filter by a `user_name` provided in the request parameters.

**Implementation:** [image/api/controllers/subscription_controller.js:28-35]()
**Test Coverage:** [tests/subscription_rbac.test.js:66-94]()

### 2. User Identification Enforcement
When creating or updating subscriptions, the controller ensures a user cannot impersonate another:

*   **Create**: If `req.isAdmin` is false, the `user_name` in the payload is overwritten with `req.username` [image/api/controllers/subscription_controller.js:48-50]().
*   **Update**: If `req.isAdmin` is false, the `user_name` field is deleted from the update payload entirely, preventing users from "transferring" their subscriptions to others [image/api/controllers/subscription_controller.js:86-88]().

### 3. The `getSubscriptionWithAuthCheck` Pattern
This helper function is the central point for enforcing ownership on individual resource access (GET, PATCH, DELETE by ID).

**Implementation:** [image/api/controllers/subscription_controller.js:11-22]()

| Scenario | Result | Status Code |
| :--- | :--- | :--- |
| Resource does not exist | Returns `null` | `404 Not Found` |
| Resource exists, User is Admin | Returns `subscription` | `200 OK` |
| Resource exists, `user_name` matches `req.username` | Returns `subscription` | `200 OK` |
| Resource exists, `user_name` mismatch | Returns `null` | `403 Forbidden` |

**Sources:** [image/api/controllers/subscription_controller.js:11-22](), [tests/subscription_rbac.test.js:138-169]()

---

## Data Flow & Sanitization

The controller uses a whitelist-based sanitization approach to prevent mass-assignment vulnerabilities.

**Code Entity Relationship**
```mermaid
graph LR
    subgraph "Input Handling"
        "req.swagger.params[Swagger Params]" --> "body[Raw Body]"
    end

    subgraph "Sanitization & Security"
        "body" --> "sanitizeBody[sanitizeBody function]"
        "ALLOWED_FIELDS[ALLOWED_FIELDS Whitelist]" -.-> "sanitizeBody"
        "sanitizeBody" --> "sanitized[Sanitized Object]"
        "req.isAdmin[req.isAdmin Flag]" --> "UpdateLogic{Update Handler}"
        "UpdateLogic" -- "isAdmin == false" --> "Strip[Delete user_name]"
        "Strip" --> "sanitized"
    end

    subgraph "Persistence"
        "sanitized" --> "knex[db('user_subscriptions')]"
    end
```

### Whitelist Fields
The `ALLOWED_FIELDS` array defines the only keys permitted to reach the database:
*   `user_name`
*   `event_type`
*   `channel`
*   `enabled`
*   `filters`

**Sources:** [image/api/controllers/subscription_controller.js:5-9]()

---

## Error Handling Distinctions

The service makes a clear distinction between resource visibility and authorization:

1.  **404 Not Found**: Returned when the `id` provided does not exist in the `user_subscriptions` table [image/api/controllers/subscription_controller.js:13-16]().
2.  **403 Forbidden**: Returned when the resource exists, but the `user_name` associated with the record does not match the authenticated `req.username` (and the user is not an admin) [image/api/controllers/subscription_controller.js:17-20]().

**Sources:** [image/api/controllers/subscription_controller.js:11-22](), [tests/subscription_rbac.test.js:147-154]()
