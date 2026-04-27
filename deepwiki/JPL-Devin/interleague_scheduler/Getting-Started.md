# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [frontend/package.json](frontend/package.json)
- [frontend/vite.config.ts](frontend/vite.config.ts)
- [interleague_scheduler/__init__.py](interleague_scheduler/__init__.py)
- [interleague_scheduler/config.py](interleague_scheduler/config.py)
- [pyproject.toml](pyproject.toml)

</details>



This guide provides a step-by-step walkthrough for setting up the **Interleague Scheduler** development environment. The project consists of a FastAPI backend and a Vue 3 frontend, designed to coordinate sports games across different organizations.

## Prerequisites

The system requires the following software:
*   **Python 3.11+**: Required for the backend [pyproject.toml:9-9]().
*   **Node.js & npm**: Required for building and running the frontend [frontend/package.json:1-28]().
*   **Virtual Environment Tool**: `venv` is recommended for Python dependency isolation.

---

## Backend Setup

The backend uses FastAPI with SQLAlchemy for ORM and Pydantic for configuration and validation [README.md:17-27]().

### 1. Installation
Navigate to the project root and create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
```

Install the package in editable mode with development dependencies:
```bash
pip install -e ".[dev]"
```
*Sources: [README.md:31-36](), [pyproject.toml:22-28]()*

### 2. Configuration
The application uses `pydantic-settings` to manage configuration. All environment variables must be prefixed with `ILS_` [interleague_scheduler/config.py:17-17]().

| Variable | Default | Description |
| :--- | :--- | :--- |
| `ILS_DATABASE_URL` | `sqlite:///./interleague_scheduler.db` | SQLAlchemy connection string [interleague_scheduler/config.py:5-5]() |
| `ILS_SECRET_KEY` | `change-me-in-production` | Key for JWT signing [interleague_scheduler/config.py:9-9]() |
| `ILS_GOOGLE_CLIENT_ID` | `""` | OAuth2 Client ID [interleague_scheduler/config.py:13-13]() |
| `ILS_GOOGLE_CLIENT_SECRET` | `""` | OAuth2 Client Secret [interleague_scheduler/config.py:14-14]() |

*Sources: [interleague_scheduler/config.py:4-17](), [README.md:47-52]()*

### 3. Running the Backend
Start the development server using Uvicorn with the `--reload` flag enabled for hot-reloading:
```bash
uvicorn interleague_scheduler.main:app --reload
```
*Sources: [README.md:39-39]()*

### 4. Interactive API Documentation
Once the server is running, you can access the auto-generated Swagger UI:
*   **URL**: `http://127.0.0.1:8000/docs`
*   **Alternative (ReDoc)**: `http://127.0.0.1:8000/redoc`

---

## Frontend Setup

The frontend is a Vue 3 application built with Vite and styled with Vuetify [frontend/package.json:11-17]().

### 1. Installation
Navigate to the `frontend` directory and install dependencies:
```bash
cd frontend
npm install
```

### 2. Development Server
Run the Vite development server:
```bash
npm run dev
```
The frontend is configured to proxy `/api` requests to `http://localhost:8000` to avoid CORS issues during development [frontend/vite.config.ts:6-13]().

---

## System Integration Flow

The following diagram illustrates how the development environment components interact, bridging the natural language concepts to the specific code entities.

### Environment and Data Flow
"Vite" manages the "Frontend" and proxies requests to "Uvicorn" which serves the "FastAPI" application. The "Settings" class loads "Environment Variables" to configure the "SQLAlchemy Engine".

```mermaid
graph TD
    subgraph "Client Space"
        "Browser" -- "localhost:5173" --> "Vite_Dev_Server[Vite Dev Server]"
    end

    subgraph "Frontend Code Entity Space"
        "Vite_Dev_Server" -- "Proxy /api" --> "Backend_Entry[Uvicorn]"
        "Vite_Dev_Server" -.-> "ViteConfig[vite.config.ts]"
    end

    subgraph "Backend Code Entity Space"
        "Backend_Entry" --> "FastAPI_App[interleague_scheduler.main:app]"
        "FastAPI_App" --> "Config_Settings[interleague_scheduler.config:Settings]"
        "Config_Settings" -- "Reads ILS_ prefix" --> "Env_Vars[Environment Variables]"
        "FastAPI_App" --> "DB_Engine[SQLAlchemy Engine]"
        "DB_Engine" --> "SQLite_File[interleague_scheduler.db]"
    end

    style "ViteConfig" stroke-dasharray: 5 5
    style "Env_Vars" stroke-dasharray: 5 5
```
*Sources: [frontend/vite.config.ts:7-13](), [interleague_scheduler/config.py:4-20](), [README.md:39-42]()*

---

## Code Entity Mapping

The table below maps high-level development tasks to the specific files and classes responsible for them.

| Task | Code Entity / File | Description |
| :--- | :--- | :--- |
| **Dependency Management** | `pyproject.toml` | Defines Python dependencies and dev tools like `ruff` and `pytest` [pyproject.toml:10-28](). |
| **App Configuration** | `interleague_scheduler.config:Settings` | Pydantic class that handles `ILS_` environment variables [interleague_scheduler/config.py:4-17](). |
| **API Entry Point** | `interleague_scheduler.main:app` | The FastAPI application instance used by Uvicorn [README.md:39-39](). |
| **Frontend Proxy** | `frontend/vite.config.ts` | Configures Vite to route `/api` calls to the Python backend [frontend/vite.config.ts:7-13](). |
| **Frontend Scripts** | `frontend/package.json` | Defines `dev`, `build`, and `preview` scripts [frontend/package.json:6-10](). |

### Development Component Interaction
This diagram maps the relationship between the configuration entities and the runtime environment.

```mermaid
classDiagram
    class "Settings" {
        +database_url: str
        +secret_key: str
        +env_prefix: ILS_
    }
    class "ViteConfig" {
        +target: http://localhost:8000
        +changeOrigin: true
    }
    class "PyProject" {
        +dependencies: list
        +dev_dependencies: list
    }

    "Settings" <|-- "interleague_scheduler.config.py" : "Defined in"
    "ViteConfig" <|-- "frontend/vite.config.ts" : "Defined in"
    "PyProject" <|-- "pyproject.toml" : "Defined in"

    "Backend Runtime" ..> "Settings" : "Initializes"
    "Frontend Runtime" ..> "ViteConfig" : "Uses for API routing"
```
*Sources: [interleague_scheduler/config.py:4-20](), [frontend/vite.config.ts:4-14](), [pyproject.toml:5-28]()*
