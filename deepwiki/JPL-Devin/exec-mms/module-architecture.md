# Page: Module Architecture

# Module Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.circleci/config.yml](.circleci/config.yml)
- [Dockerfile](Dockerfile)
- [authenticator/authenticator.gradle](authenticator/authenticator.gradle)
- [build.gradle](build.gradle)
- [core/core.gradle](core/core.gradle)
- [data/data.gradle](data/data.gradle)
- [elastic/elastic.gradle](elastic/elastic.gradle)
- [example/example.gradle](example/example.gradle)
- [example/getAtCommits.postman_collection.json](example/getAtCommits.postman_collection.json)
- [gradle.properties](gradle.properties)
- [rdb/rdb.gradle](rdb/rdb.gradle)
- [sonar-project.properties](sonar-project.properties)
- [storage/src/main/resources/application.properties.example](storage/src/main/resources/application.properties.example)
- [storage/storage.gradle](storage/storage.gradle)
- [twc/twc.gradle](twc/twc.gradle)

</details>



The Model Management System (MMS) is built using a highly decoupled, Gradle multi-module architecture. This design allows for pluggable persistence layers, flexible authentication providers, and domain-specific schema extensions (such as Cameo or Jupyter) to be toggled on or off depending on the requirements of the deployment.

## Dependency Hierarchy and Data Flow

The architecture follows a layered approach where the `json` and `core` modules define the contracts and interfaces, while implementation modules (like `rdb`, `elastic`, and `federatedpersistence`) provide the logic for data storage and retrieval.

### Core Dependency Tree
The following diagram illustrates how the primary modules depend on one another to form the system's backbone.

**MMS Module Dependency Map**
```mermaid
graph TD
    ["example"] --> [":authenticator"]
    ["example"] --> [":federatedpersistence"]
    ["example"] --> [":cameo"]
    ["example"] --> [":jupyter"]
    
    [":federatedpersistence"] --> [":rdb"]
    [":federatedpersistence"] --> [":elastic"]
    
    [":rdb"] --> [":data"]
    [":elastic"] --> [":data"]
    [":elastic"] --> [":search"]
    
    [":data"] --> [":core"]
    [":data"] --> [":json"]
    
    [":core"] --> [":json"]
    [":authenticator"] --> [":core"]
    
    subgraph Domain_Logic ["Domain Logic & Contracts"]
        [":core"]
        [":json"]
    end

    subgraph Persistence_Layer ["Persistence Layer"]
        [":rdb"]
        [":elastic"]
        [":federatedpersistence"]
    end
```
**Sources:** [example/example.gradle:16-31](), [data/data.gradle:1-3](), [core/core.gradle:3-3](), [elastic/elastic.gradle:1-4]()

---

## Primary Modules

### 1. `json` and `core`
These modules contain the base domain objects and service interfaces. 
- **`json`**: Defines the HashMap-based DTOs (Data Transfer Objects) used for REST API requests and responses.
- **`core`**: Contains the service interfaces (e.g., `NodeService`, `BranchService`) and common exceptions. It depends on `json` to define the input/output of these services.

**Sources:** [core/core.gradle:3-3](), [data/data.gradle:2-3]()

### 2. `data`
The `data` module bridges the domain model and persistence. It contains the JPA entity definitions for both global metadata (Users, Orgs) and scoped project data (Nodes, Commits). It serves as a shared dependency for both relational and search-based persistence modules.

**Sources:** [data/data.gradle:1-13]()

### 3. `rdb` and `elastic`
These modules provide specific database implementations:
- **`rdb`**: Implements relational persistence using Spring Data JPA and Hibernate. It handles multi-tenant schema routing and metadata storage.
- **`elastic`**: Implements search and large-scale element indexing using the `RestHighLevelClient`. It provides the `NodeElasticDAO` for fast retrieval of element JSON content.

**Sources:** [elastic/elastic.gradle:1-6](), [gradle.properties:10-10]()

### 4. `federatedpersistence`
This is a coordinator module that implements the "Federated Persistence" pattern. It ensures that data is synchronized across both the Relational Database (RDB) and Elasticsearch. For example, when a commit is made, `federatedpersistence` manages the transaction to write metadata to RDB and the full element JSON to Elastic.

**Sources:** [example/example.gradle:31-31]()

---

## Extension and Plugin Modules

MMS utilizes optional modules to provide specialized functionality. These are included in the `example` application build to provide a full-featured reference implementation.

| Module | Purpose | Key Dependencies |
|:---|:---|:---|
| `authenticator` | Core JWT token generation and filter logic. | `jjwt`, `spring-security` |
| `localuser` | Management of users stored directly in the MMS database. | `authenticator` |
| `ldap` | Integration with LDAP/Active Directory for authentication. | `spring-security-ldap` |
| `search` | Defines the search request structures and service interfaces. | `core` |
| `artifacts` | Handles binary file attachments (blobs) for elements. | `core` |
| `storage` | S3/MinIO implementation for the `artifacts` module. | `aws-java-sdk-s3` |
| `webhooks` | Outbound HTTP callback system for commit events. | `core` |
| `cameo` | Schema support for MagicDraw/Cameo systems modeling. | `core`, `json` |
| `jupyter` | Integration for storing and managing Jupyter Notebooks. | `core`, `elastic` |

**Sources:** [example/example.gradle:16-31](), [storage/storage.gradle:1-5](), [authenticator/authenticator.gradle:1-10](), [elastic/elastic.gradle:4-4]()

---

## Application Assembly

The `example` module acts as the "Aggregator" or "Main" application. It compiles all sub-modules into a single executable Spring Boot JAR.

### Code-to-System Mapping
This diagram shows how the Gradle project structure maps to the runtime Spring Boot application and its infrastructure.

**MMS Assembly & Infrastructure Mapping**
```mermaid
graph LR
    subgraph "Gradle Project Structure"
        [":example"] -- "builds" --> ["bootJar"]
        [":rdb"] -- "configures" --> ["DataSource"]
        [":elastic"] -- "connects" --> ["RestHighLevelClient"]
        [":storage"] -- "uses" --> ["AmazonS3Client"]
    end

    subgraph "Runtime Environment (Docker)"
        ["bootJar"] -- "runs in" --> ["mms-container"]
        ["DataSource"] -- "talks to" --> ["PostgreSQL"]
        ["RestHighLevelClient"] -- "talks to" --> ["Elasticsearch"]
        ["AmazonS3Client"] -- "talks to" --> ["MinIO"]
    end

    subgraph "External Clients"
        ["Newman/Postman"] -- "REST API" --> ["mms-container"]
    end
```
**Sources:** [Dockerfile:1-9](), [.circleci/config.yml:23-31](), [example/example.gradle:45-53](), [storage/storage.gradle:4-4]()

### Build and Deployment Flow
1. **Compilation**: Gradle compiles all modules. The `example` module's `bootJar` task packages all dependencies into a single archive.
2. **Containerization**: The `Dockerfile` uses `openjdk:17.0.2-slim` as a base, copies the `example` JAR as `app.jar`, and sets the entry point.
3. **CI/CD Integration**: The CircleCI pipeline executes the `build_and_test` job, which spins up the infrastructure via `docker-compose` and runs Newman tests against the assembled application.
4. **Publication**: Artifacts are signed and published to Sonatype/OSSRH using the `maven-publish` and `signing` plugins.

**Sources:** [Dockerfile:1-9](), [build.gradle:98-164](), [.circleci/config.yml:14-53](), [example/example.gradle:51-53]()
