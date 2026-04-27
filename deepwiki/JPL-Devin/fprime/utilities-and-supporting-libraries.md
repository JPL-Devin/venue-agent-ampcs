# Page: Utilities and Supporting Libraries

# Utilities and Supporting Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Fw/FilePacket/FilePacket.cpp](Fw/FilePacket/FilePacket.cpp)
- [Fw/Types/Serializable.cpp](Fw/Types/Serializable.cpp)
- [Fw/Types/Serializable.hpp](Fw/Types/Serializable.hpp)
- [Os/ValidateFileCommon.cpp](Os/ValidateFileCommon.cpp)
- [STest/STest/Scenario/RandomScenario.hpp](STest/STest/Scenario/RandomScenario.hpp)
- [Svc/Ccsds/SpacePacketDeframer/SpacePacketDeframer.cpp](Svc/Ccsds/SpacePacketDeframer/SpacePacketDeframer.cpp)
- [Svc/Ccsds/SpacePacketDeframer/SpacePacketDeframer.fpp](Svc/Ccsds/SpacePacketDeframer/SpacePacketDeframer.fpp)
- [Svc/Ccsds/TcDeframer/TcDeframer.cpp](Svc/Ccsds/TcDeframer/TcDeframer.cpp)
- [Svc/Ccsds/TcDeframer/TcDeframer.fpp](Svc/Ccsds/TcDeframer/TcDeframer.fpp)
- [Svc/Ccsds/Types/Types.fpp](Svc/Ccsds/Types/Types.fpp)
- [Svc/FprimeDeframer/FprimeDeframer.cpp](Svc/FprimeDeframer/FprimeDeframer.cpp)
- [Svc/FprimeDeframer/test/ut/FprimeDeframerTester.cpp](Svc/FprimeDeframer/test/ut/FprimeDeframerTester.cpp)
- [Svc/FrameAccumulator/CMakeLists.txt](Svc/FrameAccumulator/CMakeLists.txt)
- [Svc/FrameAccumulator/FrameDetector/CcsdsTcFrameDetector.cpp](Svc/FrameAccumulator/FrameDetector/CcsdsTcFrameDetector.cpp)
- [Svc/FrameAccumulator/FrameDetector/FprimeFrameDetector.cpp](Svc/FrameAccumulator/FrameDetector/FprimeFrameDetector.cpp)
- [Svc/FrameAccumulator/test/ut/detectors/FprimeFrameDetectorTestMain.cpp](Svc/FrameAccumulator/test/ut/detectors/FprimeFrameDetectorTestMain.cpp)
- [Utils/CMakeLists.txt](Utils/CMakeLists.txt)
- [Utils/CRCChecker.cpp](Utils/CRCChecker.cpp)
- [Utils/CRCChecker.hpp](Utils/CRCChecker.hpp)
- [Utils/Hash/Hash.hpp](Utils/Hash/Hash.hpp)
- [Utils/Hash/HashBuffer.hpp](Utils/Hash/HashBuffer.hpp)
- [Utils/Hash/HashBufferCommon.cpp](Utils/Hash/HashBufferCommon.cpp)
- [Utils/Hash/README.md](Utils/Hash/README.md)
- [Utils/Hash/libcrc/CRC32.cpp](Utils/Hash/libcrc/CRC32.cpp)
- [Utils/Hash/openssl/SHA256.cpp](Utils/Hash/openssl/SHA256.cpp)
- [Utils/Types/CMakeLists.txt](Utils/Types/CMakeLists.txt)
- [Utils/Types/CircularBuffer.cpp](Utils/Types/CircularBuffer.cpp)
- [Utils/Types/CircularBuffer.hpp](Utils/Types/CircularBuffer.hpp)
- [Utils/Types/Queue.cpp](Utils/Types/Queue.cpp)
- [Utils/Types/Queue.hpp](Utils/Types/Queue.hpp)
- [Utils/Types/test/ut/CircularBuffer/CircularRules.cpp](Utils/Types/test/ut/CircularBuffer/CircularRules.cpp)
- [Utils/Types/test/ut/CircularBuffer/CircularRules.hpp](Utils/Types/test/ut/CircularBuffer/CircularRules.hpp)
- [Utils/Types/test/ut/CircularBuffer/CircularState.cpp](Utils/Types/test/ut/CircularBuffer/CircularState.cpp)
- [Utils/Types/test/ut/CircularBuffer/CircularState.hpp](Utils/Types/test/ut/CircularBuffer/CircularState.hpp)
- [Utils/Types/test/ut/CircularBuffer/Main.cpp](Utils/Types/test/ut/CircularBuffer/Main.cpp)
- [Utils/test/ut/RateLimiterTester.cpp](Utils/test/ut/RateLimiterTester.cpp)
- [Utils/test/ut/RateLimiterTester.hpp](Utils/test/ut/RateLimiterTester.hpp)
- [default/config/CRCCheckerConfig.hpp](default/config/CRCCheckerConfig.hpp)

</details>



The F´ framework provides a suite of cross-cutting utilities and supporting libraries designed to handle common flight software tasks such as data integrity verification, efficient data buffering, and modeling tool integration. These utilities are primarily located in the `Utils/` and `Fw/DataStructures/` directories and are used extensively by both the framework core and service components.

### Utility Architecture Overview

The following diagram illustrates how the various utility libraries interface with the core framework and the physical file system.

**Utility Component Relationships**
```mermaid
graph TD
    subgraph "Integrity & Validation"
        ["Utils::Hash"] --> ["Utils::CRCChecker"]
        ["Utils::Hash"] --> ["Os::ValidatedFile"]
        ["Utils::Hash"] --> ["Svc::FprimeDeframer"]
        ["Utils::Hash"] --> ["Svc::Ccsds::TcDeframer"]
    end

    subgraph "Data Management"
        ["Utils::Types::CircularBuffer"] --> ["Svc::FrameAccumulator"]
        ["Fw::DataStructures"] --> ["Svc::TlmChan"]
        ["Fw::DataStructures"] --> ["Svc::PrmDb"]
        ["Fw::Serializable"] --> ["Utils::Types::CircularBuffer"]
    end

    ["Utils::CRCChecker"] -- "reads/writes" --> ["Os::File"]
    ["Os::ValidatedFile"] -- "validates" --> ["Os::FileSystem"]
    ["Svc::FprimeDeframer"] -- "checks CRC" --> ["Fw::Buffer"]
```
Sources: [Utils/Hash/Hash.hpp:19-102](), [Utils/CRCChecker.cpp:24-104](), [Os/ValidateFileCommon.cpp:166-217](), [Svc/FprimeDeframer/FprimeDeframer.cpp:84-99](), [Svc/Ccsds/TcDeframer/TcDeframer.cpp:96-110]()

---

### Hashing, CRC, and Validation
F´ provides a generic `Utils::Hash` interface to abstract specific cryptographic or error-detection algorithms. Depending on the build configuration, this can resolve to SHA-256 (via OpenSSL) or CRC32 (via libcrc). These tools are critical for ensuring the integrity of files stored on disk and data frames received over communication links.

*   **`Utils::Hash`**: A generic class for incremental hash computation using `init()`, `update()`, and `finalize()` [Utils/Hash/Hash.hpp:55-78](). It supports both `HashBuffer` and raw `U32` outputs [Utils/Hash/libcrc/CRC32.cpp:54-66]().
*   **`Utils::CRCChecker`**: Provides higher-level functions to create and verify `.crc32` files associated with data files [Utils/CRCChecker.cpp:24-104](). It utilizes a block-based read approach (`CRC_FILE_READ_BLOCK`) to minimize memory overhead [Utils/CRCChecker.cpp:53-63]().
*   **`Os::ValidatedFile`**: Uses `Utils::Hash` to ensure that a file matches its expected checksum before the software attempts to process it [Os/ValidateFileCommon.cpp:171-198]().

For details, see [Hashing, CRC, and Validation](#10.1).

---

### Data Structure Utilities
The framework includes specialized data structures optimized for embedded constraints, such as fixed memory allocation and lock-free access patterns.

*   **`Utils::Types::CircularBuffer`**: A ring buffer implementation that manages an externally supplied memory block [Utils/Types/CircularBuffer.hpp:25-47](). It supports "peeking" at data without consuming it [Utils/Types/CircularBuffer.hpp:75-98]() and "rotating" the head to free space [Utils/Types/CircularBuffer.hpp:100-106]().
*   **`Fw::Serializable`**: The base class for all data that can be serialized into buffers. `LinearBufferBase` provides the underlying implementation for serializing basic types (U8, U16, U32, U64) with configurable endianness [Fw/Types/Serializable.cpp:66-187]().
*   **`Fw::DataStructures`**: A library of template-based structures including `Array`, `FifoQueue`, and `RedBlackTreeMap`. These are designed to avoid dynamic memory allocation after initialization.
*   **Throttling**: `Utils::RateLimiter` and `Utils::TokenBucket` are provided to prevent components from overwhelming the system with events or telemetry during high-frequency fault conditions.

**CircularBuffer Logic-to-Code Mapping**
```mermaid
graph LR
    subgraph "Logic: Ring Buffer"
        A["Head Pointer"]
        B["Tail (Allocated Size)"]
        C["Free Space"]
        D["High Water Mark"]
    end

    subgraph "Code: Types::CircularBuffer"
        A --> ["m_head_idx"]
        B --> ["m_allocated_size"]
        C --> ["get_free_size()"]
        D --> ["m_high_water_mark"]
        ["serialize()"] --> B
        ["rotate()"] --> A
        ["peek()"] -- "read without moving" --> A
    end
```
Sources: [Utils/Types/CircularBuffer.hpp:154-164](), [Utils/Types/CircularBuffer.hpp:67-114](), [Utils/Types/CircularBuffer.hpp:127-138]()

For details, see [Data Structure Utilities](#10.2).

---

### MagicDraw Plugin and Legacy Autocoders
F´ supports model-based engineering through integration with UML/SysML tools.

*   **MagicDraw/Cameo Plugin**: Located in `Autocoders/MagicDrawCompPlugin`, this Java-based tool allows developers to draw component architectures and topologies in MagicDraw and export them as F´ XML specifications (AI-XML).
*   **Legacy Python Autocoders**: While FPP is the modern standard, the repository maintains Python-based autocoders for processing AI-XML (Architecture Interface XML) files. These tools generate the C++ base classes, command dispatchers, and GDS dictionaries required for the software to function.

For details, see [MagicDraw Plugin and Legacy Autocoders](#10.3).

---
**Sources:**
- [Fw/Types/Serializable.cpp:42-187]()
- [Fw/Types/Serializable.hpp:45-113]()
- [Utils/Hash/Hash.hpp:19-102]()
- [Utils/Hash/libcrc/CRC32.cpp:19-75]()
- [Utils/CRCChecker.cpp:24-205]()
- [Utils/Types/CircularBuffer.hpp:25-164]()
- [Os/ValidateFileCommon.cpp:8-217]()
- [Svc/FprimeDeframer/FprimeDeframer.cpp:84-109]()
- [Svc/Ccsds/TcDeframer/TcDeframer.cpp:53-118]()
