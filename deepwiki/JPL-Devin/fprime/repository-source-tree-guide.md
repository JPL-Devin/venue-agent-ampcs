# Page: Repository Source Tree Guide

# Repository Source Tree Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/spelling/README.md](.github/actions/spelling/README.md)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [CMakeLists.txt](CMakeLists.txt)
- [Drv/ByteStreamDriverModel/ByteStreamDriverModel.fpp](Drv/ByteStreamDriverModel/ByteStreamDriverModel.fpp)
- [Fw/Types/CAssert.h](Fw/Types/CAssert.h)
- [Fw/Types/Types.fpp](Fw/Types/Types.fpp)
- [Fw/Types/test/ut/CAssertTest.cpp](Fw/Types/test/ut/CAssertTest.cpp)
- [Os/docs/sdd.md](Os/docs/sdd.md)
- [README.md](README.md)
- [Ref/CMakeLists.txt](Ref/CMakeLists.txt)
- [Ref/README.md](Ref/README.md)
- [Ref/docs/TestCases.txt](Ref/docs/TestCases.txt)
- [Ref/docs/sdd.md](Ref/docs/sdd.md)
- [Svc/Ccsds/TmFramer/TmFramer.hpp](Svc/Ccsds/TmFramer/TmFramer.hpp)
- [cmake/test/data/test-fprime-library/TestLibrary/TestComponent/TestComponent.cpp](cmake/test/data/test-fprime-library/TestLibrary/TestComponent/TestComponent.cpp)
- [cmake/test/data/test-fprime-library/TestLibrary/TestComponent/TestComponent.hpp](cmake/test/data/test-fprime-library/TestLibrary/TestComponent/TestComponent.hpp)
- [cmake/test/data/test-fprime-library2/TestLibrary2/TestComponent/TestComponent.cpp](cmake/test/data/test-fprime-library2/TestLibrary2/TestComponent/TestComponent.cpp)
- [cmake/test/data/test-fprime-library2/TestLibrary2/TestComponent/TestComponent.hpp](cmake/test/data/test-fprime-library2/TestLibrary2/TestComponent/TestComponent.hpp)
- [docs/INSTALL.md](docs/INSTALL.md)
- [docs/how-to/develop-fprime-libraries.md](docs/how-to/develop-fprime-libraries.md)
- [docs/how-to/implement-osal.md](docs/how-to/implement-osal.md)
- [docs/how-to/porting-guide.md](docs/how-to/porting-guide.md)
- [docs/img/fprime-logo.png](docs/img/fprime-logo.png)
- [docs/img/fprime-logo.svg](docs/img/fprime-logo.svg)
- [docs/index.md](docs/index.md)
- [docs/reference/index.md](docs/reference/index.md)
- [docs/user-manual/framework/assert.md](docs/user-manual/framework/assert.md)
- [docs/user-manual/gds/gds-cli.md](docs/user-manual/gds/gds-cli.md)
- [docs/user-manual/gds/seqgen.md](docs/user-manual/gds/seqgen.md)
- [docs/user-manual/overview/development-practice.md](docs/user-manual/overview/development-practice.md)
- [docs/user-manual/overview/source-tree.md](docs/user-manual/overview/source-tree.md)

</details>



This page provides a technical tour of the F´ repository structure. The F´ codebase is organized into functional layers that separate the core framework, reusable services, hardware drivers, and deployment-specific logic. This modularity allows the core framework to remain platform-agnostic while providing clear locations for project-specific adaptations.

## Top-Level Directory Overview

The repository is structured to support "out-of-source" builds, where build artifacts are kept separate from the source code. The top-level `CMakeLists.txt` sets the `FPRIME_FRAMEWORK_PATH` and `FPRIME_PROJECT_ROOT` to the current directory [CMakeLists.txt:8-9]().

| Directory | Description |
|---|---|
| `Fw` | **Framework**: Foundational C++ classes, serialization, and component base classes. |
| `Svc` | **Services**: Reusable flight software components (Commanding, Telemetry, File Management). |
| `Drv` | **Drivers**: Hardware abstraction components following the `ByteStreamDriverModel`. |
| `Os` | **OSAL**: Operating System Abstraction Layer for tasks, queues, and files. |
| `Ref` | **Reference App**: A complete example deployment for Linux/macOS. |
| `RPI` | **Raspberry Pi**: Demo deployment and drivers for ARM-based Linux hardware. |
| `Gds` | **Ground System**: The Python-based ground software and web interface. |
| `cmake` | **Build System**: The CMake infrastructure and autocoding logic. |
| `config` | **Project Config**: Global configuration headers and FPP settings. |
| `Utils` | **Utilities**: Common algorithms (CRC, Hash) and data structures. |

## Core Framework (`Fw`)

The `Fw` directory contains the heart of the F´ architecture. It defines the base classes that all components inherit from and the serialization protocols used for inter-component communication.

*   **Fw/Types**: Contains `BasicTypes.h`, `StringType`, and the `PolyType` [Fw/Types/Types.fpp:4-7](). It also defines the standard return statuses for serialization (`SerialStatus`) and deserialization (`DeserialStatus`) [Fw/Types/Types.fpp:10-23](). This directory also contains the framework's assertion logic, including `FW_ASSERT` for C++ and `FW_CASSERT` for C code [Fw/Types/CAssert.h:26-32]().
*   **Fw/Comp**: Implementation of `PassiveComponentBase`, `QueuedComponentBase`, and `ActiveComponentBase`.
*   **Fw/Port**: The base classes for synchronous and asynchronous port communication.
*   **Fw/FilePacket**: Definitions for file transfer packets (Start, Data, End) used by file services.

### Framework Data Flow
The following diagram illustrates how core framework entities relate to the generated code used in deployments.

```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Component Base Class"]
        B["Port Interface"]
        C["Serialization Status"]
        D["Assertion Macro"]
    end

    subgraph "Code Entity Space"
        A --> "Fw::PassiveComponentBase"
        A --> "Fw::ActiveComponentBase"
        B --> "Fw::InputPortBase"
        B --> "Fw::OutputPortBase"
        C --> "Fw::SerialStatus::OK"
        C --> "Fw::SerialStatus::FORMAT_ERROR"
        D --> "FW_CASSERT"
        D --> "FW_ASSERT"
    end
```
**Sources:** [Fw/Types/Types.fpp:10-14](), [Fw/Types/CAssert.h:26-32](), [docs/user-manual/framework/assert.md:9-10]()

## Service Components (`Svc`)

The `Svc` directory is a library of reusable components that provide standard spacecraft functions. These are added to a project using `add_fprime_subdirectory` in the deployment's `CMakeLists.txt` [Ref/CMakeLists.txt:34-41]().

*   **Commanding**: `CmdDispatcher` (routing commands to components) and `CmdSequencer` (loading and executing command sequences) [Ref/docs/sdd.md:29-30]().
*   **Telemetry & Events**: `TlmChan` (telemetry storage and downlink) and `EventManager` (event logging) [Ref/docs/sdd.md:26, 37]().
*   **Communication Stack**: Components like `FprimeFramer` and `FprimeDeframer` handle protocol framing.
*   **File Handling**: `FileDownlink`, `FileUplink`, and `FileManager` manage cross-link file transfers [Ref/docs/sdd.md:31-33]().
*   **System Health**: `Health` (monitoring component aliveness via pings) and `RateGroupDriver` (providing execution ticks) [Ref/docs/sdd.md:34, 36]().

**Sources:** [Ref/docs/sdd.md:24-39](), [Ref/CMakeLists.txt:34-41]()

## Driver Layer (`Drv`)

The `Drv` directory contains hardware-specific components. Most drivers implement the `ByteStreamDriverModel`, which provides a standardized interface for reading and writing raw byte streams [Drv/ByteStreamDriverModel/ByteStreamDriverModel.fpp:1-27]().

*   **IP Drivers**: Socket-based drivers for TCP/UDP communication.
*   **Linux Drivers**: Drivers for interacting with standard Linux device nodes (UART, SPI, I2C, GPIO).
*   **ByteStreamDriverModel**: Defines the `ByteStreamSend` port for outgoing data and the `ByteStreamData` port for incoming data and status [Drv/ByteStreamDriverModel/ByteStreamDriverModel.fpp:14-22]().

### ByteStreamDriverModel Mapping
This diagram maps the logical driver model to the FPP port definitions.

```mermaid
graph LR
    subgraph "Driver Model Logic"
        Send["Send Data"]
        Recv["Receive Data"]
        Status["Status Codes"]
    end

    subgraph "Code Entity (Drv Namespace)"
        Send --> "Drv::ByteStreamSend"
        Recv --> "Drv::ByteStreamData"
        Status --> "Drv::ByteStreamStatus::OP_OK"
        Status --> "Drv::ByteStreamStatus::SEND_RETRY"
    end
```
**Sources:** [Drv/ByteStreamDriverModel/ByteStreamDriverModel.fpp:4-22]()

## Build System and Configuration (`cmake`, `config`)

The `cmake` directory contains the logic for the build system. It handles the discovery of modules and the execution of the FPP/XML autocoders.

*   **cmake/FPrime.cmake**: The entry point for the F´ build system, included by the top-level `CMakeLists.txt` [CMakeLists.txt:12]().
*   **cmake/FPrime-Code.cmake**: Handles the registration of framework-level code modules [CMakeLists.txt:36]().
*   **config/**: Contains project-specific configuration.
*   **default/config/**: Provides default framework-level configuration headers that can be overridden.

**Sources:** [CMakeLists.txt:6-36]()

## Reference Deployments (`Ref`, `RPI`)

Deployments are the top-level executables built by the system. They contain a `Topology` that wires components together.

*   **Ref**: The standard reference application for Linux/macOS [Ref/README.md:3-5](). It demonstrates a collection of components including `SignalGen`, `PingReceiver`, and `BlockDriver` [Ref/docs/sdd.md:14-20](). Its `CMakeLists.txt` uses `register_fprime_deployment` to create the final binary [Ref/CMakeLists.txt:43-48]().
*   **RPI**: Specifically targets the Raspberry Pi platform, including drivers for Pi-specific hardware like GPIO and SPI.

**Sources:** [Ref/README.md:1-5](), [Ref/docs/sdd.md:10-21](), [Ref/CMakeLists.txt:43-48]()

## Supporting Infrastructure

*   **Gds**: Contains the `fprime-gds` Python package, which provides a web-based ground system for commanding and telemetry [Ref/README.md:49-52]().
*   **Utils**: Contains cross-cutting utilities like hashing and CRC checks.
*   **Os**: The Operating System Abstraction Layer (OSAL) providing unified interfaces for `Os::Task`, `Os::Queue`, and `Os::File`.
*   **FppTestProject**: A suite of tests used to validate the FPP autocoder against various language constructs.

**Sources:** [Ref/README.md:49-57](), [README.md:12-18]()
