# Page: Server Infrastructure

# Server Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [Dockerfile](Dockerfile)
- [deploy/package-lock.json](deploy/package-lock.json)
- [src/main/kotlin/org/openmbee/flexo/mms/Compressor.kt](src/main/kotlin/org/openmbee/flexo/mms/Compressor.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/Content.kt](src/main/kotlin/org/openmbee/flexo/mms/Content.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/routes/Artifacts.kt](src/main/kotlin/org/openmbee/flexo/mms/routes/Artifacts.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/routes/Orgs.kt](src/main/kotlin/org/openmbee/flexo/mms/routes/Orgs.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/Authentication.kt](src/main/kotlin/org/openmbee/flexo/mms/server/Authentication.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/BuildInfo.kt](src/main/kotlin/org/openmbee/flexo/mms/server/BuildInfo.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/GraphStore.kt](src/main/kotlin/org/openmbee/flexo/mms/server/GraphStore.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt](src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/LinkedDataPlatform.kt](src/main/kotlin/org/openmbee/flexo/mms/server/LinkedDataPlatform.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/Protocol.kt](src/main/kotlin/org/openmbee/flexo/mms/server/Protocol.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt](src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/SparqlQuery.kt](src/main/kotlin/org/openmbee/flexo/mms/server/SparqlQuery.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/SparqlUpdate.kt](src/main/kotlin/org/openmbee/flexo/mms/server/SparqlUpdate.kt)
- [src/main/kotlin/org/openmbee/flexo/mms/server/StorageAbstraction.kt](src/main/kotlin/org/openmbee/flexo/mms/server/StorageAbstraction.kt)
- [src/main/resources/logback.xml](src/main/resources/logback.xml)

</details>



The Flexo MMS Layer 1 Service is built on the Ktor asynchronous framework, providing a high-performance HTTP server specialized for RDF data management and SPARQL operations. The infrastructure is designed to handle complex content negotiation, enforce security via JWT authentication, and provide a unified routing abstraction for Linked Data Platform (LDP), Graph Store Protocol (GSP), and Artifact Storage interactions.

## HTTP Configuration and Middleware

The server's HTTP pipeline is configured in `src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt`. It installs several standard Ktor plugins to handle headers, logging, and cross-origin resource sharing.

### Key Plugins
*   **DefaultHeaders**: Injects `X-Engine: Ktor` and a custom `Flexo-MMS-Layer-1` version header into every response [src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt:17-20]().
*   **CORS**: Configured to allow credentials and common RDF/MMS headers such as `Authorization`, `ETag`, `If-Match`, `If-None-Match`, and `SLUG`. It exposes headers like `Accept-Post`, `Accept-Patch`, `Accept-Put`, and `Location` to clients [src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt:32-60]().
*   **StatusPages**: Provides a global exception handling mechanism. It specifically catches `HttpException` and delegates handling to the exception's own `handle(call)` method, while logging generic `Throwable` instances as internal errors [src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt:22-30]().
*   **ForwardedHeaders / XForwardedHeaders**: Enables the service to correctly identify client IPs and protocols when running behind a reverse proxy [src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt:15-16]().

### Request Handling Flow

The following diagram illustrates the flow of an HTTP request through the server infrastructure:

**HTTP Request Pipeline**
```mermaid
graph TD
    subgraph "Ktor Application Pipeline"
        A["Incoming Request"] --> B["DefaultHeaders / ForwardedHeaders"]
        B --> C["CORS Plugin"]
        C --> D["Authentication (JWT)"]
        D --> E["Routing / Matcher"]
        E --> F["Layer1Context Creation"]
        F --> G["beforeEach Callback"]
        G --> H["Handler Execution (CRUD/Query)"]
        H --> I["Content Negotiation"]
        I --> J["StatusPages (on error)"]
        J --> K["Outgoing Response"]
    end

    Sources: ["src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt:14-63", "src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt:86-124", "src/main/kotlin/org/openmbee/flexo/mms/server/Protocol.kt:145-184"]
```

## Content Negotiation and RDF Types

MMS Layer 1 supports a wide array of RDF formats. Content negotiation is handled both for incoming request bodies (deserialization) and outgoing responses (serialization).

### RDF Content Types
The `RdfContentTypes` object defines the supported media types, including Turtle, TriG, N-Triples, N-Quads, RDF/XML, JSON-LD, and SPARQL-specific types like `application/sparql-query` and `application/sparql-update` [src/main/kotlin/org/openmbee/flexo/mms/Content.kt:24-50]().

### Serialization and Deserialization Logic
The `TextConverter` class implements Ktor's `ContentConverter` to handle the conversion of RDF strings.
*   **Deserialization**: Reads the input stream directly into a string using a buffered reader [src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt:57-59]().
*   **Serialization**: Wraps the result string in a `TextContent` object with the negotiated `ContentType` [src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt:61-68]().

The `ApplicationCall.negotiateRdfResponseContentType()` function inspects the `Accept` header items in descending quality order and selects the best format, defaulting to Turtle if no specific format is requested or if wildcards are used [src/main/kotlin/org/openmbee/flexo/mms/Content.kt:99-148]().

## Routing and Protocol Abstractions

To maintain consistency across different resource types, the service uses a hierarchy of route builders that encapsulate protocol-specific logic.

### GenericProtocolRoute
The base class `GenericProtocolRoute` provides the foundation for all protocol-aware routes. It manages:
*   **Allowed Methods**: Tracks which HTTP verbs are active for a specific endpoint and automatically responds to `OPTIONS` requests [src/main/kotlin/org/openmbee/flexo/mms/server/Protocol.kt:92-124]().
*   **Context Lifecycle**: The `eachCall` function initializes the `Layer1Context`, executes the `beforeEach` hooks, validates that the requested method is allowed, and sets protocol-specific headers like `Accept-Post` and `Accept-Patch` [src/main/kotlin/org/openmbee/flexo/mms/server/Protocol.kt:145-184]().

### Protocol Implementations
| Abstraction | Target Protocol | Key Class |
| :--- | :--- | :--- |
| **LDP** | Linked Data Platform | `LinkedDataPlatformRoute` [src/main/kotlin/org/openmbee/flexo/mms/server/LinkedDataPlatform.kt:221]() |
| **GSP** | Graph Store Protocol | `GraphStoreProtocolRoute` [src/main/kotlin/org/openmbee/flexo/mms/server/GraphStore.kt:138]() |
| **Storage** | Artifact Storage | `StorageAbstractionRoute` [src/main/kotlin/org/openmbee/flexo/mms/server/StorageAbstraction.kt:128]() |

### Code Entity Mapping: Routing Infrastructure

This diagram maps the high-level protocol concepts to the specific classes and functions in the codebase.

**Protocol Routing Abstractions**
```mermaid
classDiagram
    class "GenericProtocolRoute<T>" {
        +beforeEach: suspend () -> Unit
        +eachCall(call, creator) Layer1Context
        +head(body)
        +get(body)
        +post(body)
        +put(body)
        +patch(body)
    }
    class "LinkedDataPlatformRoute" {
        +head(body)
        +get(body)
        +post(body)
    }
    class "GraphStoreProtocolRoute" {
        +patch(body)
        +put(body)
    }
    class "StorageAbstractionRoute" {
        +head(body)
        +get(body)
        +post(body)
    }

    "GenericProtocolRoute<T>" <|-- "LinkedDataPlatformRoute"
    "GenericProtocolRoute<T>" <|-- "GraphStoreProtocolRoute"
    "GenericProtocolRoute<T>" <|-- "StorageAbstractionRoute"

    style "GenericProtocolRoute<T>" stroke-dasharray: 5 5

    Sources: ["src/main/kotlin/org/openmbee/flexo/mms/server/Protocol.kt:84-210", "src/main/kotlin/org/openmbee/flexo/mms/server/LinkedDataPlatform.kt:221-230", "src/main/kotlin/org/openmbee/flexo/mms/server/GraphStore.kt:138-172", "src/main/kotlin/org/openmbee/flexo/mms/server/StorageAbstraction.kt:128-172"]
```

## Graph Store Protocol (GSP) Implementation

The `GraphStoreProtocolRoute` handles operations on named graphs according to the W3C Graph Store HTTP Protocol. It uses `GspRequest` to parse the `graph` or `default` query parameters [src/main/kotlin/org/openmbee/flexo/mms/server/GraphStore.kt:27-61]().

A critical feature is the `patch` implementation, which can transform various input types into SPARQL Updates:
*   **SPARQL Update**: If the content type is `application/sparql-update`, the body is passed through directly [src/main/kotlin/org/openmbee/flexo/mms/server/GraphStore.kt:180-182]().
*   **Triples Transformation**: If a triples document (e.g., Turtle) is sent via `PATCH`, the server parses the triples into a `KModel` and wraps them in an `INSERT DATA` block [src/main/kotlin/org/openmbee/flexo/mms/server/GraphStore.kt:193-215]().

## Routing Registration

The final assembly of the server occurs in `Application.configureRouting()`. This function defines the global `authenticate` block and registers all resource-specific CRUD and query routes [src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt:86-124]().

**Route Registration Example (Artifacts)**
```kotlin
// Registration in Routing.kt
authenticate {
    storeArtifacts() // Calls Artifacts.kt registration
}

// Definition in Artifacts.kt
fun Route.storeArtifacts() {
    storageAbstractionResource("/orgs/{orgId}/repos/{repoId}/artifacts") {
        beforeEach = {
            parsePathParams { org(); repo() }
            parseQueryParams { download() }
        }
        get { getArtifactsStore(allArtifacts = true, allData = true) }
        post { createArtifact() }
    }
}
```
Sources: [src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt:91-122](), [src/main/kotlin/org/openmbee/flexo/mms/routes/Artifacts.kt:22-53]()

## Internal HTTP Client

The server maintains an internal `HttpClient` (using the `CIO` engine) for communicating with the underlying SPARQL quad-store. This client is configured with a `TextConverter` for RDF content types (Turtle, TriG, etc.) and includes a configurable request timeout, defaulting to 30 minutes if not specified in the application configuration [src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt:31-48]().

Sources:
*   `src/main/kotlin/org/openmbee/flexo/mms/server/HTTP.kt`
*   `src/main/kotlin/org/openmbee/flexo/mms/server/Routing.kt`
*   `src/main/kotlin/org/openmbee/flexo/mms/server/Protocol.kt`
*   `src/main/kotlin/org/openmbee/flexo/mms/server/GraphStore.kt`
*   `src/main/kotlin/org/openmbee/flexo/mms/server/LinkedDataPlatform.kt`
*   `src/main/kotlin/org/openmbee/flexo/mms/Content.kt`
*   `src/main/kotlin/org/openmbee/flexo/mms/server/StorageAbstraction.kt`
*   `src/main/kotlin/org/openmbee/flexo/mms/routes/Artifacts.kt`
