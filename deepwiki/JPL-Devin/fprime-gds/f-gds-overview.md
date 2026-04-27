# Page: F´ GDS Overview

# F´ GDS Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ISSUE_TEMPLATE/config.yml](.github/ISSUE_TEMPLATE/config.yml)
- [.github/actions/spelling/expect.txt](.github/actions/spelling/expect.txt)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [LICENSE.txt](LICENSE.txt)
- [NOTICE.txt](NOTICE.txt)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [src/fprime_gds/version.py](src/fprime_gds/version.py)

</details>



The F´ Ground Data System (GDS) is a collection of Python-based tools and classes that provide a graphical and programmatic interface for F´ flight software deployments [README.md:8-9](). It enables operators to monitor telemetry (channels), receive event reports, and dispatch commands to a running spacecraft or embedded system [README.md:9]().

The system is designed around a publisher/subscriber architecture to ensure it is adaptable and easily expandable [README.md:14-15]().

### Core Purpose and Capabilities
*   **Telemetry Monitoring:** Decodes and displays real-time channel data and packetized telemetry [README.md:19-20]().
*   **Event Logging:** Captures and formats event messages from the flight software [README.md:19]().
*   **Commanding:** Encodes user inputs into binary formats for uplink to the deployment [README.md:23-26]().
*   **File Handling:** Supports stop-and-wait protocols for uploading and downloading files [Table of Contents Section 4.3]().
*   **Automated Testing:** Provides a robust Integration Test API for scripted interactions with flight software [README.md:45-46]().

### High-Level Architecture
The GDS acts as a bridge between the binary world of flight software and the human-readable world of the operator. Data enters the system via a transport layer (typically TCP), is routed by a `Distributor`, and is transformed into data objects by specialized `Decoders` [README.md:17-22]().

#### Data Flow and Code Entities
The following diagram illustrates how high-level system concepts map to specific classes and entities within the codebase.

**GDS Entity Mapping**
```mermaid
graph TD
    subgraph "Transport Layer"
        [TCP_Client] --> |"Raw Binary"| [Distributor]
    end

    subgraph "Processing Pipeline"
        [Distributor] --> |"Message Data"| [EventDecoder]
        [Distributor] --> |"Message Data"| [ChDecoder]
        [Distributor] --> |"Message Data"| [PktDecoder]
        
        [EventDecoder] --> |"EventData"| [RamHistory]
        [ChDecoder] --> |"ChData"| [RamHistory]
    end

    subgraph "User Interface"
        [RamHistory] --> [Flask_REST_API]
        [Flask_REST_API] --> [Vue_Frontend]
    end

    subgraph "Command Uplink"
        [Vue_Frontend] --> |"REST Request"| [Flask_REST_API]
        [Flask_REST_API] --> [CmdEncoder]
        [CmdEncoder] --> |"Encoded Binary"| [TCP_Client]
    end

    style [TCP_Client] stroke-dasharray: 5 5
    style [Distributor] stroke-dasharray: 5 5
```
Sources: [README.md:17-29](), [README.md:61-84](), [README.md:115-129]()

### Key Components

| Component | Code Entity / Path | Description |
| :--- | :--- | :--- |
| **Pipeline** | `StandardPipeline` | A helper layer that instantiates the GDS stack and connects to the deployment [README.md:39-43](). |
| **Distributor** | `Distributor` | Parses packet headers (length/descriptor) and routes payloads [README.md:66-71](). |
| **Decoders** | `Decoder` (Base) | Subclasses that turn binary messages into `DataObjects` [README.md:115-124](). |
| **Encoders** | `Encoder` (Base) | Subclasses that serialize `DataObjects` into binary for uplink [README.md:126-133](). |
| **Histories** | `RamHistory` | In-memory storage for received telemetry and events [README.md:41-42](). |
| **Loaders** | `Loader` (Base) | Constructs dictionaries (templates) from XML or JSON files [README.md:106-113](). |

Sources: [README.md:39-134]()

### System Entry Points
The GDS provides several command-line interfaces (CLIs) for different operational needs, defined as entry points in the package configuration [pyproject.toml:62-69]().

**CLI to Code Entry Point Mapping**
```mermaid
graph LR
    [fprime-gds] --> |"starts"| [run_deployment.py]
    [fprime-cli] --> |"starts"| [fprime_cli.py]
    [fprime-seqgen] --> |"starts"| [seqgen.py]
    [fprime-dp] --> |"starts"| [data_products.py]

    subgraph "Executable Scripts"
        [run_deployment.py]
        [fprime_cli.py]
        [seqgen.py]
        [data_products.py]
    end
```
Sources: [pyproject.toml:62-69]()

### Detailed Coverage
For more in-depth information on specific areas of the F´ GDS, please refer to the following child pages:

*   **[Getting Started & Installation](#1.1):** Instructions on installing the `fprime-gds` package and launching the stack.
*   **[System Architecture & Data Flow](#1.2):** Deep dive into the publisher/subscriber registration pattern and the end-to-end binary data lifecycle.

---
Sources: [README.md:1-140](), [pyproject.toml:1-98](), [src/fprime_gds/version.py:1-10]()
