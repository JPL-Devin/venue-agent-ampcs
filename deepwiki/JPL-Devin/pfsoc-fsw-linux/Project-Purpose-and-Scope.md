# Project Purpose and Scope

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitmodules](.gitmodules)
- [README.md](README.md)

</details>



The `pfsoc-fsw-linux` project is a specialized deployment of the **F´ (F Prime)** flight software framework designed to run within the Linux userspace on the **Microchip PolarFire SoC (MPFS)**. The primary objective of this repository is to validate the portability of F´ components and its Operating System Abstraction Layer (OSAL) when targeting RISC-V application cores (U54 cores) running a Linux kernel [README.md:1-3]().

## Core Objectives

The project serves as a technical bridge between the F´ framework and the RISC-V hardware ecosystem. It focuses on the following goals:

1.  **Framework Validation**: Ensuring the F´ core framework (including `Fw`, `Svc`, and `Os` namespaces) correctly compiles and executes on a 64-bit RISC-V architecture.
2.  **Linux Userspace Integration**: Leveraging the standard Linux `pthreads`, `sockets`, and `sysfs` interfaces to provide the underlying services for F´ active components and communication drivers.
3.  **Deployment Prototyping**: Establishing a reference topology that includes standard flight software services such as command dispatch, telemetry management, and health monitoring, tailored for the MPFS environment [README.md:12-15]().

### Data Flow and System Context

The following diagram illustrates how the `pfsoc-fsw-linux` deployment sits between the Ground Data System (GDS) and the PolarFire SoC hardware.

**Figure 1: System Context and Data Flow**
```mermaid
graph TD
    subgraph "GroundSegment"
        ["GDS: F Prime Ground Data System"]
    end

    subgraph "PolarFireSoC_MPFS_LinuxUserspace"
        subgraph "pfsoc-fsw-linux_Binary"
            ["comDriver: Drv::TcpClient"]
            ["cmdDisp: Svc::CommandDispatcher"]
            ["tlmChan: Svc::TlmChan"]
            ["eventLogger: Svc::ActiveLogger"]
            ["Top: PfSocLinuxTopology"]
        end
        
        ["Linux_Kernel_RISC-V"]
    end

    ["GDS: F Prime Ground Data System"] <== "TCP/UDP (Command/Telemetry)" ==> ["comDriver: Drv::TcpClient"]
    ["comDriver: Drv::TcpClient"] <== "Fw::Com Ports" ==> ["Top: PfSocLinuxTopology"]
    ["Top: PfSocLinuxTopology"] ==> ["cmdDisp: Svc::CommandDispatcher"]
    ["Top: PfSocLinuxTopology"] ==> ["tlmChan: Svc::TlmChan"]
    ["Top: PfSocLinuxTopology"] ==> ["eventLogger: Svc::ActiveLogger"]
    ["Linux_Kernel_RISC-V"] <== "Syscalls / pthreads" ==> ["Top: PfSocLinuxTopology"]
```
**Sources:** [README.md:1-3](), [PfSocLinux/Main.cpp:1-40]()

---

## Technical Scope

### Target Hardware: RISC-V U54 Cores
The scope is limited to the **Microprocessor Subsystem (MSS)** of the PolarFire SoC. While the MPFS contains an FPGA fabric and a monitor core (E51), this project specifically targets the four **SiFive U54 RISC-V cores**. The software runs as a standard Linux process, utilizing the `Os` abstraction layer provided by the F´ framework to interface with the hardware via the Linux kernel [README.md:1-3]().

### Software Stack Architecture
The deployment utilizes a layered architecture to separate flight logic from hardware-specific implementation. It incorporates the core F´ framework and a specific library for PolarFire SoC Linux support as git submodules [.gitmodules:1-8]().

| Layer | Component/Namespace | Responsibility |
| :--- | :--- | :--- |
| **Application** | `PfSocLinux` | High-level flight logic, command handling, and telemetry collection [PfSocLinux/Top/:1-10](). |
| **Framework** | `Fw` | Port-based communication, serialization, and component base classes [lib/fprime:1-3](). |
| **OSAL** | `Os` | Abstraction of Linux-specific `pthreads`, `File`, and `Mutex` implementations for RISC-V. |
| **Driver** | `Drv::TcpClient` | Bridge between F´ `Fw::Com` packets and Linux TCP/IP stacks. |

**Figure 2: Component-to-Code Mapping**
```mermaid
classDiagram
    class "Fw::ObjBase" {
        <<Framework>>
        +getName()
    }
    class "Os::Task" {
        <<OSAL>>
        +start(name, routine)
    }
    class "Drv::TcpClient" {
        <<Driver>>
        +configure(hostname, port)
    }
    class "PfSocLinuxTopology" {
        <<Deployment>>
        +setup()
        +teardown()
    }

    "PfSocLinuxTopology" --> "Fw::ObjBase" : "Instantiates"
    "PfSocLinuxTopology" --> "Os::Task" : "Spawns Threads"
    "Drv::TcpClient" ..> "Os::Task" : "Uses for I/O loop"
    "Fw::ObjBase" <|-- "Drv::TcpClient" : "Inherits"
```
**Sources:** [README.md:1-17](), [.gitmodules:1-8](), [PfSocLinux/Main.cpp:1-40]()

---

## Validation Goals

To ensure the success of the `pfsoc-fsw-linux` deployment, the project scope includes the validation of several key F´ features on the MPFS platform:

*   **Multi-threading**: Verification that `Os::Task` correctly maps to Linux `pthreads` on RISC-V, ensuring that active components execute in parallel without race conditions in the port-passing logic.
*   **Endianness and Alignment**: Validating that the F´ serialization engine correctly handles 64-bit RISC-V data alignment and little-endian byte ordering during telemetry and command processing.
*   **Cross-Compilation Integrity**: Ensuring the CMake-based build system correctly integrates the `riscv64-unknown-linux-gnu` toolchain to produce optimized binaries for the U54 cores [settings.ini:1-16]().

**Sources:** [README.md:1-3](), [settings.ini:1-16]()
