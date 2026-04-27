# Page: Deployment and Infrastructure

# Deployment and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker-compose/docker-compose-graphdb.yml](docker-compose/docker-compose-graphdb.yml)
- [docker-compose/docker-compose-openmbee.yml](docker-compose/docker-compose-openmbee.yml)
- [docker-compose/docker-compose.yml](docker-compose/docker-compose.yml)

</details>



The `flexo-mms-sysmlv2` service is designed for containerized deployment within the OpenMBEE Flexo ecosystem. It functions as a specialized SysML v2 API layer that communicates with a Flexo MMS Layer 1 service, which in turn interacts with an underlying RDF quad store.

The deployment architecture is managed through Docker Compose, providing several configurations ranging from a lightweight local development setup to more complex environments involving authentication services and enterprise-grade triplestores.

### Deployment Stack Overview

The standard deployment consists of three primary tiers:
1.  **SysML v2 Service**: The `flexo-sysmlv2` container running the Ktor application [docker-compose/docker-compose.yml:28-31]().
2.  **Layer 1 Service**: The `flexo-mms-layer1-service` which provides the core Model Management System logic [docker-compose/docker-compose.yml:16-19]().
3.  **Quad Store**: An RDF triplestore (e.g., Apache Jena Fuseki or Ontotext GraphDB) that persists the SysML v2 model data as RDF quads [docker-compose/docker-compose.yml:4-7]().

### Container Relationship Diagram

The following diagram illustrates how the different containers in the stack relate to one another and the environment files that configure them.

**Service Dependency and Configuration Map**
```mermaid
graph TD
    subgraph "Application_Layer"
        ["sysmlv2-service"]
    end

    subgraph "MMS_Core_Layer"
        ["layer1-service"]
    end

    subgraph "Persistence_Layer"
        ["quad-store-server"]
    end

    ["sysmlv2-service"] -- "HTTP_API_Calls" --> ["layer1-service"]
    ["layer1-service"] -- "SPARQL/Update" --> ["quad-store-server"]

    ["flexo-sysmlv2.env"] -.-> ["sysmlv2-service"]
    ["flexo-mms-layer1.env"] -.-> ["layer1-service"]
    ["flexo-mms-jwt.env"] -.-> ["layer1-service"]
    ["flexo-mms-quad-store.env"] -.-> ["quad-store-server"]
```
Sources: [docker-compose/docker-compose.yml:1-38]()

---

### Local Fuseki Deployment
The default deployment uses **Apache Jena Fuseki** (via the `atomgraph/fuseki:4.6` image) as the quad store [docker-compose/docker-compose.yml:4-5](). This setup is intended for local development and testing. It includes a bootstrap mechanism where a `cluster.trig` file is mounted to initialize the quad store with necessary metadata and enables updates on the `/ds` dataset [docker-compose/docker-compose.yml:10-12]().

For details on port mappings and volume mounts for this configuration, see [Local Fuseki Deployment](#5.1).

Sources: [docker-compose/docker-compose.yml:4-15]()

### OpenMBEE Cloud and GraphDB Deployments
Beyond the basic local setup, the repository provides alternative configurations for different infrastructure requirements:

*   **OpenMBEE Cloud**: A variant defined in `docker-compose-openmbee.yml` that optimizes the stack for external Layer 1 environments, using specific environment overrides like `flexo-mms-layer1-openmbee.env` [docker-compose/docker-compose-openmbee.yml:1-13]().
*   **GraphDB Variant**: A robust deployment using **Ontotext GraphDB** (`ontotext/graphdb:10.3.0`) [docker-compose/docker-compose-graphdb.yml:21-22](). This configuration includes additional infrastructure components such as `openldap-server` for identity management [docker-compose/docker-compose-graphdb.yml:5-8](), `minio-server` for S3-compatible storage [docker-compose/docker-compose-graphdb.yml:31-34](), and a dedicated `auth-service` [docker-compose/docker-compose-graphdb.yml:42-45]().

For details on these variants and their specific environment requirements, see [OpenMBEE Cloud and GraphDB Deployments](#5.2).

Sources: [docker-compose/docker-compose-openmbee.yml:1-30](), [docker-compose/docker-compose-graphdb.yml:1-85]()

### Environment Configuration Reference
The behavior of the entire stack is governed by a collection of `.env` files located in the `docker-compose/env/` directory. These files define:
*   **Service Locations**: Configurations that allow the SysML v2 service to locate and communicate with the Layer 1 service [docker-compose/docker-compose.yml:32-33]().
*   **Authentication**: JWT secrets (`flexo-mms-jwt.env`) and credential management for secure communication between services [docker-compose/docker-compose.yml:20-21]().
*   **Storage Backend**: Specific triplestore settings, such as Fuseki update commands or GraphDB cache settings [docker-compose/docker-compose.yml:10](), [docker-compose/docker-compose-graphdb.yml:27]().

For a comprehensive list of all variables and their roles, see [Environment Configuration Reference](#5.3).

Sources: [docker-compose/docker-compose.yml:21-22](), [docker-compose/docker-compose.yml:33]()

---

### Deployment Architecture Code Map

This diagram bridges the conceptual deployment services to the specific images and environment files defined in the codebase.

**Code Entity Deployment Map**
```mermaid
graph LR
    subgraph "Docker_Images"
        ["openmbee/flexo-sysmlv2:v0.1.1"]
        ["openmbee/flexo-mms-layer1-service:v0.2.2"]
        ["atomgraph/fuseki:4.6"]
        ["ontotext/graphdb:10.3.0"]
    end

    subgraph "Env_Files"
        ["flexo-sysmlv2.env"]
        ["flexo-mms-layer1.env"]
        ["flexo-mms-jwt.env"]
        ["flexo-mms-quad-store.env"]
    end

    ["openmbee/flexo-sysmlv2:v0.1.1"] -- "depends_on" --> ["openmbee/flexo-mms-layer1-service:v0.2.2"]
    ["openmbee/flexo-mms-layer1-service:v0.2.2"] -- "depends_on" --> ["atomgraph/fuseki:4.6"]
    
    ["flexo-sysmlv2.env"] -- "env_file" --> ["openmbee/flexo-sysmlv2:v0.1.1"]
    ["flexo-mms-layer1.env"] -- "env_file" --> ["openmbee/flexo-mms-layer1-service:v0.2.2"]
    ["flexo-mms-jwt.env"] -- "env_file" --> ["openmbee/flexo-mms-layer1-service:v0.2.2"]
    ["flexo-mms-quad-store.env"] -- "env_file" --> ["atomgraph/fuseki:4.6"]
```
Sources: [docker-compose/docker-compose.yml:1-38](), [docker-compose/docker-compose-graphdb.yml:21-26]()
