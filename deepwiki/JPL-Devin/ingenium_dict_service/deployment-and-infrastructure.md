# Page: Deployment and Infrastructure

# Deployment and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [LICENSE](LICENSE)

</details>



This section provides an overview of how the Ingenium Dictionary Service is packaged, configured, and licensed for deployment. The service is designed to run as a containerized microservice, relying on environment variables for runtime configuration and adhering to the Apache License 2.0 for redistribution and use.

## Containerization Overview

The service utilizes Docker to ensure a consistent runtime environment across development, testing, and production. The build process is optimized using a lightweight Alpine-based Node.js image to minimize the attack surface and image size.

### Build and Runtime Lifecycle
The `Dockerfile` defines a standard lifecycle for the application:
1.  **Base Image**: Uses `node:20-alpine` for a minimal footprint [[Dockerfile:2-2]]().
2.  **Environment Setup**: Sets the working directory to `/app` [[Dockerfile:5-5]]().
3.  **Dependency Management**: Executes `npm ci --production` to ensure only necessary runtime dependencies are installed, ignoring `devDependencies` [[Dockerfile:11-11]]().
4.  **Networking**: Exposes port `5000` for the Fastify server [[Dockerfile:14-14]]().
5.  **Execution**: Boots the service via `node src/app.js` [[Dockerfile:17-17]]().

For detailed documentation on the Docker configuration, including `.dockerignore` rules and local development overrides, see [Docker and Containerization](#6.1).

### Infrastructure Component Mapping
The following diagram illustrates how the codebase entities map to the infrastructure and deployment environment.

**Infrastructure to Code Mapping**
```mermaid
graph TD
    subgraph "Environment Space"
        [".env / Shell"] -- "Injects" --> ["Process Environment"]
    end

    subgraph "Container Space (Dockerfile)"
        ["node:20-alpine"] -- "WORKDIR" --> ["/app"]
        ["/app"] -- "Entrypoint" --> ["src/app.js"]
    end

    subgraph "Code Entity Space"
        ["src/app.js"] -- "Calls" --> ["src/server.js"]
        ["src/server.js"] -- "Reads" --> ["process.env.APP_PORT"]
        ["src/server.js"] -- "Reads" --> ["process.env.ARANGO_URL"]
    end

    ["Process Environment"] -.-> ["process.env.APP_PORT"]
    ["Process Environment"] -.-> ["process.env.ARANGO_URL"]
```
Sources: [[Dockerfile:1-17]](), [[.dockerignore:1-2]]()

## Configuration and Secrets

The service is configured entirely through environment variables, following the 12-factor app methodology. This allows the same Docker image to be deployed across multiple environments (e.g., CI, Staging, Production) without modification.

Critical configuration categories include:
*   **Server Settings**: `APP_PORT`, `APP_HOST`, and `NODE_ENV`.
*   **Database Connectivity**: `ARANGO_URL`, `ARANGO_DB_NAME`, and credentials.
*   **Security**: `PUBLIC_PEM` for JWT verification.

Security is maintained by excluding sensitive files like `secret.txt`, `.env` files, and `.pem` keys from the repository via `.gitignore` [[.gitignore:8-15]]() and ensuring they are not baked into the Docker image via `.dockerignore` [[.dockerignore:1-1]]().

For a full list of required variables and their roles, see [Docker and Containerization](#6.1).

## Licensing

The Ingenium Dictionary Service is released under the **Apache License, Version 2.0**. This is a permissive license that allows for:
*   **Commercial Use**: Use of the software for commercial purposes.
*   **Modification**: The ability to change the source code.
*   **Distribution**: The right to redistribute the original or modified code.

The license includes a grant of patent rights from contributors to users [[LICENSE:73-81]]() and a defensive patent termination clause to protect the community [[LICENSE:81-87]](). All redistributions must include a copy of the license and appropriate attribution [[LICENSE:89-114]]().

For a summary of legal obligations and the full license text, see [License](#6.2).

### License and Contribution Flow
The following diagram shows how the Apache 2.0 license governs the relationship between contributors and the work.

**License Governance Model**
```mermaid
graph LR
    subgraph "Natural Language Space (Legal)"
        ["Contributor"] -- "Grants Rights" --> ["Apache License 2.0"]
        ["Apache License 2.0"] -- "Protects" --> ["You (User/Entity)"]
    end

    subgraph "Code Entity Space"
        ["LICENSE File"] -- "Defines" --> ["Work"]
        ["NOTICE File"] -- "Attribution" --> ["Derivative Works"]
        ["Source Code"] -- "Is" --> ["Work"]
    end

    ["Apache License 2.0"] -.-> ["LICENSE File"]
    ["Contributor"] -.-> ["Source Code"]
```
Sources: [[LICENSE:1-129]]()

---

**Child Pages:**
*   [Docker and Containerization](#6.1)
*   [License](#6.2)
