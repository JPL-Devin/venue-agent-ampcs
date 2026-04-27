# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [fprime-pfsoc-linux/Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp](fprime-pfsoc-linux/Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp)

</details>



The `fprime-pfsoc-linux` library provides a standardized bridge between F´ software components and the Microchip PolarFire SoC (PFSoC) FPGA hardware resources. This bridge is implemented using the Linux **Userspace I/O (UIO)** framework, which allows user-space drivers to perform memory-mapped I/O (MMIO) and handle hardware interrupts without writing custom kernel modules [README.md:15-16]().

The architecture is organized into a strict three-layer hierarchy—Types, Ports, and Components—ensuring that hardware-specific data structures and communication protocols are decoupled from the high-level application logic.

### Architectural Layering

The library follows the standard F´ pattern of separating data definitions from interface definitions, which are then implemented by functional components.

| Layer | Directory | Purpose |
| :--- | :--- | :--- |
| **Types** | `fprime-pfsoc-linux/Types/` | Defines shared data structures and constants used across the library [README.md:11](). |
| **Ports** | `fprime-pfsoc-linux/Ports/` | Defines the communication interfaces (Read/Write/Interrupt) between drivers and users [README.md:9-10](). |
| **Components** | `fprime-pfsoc-linux/Components/` | Contains the C++ implementation of the driver logic, such as the `LinuxAmbaIf` component [README.md:7-8](). |

**Sources:** [README.md:5-11]()

### Hardware-to-Software Mapping

The library maps physical FPGA resources (AXI/AMBA registers and IRQs) into the F´ component architecture. The `LinuxAmbaIf` component acts as the primary gateway, translating F´ port calls into memory-mapped register accesses on the PFSoC.

**System Entity Relationship**
```mermaid
graph TD
    subgraph "F_Software_Space"
        [AppComp] -- "AmbaRead/Write" --> [LinuxAmbaIf]
        [LinuxAmbaIf] -- "AmbaInterrupt" --> [AppComp]
    end

    subgraph "Linux_Kernel_Space"
        [LinuxAmbaIf] -- "mmap/dev/uioX" --> [UIO_Driver]
        [UIO_Driver] -- "sys_read/poll" --> [IRQ_Subsystem]
    end

    subgraph "PFSoC_Hardware_Space"
        [UIO_Driver] -- "AXI_Bus" --> [FPGA_Registers]
        [FPGA_Registers] -- "Hardware_Signal" --> [PL_to_PS_IRQ]
    end
```
**Sources:** [README.md:15-16](), [Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp:21-35]()

### Layer 1: Type Definitions (Types Layer)

The Types layer resides in the `PfSocLinuxDrv` module. It serves as the "data contract" for the library. By defining types in `.fpp` files, the F´ autocoder generates C++ classes that ensure type safety and consistent data representation across the entire flight software stack. This layer also defines alignment constants, such as `ALIGN_32` and `ALIGN_64`, to ensure bus-compliant memory access [Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp:11-15]().

For details on the specific types used for PFSoC hardware interaction, see [Type Definitions (Types Layer)](#2.1).

**Sources:** [README.md:11](), [Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp:1-15]()

### Layer 2: Port Definitions (Ports Layer)

Ports define the signatures for interactions between components. In this library, ports are specialized for AMBA/AXI bus operations. These ports allow user components to request 32-bit or 64-bit reads and writes, and to receive asynchronous interrupt notifications from the hardware. The `LinuxAmbaIf` component exposes these as synchronous input ports for register access and an output port for interrupts [Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp:21-34]().

For details on the `AmbaRead`, `AmbaWrite`, and `AmbaInterrupt` signatures, see [Port Definitions (Ports Layer)](#2.2).

**Sources:** [README.md:9-10](), [Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp:21-34]()

### Layer 3: Component Implementation

The `LinuxAmbaIf` component is the functional core of the library. It is a **passive component** that implements the port interfaces defined in the Ports layer [Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp:5](). It manages the lifecycle of the UIO device file, performs register access with bounds checking, and handles standard F´ framework requirements such as telemetry, events, and commands [Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp:36-59]().

**Code Entity Mapping**
```mermaid
classDiagram
    class "PfSocLinuxDrv::LinuxAmbaIf" {
        <<Component>>
        +write32In()
        +read32In()
        +CLEAR_EVENT_THROTTLE()
        -ALIGN_32
        -ALIGN_64
    }
    class "AmbaRead32" {
        <<Port>>
        +addr: U64
        +val: U32
    }
    class "AmbaInterrupt" {
        <<Port>>
    }

    "PfSocLinuxDrv::LinuxAmbaIf" ..|> "AmbaRead32" : implements_read32In
    "PfSocLinuxDrv::LinuxAmbaIf" --|> "AmbaInterrupt" : emits_interruptOut
```
**Sources:** [README.md:15-16](), [Components/PfSocLinuxDrv/LinuxAmbaIf/LinuxAmbaIf.fpp:5-67]()
