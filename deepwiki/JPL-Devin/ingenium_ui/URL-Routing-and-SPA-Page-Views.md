# URL Routing and SPA Page Views

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ingenium-https.conf](ingenium-https.conf)
- [ingenium.conf](ingenium.conf)
- [src/apps/ingenium_login/urls.py](src/apps/ingenium_login/urls.py)

</details>



This section documents the Django URL configuration and the mechanism by which the backend serves various Single Page Application (SPA) entry points. The Ingenium UI uses a hybrid approach where Django handles top-level routing and authentication, while specific feature modules (Authoring, Execution, Admin, etc.) are served as independent Vue.js SPAs.

## Main URL Configuration

The root URL configuration is defined in `src/ingenium/urls.py`. It acts as the primary router, delegating requests to specialized URL modules based on the path prefix.

### URL Modules Overview
| Prefix | Module | Purpose |
| :--- | :--- | :--- |
| `admin/` | `django.contrib.admin.urls` | Standard Django administrative interface. |
| `api/` | `apps.ingenium_api.urls` | Internal AJAX endpoints for frontend-to-backend communication. |
| `login/`, `logout/` | `apps.ingenium_login.urls` | Authentication flow handling (login, logout, and token renewal). |
| `/` (Root) | `apps.ingenium_pages.urls` | SPA shell pages and page-specific views. |

The `ingenium_login` application handles the authentication routes:
*   `login/` maps to `login_request` [src/apps/ingenium_login/urls.py:6-6]().
*   `logout/` maps to `logout_request` [src/apps/ingenium_login/urls.py:7-7]().
*   `renew/` maps to `renew_token_request` [src/apps/ingenium_login/urls.py:8-8]().

**Sources:** [src/apps/ingenium_login/urls.py:1-10]()

## SPA Page Routing and JS Bundle Injection

The core of the user interface is delivered via `apps.ingenium_pages.urls`. Instead of a single monolithic SPA, Ingenium UI is partitioned into several functional SPAs to optimize bundle size and separation of concerns.

### Mapping Routes to Bundles
Each SPA route in Django corresponds to a specific template. These templates inject hashed JavaScript bundle filenames, which are determined at build time and stored in Django settings (e.g., `base.py`).

| Route Path | View Function | JS Bundle (Settings Var) | Module Purpose |
| :--- | :--- | :--- | :--- |
| `/` | `dashboard_view` | `JS_BUNDLE_DASHBOARD` | Main dashboard with venue tiles. |
| `authoring/` | `authoring_view` | `JS_BUNDLE_AUTHORING` | Procedure authoring and versioning. |
| `execution/` | `execution_view` | `JS_BUNDLE_EXECUTION` | Real-time procedure execution. |
| `admin/` | `admin_view` | `JS_BUNDLE_ADMIN` | User, role, and venue management. |
| `search/` | `search_view` | `JS_BUNDLE_SEARCH` | Global search and query builder. |
| `reporting/` | `reporting_view` | `JS_BUNDLE_REPORTING` | As-run report generation. |

### Bundle Resolution Flow
The following diagram illustrates how a request for a specific SPA page (e.g., Authoring) results in the injection of the correct hashed production asset.

**SPA Asset Injection Flow**
```mermaid
graph TD
    "Browser" -- "GET /authoring/" --> "Django_Router[urls.py]"
    "Django_Router[urls.py]" --> "Authoring_View[views.authoring_view]"
    "Authoring_View[views.authoring_view]" -- "Fetch bundle name" --> "Settings[base.py]"
    "Settings[base.py]" -- "JS_BUNDLE_AUTHORING" --> "Authoring_View[views.authoring_view]"
    "Authoring_View[views.authoring_view]" -- "Render template" --> "Template[authoring.html]"
    "Template[authoring.html]" -- "Inject <script src='/static/authoring.hash.js'>" --> "Browser"
```

**Sources:** [src/apps/ingenium_login/urls.py:1-9]()

## Nginx Reverse Proxy Integration

While Django handles the application logic and initial SPA page delivery, Nginx acts as the entry point and reverse proxy for the entire microservices architecture. It intercepts specific paths and routes them either to the Django UI container or directly to backend services (Core, Dict, Auth).

### Nginx Routing Table
Nginx configuration files (`ingenium.conf` and `ingenium-https.conf`) define how traffic is distributed.

| Path Prefix | Destination Upstream | Description |
| :--- | :--- | :--- |
| `/static/` | `/src/static` | Serves CSS, JS bundles, and images directly from disk [ingenium-https.conf:68-73](). |
| `/core_server/` | `core_server:8080` | Proxy to Core microservice [ingenium-https.conf:83-95](). |
| `/dict_server/` | `dict_service:5000` | Proxy to Dictionary microservice [ingenium-https.conf:108-120](). |
| `/auth_server/` | `auth_service:8080` | Proxy to Auth microservice [ingenium-https.conf:122-134](). |
| `/execution_monitor/`| `execution_monitor:3000` | WebSocket proxy for real-time execution updates [ingenium-https.conf:203-214](). |
| `/` | `ui:5000` | Default route to the Django Gunicorn server [ingenium-https.conf:217-229](). |

### Code-to-System Mapping
This diagram maps Nginx configuration blocks to the corresponding backend upstream services.

**Nginx Upstream Mapping**
```mermaid
graph LR
    subgraph "Nginx Reverse Proxy"
        "Nginx_Conf[ingenium-https.conf]"
    end

    subgraph "Upstream Services"
        "UI_Srv[upstream ui]"
        "Core_Srv[upstream core_server]"
        "Dict_Srv[upstream dict_server]"
        "Auth_Srv[upstream auth_service]"
        "Exec_Mon[upstream execution_monitor]"
    end

    "Nginx_Conf[ingenium-https.conf]" -- "proxy_pass http://ui" --> "UI_Srv[upstream ui]"
    "Nginx_Conf[ingenium-https.conf]" -- "proxy_pass http://core_server" --> "Core_Srv[upstream core_server]"
    "Nginx_Conf[ingenium-https.conf]" -- "proxy_pass http://dict_server" --> "Dict_Srv[upstream dict_server]"
    "Nginx_Conf[ingenium-https.conf]" -- "proxy_pass http://auth_service" --> "Auth_Srv[upstream auth_service]"
    "Nginx_Conf[ingenium-https.conf]" -- "proxy_pass http://execution_monitor" --> "Exec_Mon[upstream execution_monitor]"
```

**Sources:** [ingenium-https.conf:1-230](), [ingenium.conf:1-168]()

## Partial and Modal URL Patterns

In addition to SPA shell pages, the routing system supports "Partials" and "Modals." These are smaller HTML fragments or specialized views served by Django that are often loaded into the SPA via AJAX or iframes.

*   **Admin URLs:** Managed in `pages_admin_urls.py`, these routes handle administrative views that are integrated into the Admin SPA bundle.
*   **Modal Patterns:** Specific routes designated for pop-up dialogs that require backend-driven content or complex form handling before the SPA takes over the interaction.

**Sources:** [src/apps/ingenium_login/urls.py:1-9](), [ingenium-https.conf:217-229]()
