# Page: Reusable Subtopologies

# Reusable Subtopologies

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Ref/Top/CMakeLists.txt](Ref/Top/CMakeLists.txt)
- [Ref/Top/RefTopology.cpp](Ref/Top/RefTopology.cpp)
- [Ref/Top/RefTopologyDefs.hpp](Ref/Top/RefTopologyDefs.hpp)
- [Ref/Top/instances.fpp](Ref/Top/instances.fpp)
- [Ref/Top/topology.fpp](Ref/Top/topology.fpp)
- [Svc/Health/Health.fpp](Svc/Health/Health.fpp)
- [Svc/Subtopologies/CMakeLists.txt](Svc/Subtopologies/CMakeLists.txt)
- [Svc/Subtopologies/CdhCore/CdhCore.fpp](Svc/Subtopologies/CdhCore/CdhCore.fpp)
- [Svc/Subtopologies/CdhCore/CdhCoreConfig/CdhCoreConfig.fpp](Svc/Subtopologies/CdhCore/CdhCoreConfig/CdhCoreConfig.fpp)
- [Svc/Subtopologies/CdhCore/docs/sdd.md](Svc/Subtopologies/CdhCore/docs/sdd.md)
- [Svc/Subtopologies/ComCcsds/ComCcsds.fpp](Svc/Subtopologies/ComCcsds/ComCcsds.fpp)
- [Svc/Subtopologies/ComCcsds/ComCcsdsConfig/ComCcsdsConfig.fpp](Svc/Subtopologies/ComCcsds/ComCcsdsConfig/ComCcsdsConfig.fpp)
- [Svc/Subtopologies/ComCcsds/docs/sdd.md](Svc/Subtopologies/ComCcsds/docs/sdd.md)
- [Svc/Subtopologies/ComFprime/ComFprime.fpp](Svc/Subtopologies/ComFprime/ComFprime.fpp)
- [Svc/Subtopologies/ComFprime/ComFprimeConfig/ComFprimeConfig.fpp](Svc/Subtopologies/ComFprime/ComFprimeConfig/ComFprimeConfig.fpp)
- [Svc/Subtopologies/ComFprime/docs/sdd.md](Svc/Subtopologies/ComFprime/docs/sdd.md)
- [Svc/Subtopologies/ComLoggerTee/ComLoggerTeeConfig/ComLoggerTeeConfig.fpp](Svc/Subtopologies/ComLoggerTee/ComLoggerTeeConfig/ComLoggerTeeConfig.fpp)
- [Svc/Subtopologies/ComLoggerTee/subtopology-template.fppi](Svc/Subtopologies/ComLoggerTee/subtopology-template.fppi)
- [Svc/Subtopologies/DataProducts/DataProducts.fpp](Svc/Subtopologies/DataProducts/DataProducts.fpp)
- [Svc/Subtopologies/DataProducts/DataProductsConfig/DataProductsConfig.fpp](Svc/Subtopologies/DataProducts/DataProductsConfig/DataProductsConfig.fpp)
- [Svc/Subtopologies/FileHandling/FileHandling.fpp](Svc/Subtopologies/FileHandling/FileHandling.fpp)
- [Svc/Subtopologies/FileHandling/FileHandlingConfig/FileHandlingConfig.fpp](Svc/Subtopologies/FileHandling/FileHandlingConfig/FileHandlingConfig.fpp)
- [Svc/Subtopologies/FileHandling/docs/sdd.md](Svc/Subtopologies/FileHandling/docs/sdd.md)

</details>



The `Svc/Subtopologies` library provides pre-wired bundles of F´ components designed to implement common flight software deployment patterns. By using subtopologies, integration engineers can instantiate high-level functional blocks—such as a command and data handling core or a CCSDS communication stack—without manually wiring dozens of individual ports [Svc/Subtopologies/FileHandling/docs/sdd.md:1-4]().

## Overview of Available Subtopologies

Subtopologies are defined in FPP and typically include a set of component instances, internal connections, and a configuration module (e.g., `CdhCoreConfig`) to manage Base IDs and resource allocations [Svc/Subtopologies/ComCcsds/ComCcsds.fpp:16-19]().

| Subtopology | Purpose | Key Components |
| :--- | :--- | :--- |
| **CdhCore** | Command dispatch, event management, and health. | `CommandDispatcher`, `EventManager`, `Health`, `Version`, `PassiveTextLogger` |
| **ComFprime** | F´ standard framing stack (Framer/Deframer). | `FprimeFramer`, `FprimeDeframer`, `ComQueue`, `FprimeRouter` |
| **ComCcsds** | CCSDS framing stack (Space Packets/TC/TM). | `TmFramer`, `TcDeframer`, `SpacePacketFramer`, `ApidManager` |
| **FileHandling** | Uplink, downlink, and on-board management. | `FileUplink`, `FileDownlink`, `FileManager`, `PrmDb` |
| **DataProducts** | Data product management and writing. | `DpManager`, `DpWriter`, `DpCatalog` |
| **ComLoggerTee** | Splits communication traffic for logging. | `ComLogger`, `ComSplitter` |

**Sources:** [Svc/Subtopologies/FileHandling/docs/sdd.md:19-26](), [Svc/Subtopologies/ComCcsds/ComCcsds.fpp:93-111](), [Ref/Top/topology.fpp:19-22](), [Svc/Subtopologies/CdhCore/docs/sdd.md:24-33]()

---

## CdhCore: The Command & Data Handling Core
The `CdhCore` subtopology manages the central services of the flight software. It collects standard components for command dispatching, event handling, health monitoring, and version reporting [Svc/Subtopologies/CdhCore/docs/sdd.md:1-3]().

### Data Flow: Command and Event Routing
Commands enter the subtopology via the `seqCmdBuff` port and are routed to the `cmdDisp` (`Svc::CommandDispatcher`). Events and telemetry are collected and exposed via `eventsPktSend` and `tlmSendPktSend` ports for connection to the communication stack [Ref/Top/topology.fpp:151-155](). It also includes an `AssertFatalAdapter` to convert framework `FW_ASSERT`s into `FATAL` events [Svc/Subtopologies/CdhCore/docs/sdd.md:14-15]().

**Sources:** [Ref/Top/topology.fpp:151-158](), [Svc/Subtopologies/CdhCore/docs/sdd.md:24-33](), [Svc/Subtopologies/CdhCore/CdhCore.fpp:1-10]()

---

## ComCcsds: CCSDS Framing Stack
The `ComCcsds` subtopology implements a complete CCSDS-compliant communication pipeline. It manages the transition between F´ `Com` packets and CCSDS Space Packets and Transfer Frames [Svc/Subtopologies/ComCcsds/ComCcsds.fpp:113-115]().

### Communication Pipeline Architecture
The following diagram maps the logical CCSDS pipeline to the specific component instances within the `ComCcsds` subtopology.

**CCSDS Communication Data Flow**
```mermaid
graph TD
    subgraph "Downlink Path"
        "CdhCore.tlmSend" -- "Fw.Com" --> CQ["comQueue: Svc.ComQueue"]
        CQ -- "Fw.Com" --> SPF["spacePacketFramer: Svc.Ccsds.SpacePacketFramer"]
        SPF -- "Fw.Buffer" --> AGG["aggregator: Svc.ComAggregator"]
        AGG -- "Fw.Buffer" --> TF["framer: Svc.Ccsds.TmFramer"]
        TF -- "Fw.Buffer" --> DRV["comDriver: Drv.ByteStreamDriverModel"]
    end

    subgraph "Uplink Path"
        DRV -- "Fw.Buffer" --> FA["frameAccumulator: Svc.FrameAccumulator"]
        FA -- "Fw.Buffer" --> TD["tcDeframer: Svc.Ccsds.TcDeframer"]
        TD -- "Fw.Buffer" --> SPD["spacePacketDeframer: Svc.Ccsds.SpacePacketDeframer"]
        SPD -- "Fw.Buffer" --> FR["fprimeRouter: Svc.FprimeRouter"]
        FR -- "Fw.Com" --> CD["CdhCore.cmdDisp"]
    end

    subgraph "Support"
        SPF -- "Get APID" --> AM["apidManager: Svc.Ccsds.ApidManager"]
        SPF -- "Allocate" --> BM["commsBufferManager: Svc.BufferManager"]
    end
```
**Sources:** [Svc/Subtopologies/ComCcsds/ComCcsds.fpp:142-169](), [Ref/Top/topology.fpp:114-126]()

---

## ComFprime: F´ Framing Stack
The `ComFprime` subtopology implements F´’s lightweight communications stack. It comes in two variants: one that includes a `Svc::ComStub` for connecting to a `Drv::ByteStreamDriverModel` (like TCP or UART), and a `FramingSubtopology` variant that expects an external `Svc.ComInterface` [Svc/Subtopologies/ComFprime/docs/sdd.md:3-8]().

### Internal Components and Wiring
The subtopology uses a `Svc::FrameAccumulator` with an `FprimeFrameDetector` to identify incoming frames before passing them to the `Svc::FprimeDeframer` [Svc/Subtopologies/ComFprime/ComFprime.fpp:44-53]().

**ComFprime Internal Wiring (Variant A)**
```mermaid
graph LR
    subgraph "Uplink"
        "drvReceiveIn" --> CS["comStub: Svc.ComStub"]
        CS --> FA["frameAccumulator: Svc.FrameAccumulator"]
        FA --> DF["deframer: Svc.FprimeDeframer"]
        DF --> FR["fprimeRouter: Svc.FprimeRouter"]
    end
    
    subgraph "Downlink"
        "comPacketQueueIn" --> CQ["comQueue: Svc.ComQueue"]
        CQ --> F["framer: Svc.FprimeFramer"]
        F --> CS
        CS --> "drvSendOut"
    end

    subgraph "Memory"
        FA & DF & FR & F --> BM["commsBufferManager: Svc.BufferManager"]
    end
```
**Sources:** [Svc/Subtopologies/ComFprime/ComFprime.fpp:133-147](), [Svc/Subtopologies/ComFprime/ComFprime.fpp:152-165](), [Svc/Subtopologies/ComFprime/docs/sdd.md:29-37]()

---

## FileHandling Subtopology
The `FileHandling` subtopology encapsulates `Svc::FileUplink`, `Svc::FileDownlink`, `Svc::FileManager`, and `Svc::PrmDb` [Svc/Subtopologies/FileHandling/docs/sdd.md:19-26]().

### Integration with Communication Stack
File data is transferred as `Fw::Buffer` objects. The subtopology provides standard ports to bridge with the `ComQueue` of a framing subtopology [Svc/Subtopologies/FileHandling/docs/sdd.md:56-64]().

| Port Name | Direction | Connected To (Typical) |
| :--- | :--- | :--- |
| `fileDownlinkBufferSendOut` | Output | `ComCcsds.bufferQueueIn[FILE]` |
| `fileDownlinkBufferReturn` | Input | `ComCcsds.bufferReturnOut[FILE]` |
| `fileUplinkBufferSendIn` | Input | `ComCcsds.fileUplinkOut` |

**Sources:** [Ref/Top/topology.fpp:161-169](), [Svc/Subtopologies/FileHandling/docs/sdd.md:56-64]()

---

## Configuration and Instantiation

Subtopologies are instantiated in the main `topology.fpp` file using the `instance` keyword [Ref/Top/topology.fpp:19-22]().

### Base ID Management
Each subtopology uses a `BASE_ID` constant defined in its configuration module. Component IDs within the subtopology are calculated as offsets from this base [Svc/Subtopologies/ComCcsds/ComCcsdsConfig/ComCcsdsConfig.fpp:3](). In the Reference deployment, subtopologies are assigned unique ranges (e.g., `0xDSSCCxxx` where `SS` is the subtopology digit) [Ref/Top/instances.fpp:7-14]().

```fpp
# Example Base ID Definition
module ComCcsdsConfig {
    constant BASE_ID = 0x02000000
}

# Instance with offset
instance comQueue: Svc.ComQueue base id ComCcsdsConfig.BASE_ID + 0x00000
```
**Sources:** [Svc/Subtopologies/ComCcsds/ComCcsdsConfig/ComCcsdsConfig.fpp:1-3](), [Svc/Subtopologies/ComCcsds/ComCcsds.fpp:15-16](), [Ref/Top/instances.fpp:7-14]()

### Scheduling (Rate Groups)
Subtopologies expose "Run" ports that must be connected to the deployment's `RateGroup` components to drive execution [Ref/Top/topology.fpp:86-91]().

```fpp
connections RateGroups {
    rateGroup1Comp.RateGroupMemberOut[2] -> CdhCore.Subtopology.tlmSendRun
    rateGroup1Comp.RateGroupMemberOut[3] -> FileHandling.Subtopology.fileDownlinkRun
    rateGroup1Comp.RateGroupMemberOut[5] -> ComCcsds.Subtopology.comQueueRun
    rateGroup3Comp.RateGroupMemberOut[0] -> CdhCore.Subtopology.healthRun
}
```
**Sources:** [Ref/Top/topology.fpp:82-105](), [Svc/Subtopologies/FileHandling/docs/sdd.md:52-54]()

### Health Monitoring (Ping Entries)
Deployments using subtopologies must provide `PingEntries` in their `TopologyDefs.hpp` to define warning and fatal thresholds for the health-check service [Ref/Top/RefTopologyDefs.hpp:33-51]().

**Sources:** [Ref/Top/RefTopologyDefs.hpp:18-27](), [Ref/Top/RefTopologyDefs.hpp:52-71]()
