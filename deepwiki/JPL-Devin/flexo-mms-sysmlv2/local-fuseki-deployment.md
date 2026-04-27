# Page: Local Fuseki Deployment

# Local Fuseki Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker-compose/docker-compose.yml](docker-compose/docker-compose.yml)
- [docker-compose/env/flexo-mms-jwt.env](docker-compose/env/flexo-mms-jwt.env)
- [docker-compose/env/flexo-mms-layer1-openmbee.env](docker-compose/env/flexo-mms-layer1-openmbee.env)
- [docker-compose/env/flexo-mms-quad-store.env](docker-compose/env/flexo-mms-quad-store.env)
- [docker-compose/mount/cluster.trig](docker-compose/mount/cluster.trig)
- [docker-compose/mount/openmbee.sparql](docker-compose/mount/openmbee.sparql)
- [src/main/kotlin/org/openmbee/flexo/sysmlv2/apis/RelationshipApi.kt](src/main/kotlin/org/openmbee/flexo/sysmlv2/apis/RelationshipApi.kt)

</details>



This page documents the local deployment configuration for the Flexo MMS SysML v2 service using Apache Jena Fuseki as the underlying quad store. This setup is designed for local development, testing, and demonstration purposes, providing a self-contained stack of the SysML v2 API, the Flexo MMS Layer 1 service, and a SPARQL-compliant database.

## Service Architecture

The local deployment utilizes a three-tier containerized architecture defined in the primary `docker-compose.yml` file. Data flows from the SysML v2 service through the Layer 1 abstraction to the Fuseki quad store.

### Deployment Component Diagram
The following diagram illustrates the relationship between the Docker services and the configuration files that govern them.

"Local Deployment Component Map"
```mermaid
graph TD
    subgraph "Docker Compose Stack"
        [sysmlv2-service] --> [layer1-service]
        [layer1-service] --> [quad-store-server]
    end

    subgraph "Configuration Entities"
        [flexo-sysmlv2.env] -.-> [sysmlv2-service]
        [flexo-mms-layer1.env] -.-> [layer1-service]
        [flexo-mms-jwt.env] -.-> [layer1-service]
        [flexo-mms-quad-store.env] -.-> [quad-store-server]
        [cluster.trig] -.-> [quad-store-server]
    end

    style [sysmlv2-service] stroke-width:2px
    style [layer1-service] stroke-width:2px
    style [quad-store-server] stroke-width:2px
```
Sources: [docker-compose/docker-compose.yml:1-38](), [docker-compose/env/flexo-mms-quad-store.env:1-2]()

## Service Definitions

The deployment is orchestrated via `docker-compose/docker-compose.yml`.

| Service Name | Image | Port Mapping | Description |
|:---|:---|:---|:---|
| `quad-store-server` | `atomgraph/fuseki:4.6` | `3030:3030` | The RDF quad store (Apache Jena Fuseki) that persists all MMS and SysML v2 data. |
| `layer1-service` | `openmbee/flexo-mms-layer1-service:v0.2.2` | `8080:8080` | The Flexo MMS Layer 1 service providing the foundational RDF management and access control. |
| `sysmlv2-service` | `openmbee/flexo-sysmlv2:v0.1.1` | `8083:8080` | The SysML v2 API implementation that maps SysML concepts to MMS structures. |

Sources: [docker-compose/docker-compose.yml:3-37]()

## Data Flow and Bootstrapping

The startup sequence is critical for ensuring the quad store is correctly initialized with the necessary MMS ontology and cluster-level metadata.

### Initialization Sequence
1.  **Volume Mount**: The `quad-store-server` mounts the `./mount` directory to `/tmp/mount` inside the container [docker-compose/docker-compose.yml:11-12]().
2.  **Bootstrap Data**: The Fuseki server is started with the `--file=/tmp/mount/cluster.trig --update /ds` flag [docker-compose/docker-compose.yml:10-10](). This loads the TriG file containing the initial MMS graph structure into the `/ds` dataset.
3.  **Service Dependencies**: `layer1-service` waits for `quad-store-server` [docker-compose/docker-compose.yml:23-24](), and `sysmlv2-service` waits for `layer1-service` [docker-compose/docker-compose.yml:34-35]().

### Code Entity to Infrastructure Mapping
This diagram bridges the SysML v2 service logic to the infrastructure components defined in the compose file, highlighting how API calls translate to backend requests.

"Code-to-Infrastructure Mapping"
```mermaid
graph LR
    subgraph "Kotlin Application Space"
        [AppMain.kt] --> [FlexoConfig.kt]
        [RelationshipApi.kt] -- "flexoRequestPost" --> [Flexo.kt]
    end

    subgraph "Infrastructure Space"
        [sysmlv2-service] -- "HTTP" --> [layer1-service]
        [layer1-service] -- "SPARQL Update/Query" --> [quad-store-server]
        [quad-store-server] -- "Bootstrap" --> [cluster.trig]
    end

    [Flexo.kt] -. "FLEXO_HOST" .-> [layer1-service]
```
Sources: [docker-compose/docker-compose.yml:16-37](), [src/main/kotlin/org/openmbee/flexo/sysmlv2/apis/RelationshipApi.kt:46-47](), [docker-compose/mount/cluster.trig:1-11]()

## Bootstrap Data (`cluster.trig`)

The `cluster.trig` file is essential for a "cold start" of the system. It defines the root MMS Cluster, administrative users, and the core MMS schema using the `http://layer1-service/` base URI.

### Key Graphs in `cluster.trig`
*   **`m-graph:AccessControl.Agents`**: Defines the `root` and `admin` users, as well as the `SuperAdmins` group [docker-compose/mount/cluster.trig:13-36]().
*   **`m-graph:AccessControl.Policies`**: Establishes the `DefaultSuperAdmins` policy, granting administrative roles (e.g., `mms-object:Role.AdminCluster`, `mms-object:Role.AdminOrg`, `mms-object:Role.AdminRepo`) to the root user and admin group [docker-compose/mount/cluster.trig:39-44]().
*   **`m-graph:Cluster`**: Defines the root cluster URI `http://layer1-service/` and the access control scope [docker-compose/mount/cluster.trig:47-51]().
*   **`m-graph:Schema`**: Contains the RDFS class definitions for MMS concepts like `mms:Project`, `mms:Repo`, `mms:Commit`, and `mms:Branch` [docker-compose/mount/cluster.trig:54-132]().

Sources: [docker-compose/mount/cluster.trig:13-132]()

## Environment Configuration

The local deployment relies on several `.env` files located in the `docker-compose/env/` directory.

### Quad Store Configuration (`flexo-mms-quad-store.env`)
This file sets the JVM heap size for the Fuseki server to ensure sufficient memory for processing large RDF graphs.
*   `JAVA_OPTIONS`: Set to `-Xmx8192m -Xms8192m` [docker-compose/env/flexo-mms-quad-store.env:1-1]().

### Layer 1 Configuration
The Layer 1 service is configured via several files:
1.  **`flexo-mms-jwt.env`**: Contains JWT settings including `JWT_SECRET`, `JWT_DOMAIN`, and `JWT_AUDIENCE` for authentication [docker-compose/env/flexo-mms-jwt.env:1-4]().
2.  **`flexo-mms-layer1.env`**: (Referenced in [docker-compose/docker-compose.yml:22]()) Typically configures the service to point to the `quad-store-server`.
3.  **`flexo-mms-layer1-openmbee.env`**: An alternative configuration pointing to an external Neptune instance with specific SPARQL and GSP endpoints [docker-compose/env/flexo-mms-layer1-openmbee.env:1-4]().

### SysML v2 Service Configuration (`flexo-sysmlv2.env`)
Configures the SysML v2 service to communicate with the Layer 1 service.
*   The service container maps host port `8083` to container port `8080` [docker-compose/docker-compose.yml:37-37]().

Sources: [docker-compose/docker-compose.yml:8-37](), [docker-compose/env/flexo-mms-quad-store.env:1-1](), [docker-compose/env/flexo-mms-jwt.env:1-4]()
