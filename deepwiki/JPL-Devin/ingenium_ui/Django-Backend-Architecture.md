# Django Backend Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile](Dockerfile)
- [__init__.py](__init__.py)
- [src/apps/__init__.py](src/apps/__init__.py)

</details>



The Ingenium UI backend is built on the Django framework, serving primarily as a **thin orchestration and proxy layer**. Unlike traditional Django applications, this backend does not maintain a persistent relational database (e.g., PostgreSQL or MySQL). Instead, it manages user sessions, performs authentication against external services, and proxies requests to various microservices (Core, Auth, Dictionary, and VNV).

The backend is responsible for serving the Single Page Application (SPA) shells, injecting environment-specific configurations into templates, and providing a unified AJAX API for the Vue.js frontend.

### System Entrypoint and Runtime

The application is served using **Gunicorn** as the WSGI HTTP Server, typically configured with `gevent` workers to handle asynchronous proxy requests efficiently.

```mermaid
graph TD
    subgraph "External World"
        "UserBrowser"["User Browser"]
    end

    subgraph "Ingenium UI Container"
        "Gunicorn"["Gunicorn (WSGI)"]
        "WSGI"["ingenium.wsgi"]
        "Middleware"["Middleware Stack"]
        "URLConf"["URL Routing (urls.py)"]
    end

    subgraph "External Microservices"
        "CoreSvc"["Core Service"]
        "AuthSvc"["Auth Service"]
        "DictSvc"["Dictionary Service"]
    end

    "UserBrowser" -- "HTTP Request" --> "Gunicorn"
    "Gunicorn" -- "Calls" --> "WSGI"
    "WSGI" -- "Passes through" --> "Middleware"
    "Middleware" -- "Routes to" --> "URLConf"
    "URLConf" -- "Proxy Request" --> "CoreSvc"
    "URLConf" -- "Proxy Request" --> "AuthSvc"
    "URLConf" -- "Proxy Request" --> "DictSvc"
```
**Sources:**
- [Dockerfile:73-75]() - Defines the Gunicorn entrypoint using `ingenium.wsgi`.

---

### Core Components

#### 1. Settings and Configuration
The system uses a hierarchical settings structure. `base.py` contains the core logic, including the definition of all external service endpoints and the logic to map hashed JS bundle filenames (generated during the build process) to environment variables.
*   **For details, see [Settings and Configuration](#2.1).**

#### 2. Authentication and Session Management
Authentication is handled via a custom JWT-based flow. The backend stores access tokens in secure, HTTP-only cookies and uses a custom `IngeniumUserBackend` to validate users against the external Auth service. It maintains state using `IngeniumUser` and `IngeniumAnonymousUser` models.
*   **For details, see [Authentication and Session Management](#2.2).**

#### 3. Proxy Layer and API Controllers
Since there is no local database, the backend acts as a gateway. The `request_controller.py` provides helper methods to forward frontend AJAX calls to the appropriate microservice. Specific controllers (e.g., `venue_controller`, `user_controller`) wrap these requests to provide a clean API for the Vue frontend.
*   **For details, see [Proxy Layer and API Controllers](#2.3).**

#### 4. URL Routing and SPA Page Views
The routing system is split between traditional Django views (for serving the SPA HTML shells) and AJAX endpoints. The `page_urls.py` file maps browser URLs to views that load the correct Vue.js bundles for different modules like "Authoring" or "Executions."
*   **For details, see [URL Routing and SPA Page Views](#2.4).**

#### 5. Data Models and Context Processors
Python-side data models in `ingenium_models/` act as Data Transfer Objects (DTOs) for the JSON responses received from microservices. Context processors are used to inject global variables, such as user session data and venue types, into every Django template.
*   **For details, see [Data Models and Context Processors](#2.5).**

---

### Code Entity Mapping

The following diagram maps the high-level architectural concepts to the specific Python packages and modules within the codebase.

```mermaid
graph LR
    subgraph "Django Project Root [src/]"
        "SettingsPkg"["ingenium/settings/"]
        "URLSRoot"["ingenium/urls.py"]
        "WSGIMod"["ingenium/wsgi.py"]
    end

    subgraph "Application Logic [src/apps/]"
        "AuthLogic"["ingenium_auth/"]
        "Controllers"["ingenium_controllers/"]
        "Models"["ingenium_models/"]
        "Middleware"["ingenium_middleware/"]
    end

    "WSGIMod" --> "URLSRoot"
    "URLSRoot" --> "Controllers"
    "URLSRoot" --> "AuthLogic"
    "Middleware" -- "Intercepts" --> "URLSRoot"
    "Controllers" -- "Uses" --> "Models"
    "SettingsPkg" -- "Configures" --> "WSGIMod"
```
**Sources:**
- [Dockerfile:50-50]() - Shows the source code root being copied to `/src`.
- [Dockerfile:75-75]() - References the `ingenium.wsgi` module.

### Middleware Stack
The backend utilizes a specialized middleware stack to handle the "database-less" nature of the application. These middlewares ensure that every request is authenticated against the external Auth service and that session data is hydrated from the JWT before reaching the view logic.

| Middleware | Responsibility |
| :--- | :--- |
| `IngeniumUserMiddleware` | Hydrates the `request.user` object from the JWT cookie. |
| `IngeniumSessionMiddleware` | Manages session-specific data retrieved from microservices. |
| `LoginRequiredMiddleware` | Enforces authentication for all non-whitelisted routes. |

**Sources:**
- [Dockerfile:63-64]() - Requirements installation including Django and support libraries.
