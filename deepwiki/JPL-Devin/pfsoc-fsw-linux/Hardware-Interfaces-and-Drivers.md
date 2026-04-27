# Hardware Interfaces and Drivers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PfSocLinux/Top/instances.fpp](PfSocLinux/Top/instances.fpp)

</details>



The `pfsoc-fsw-linux` deployment leverages the Linux kernel's abstraction layers to interact with the Microchip PolarFire SoC (MPFS) hardware. Instead of writing bare-metal register-level drivers, the flight software (FSW) utilizes standard Linux interfaces such as `devfs` and `sysfs`. These interfaces are wrapped within the F´ Driver component pattern, providing a consistent port-based interface to the rest of the FSW topology.

## Architectural Overview of Hardware Access

Hardware access in this deployment follows a layered approach where the F´ components act as a bridge between the F´ port-based communication and the Linux system calls.

1.  **F´ Component Layer**: Passive or Active components that define the command, telemetry, and data ports for a specific peripheral.
2.  **Linux System Call Layer**: Standard `open()`, `read()`, `write()`, and `ioctl()` calls targeting device nodes in `/dev` or attributes in `/sys`.
3.  **Kernel Driver Layer**: PolarFire-specific drivers (e.g., Cadence I2C/SPI controllers) managed by the Linux kernel.
4.  **Hardware Layer**: The Physical Microchip PolarFire SoC MSS or FPGA fabric peripherals.

### Data Flow: Component to Hardware

The following diagram illustrates the flow of a command from the FSW to a hardware peripheral through the Linux filesystem abstraction.

**Hardware Access Path**
```mermaid
graph TD
    subgraph "F´ Framework Space"
        [F_Prime_Component] -- "Invoke Port" --> [Driver_Implementation_Member_Functions]
    end

    subgraph "Linux Userspace"
        [Driver_Implementation_Member_Functions] -- "write()/ioctl()" --> [Device_Node]
        [Device_Node] --> [File_Descriptor_Table]
    end

    subgraph "Linux Kernel Space"
        [File_Descriptor_Table] -- "VFS" --> [MPFS_Specific_Kernel_Driver]
    end

    subgraph "Hardware"
        [MPFS_Specific_Kernel_Driver] -- "Memory Mapped I/O" --> [MPFS_Peripheral_Registers]
    end
```
**Sources:** [PfSocLinux/Top/instances.fpp:61-61]()

---

## Interface Mechanisms

The FSW utilizes three primary methods for hardware interaction, depending on the peripheral type and performance requirements.

### 1. I2C and SPI via `/dev` (devfs)
For standard serial buses like I2C and SPI, the FSW uses the Linux `spidev` and `i2c-dev` interfaces. 
- **I2C**: Accessed via `/dev/i2c-N`. The FSW opens the device node and uses `ioctl(I2C_SLAVE)` to set the target address before performing `read()` or `write()` operations.
- **SPI**: Accessed via `/dev/spidevN.M`. The FSW configures bus speed, mode, and word length using `ioctl()` calls.

### 2. GPIO via `/sys/class/gpio` (sysfs)
General Purpose I/O pins are managed through the Linux `sysfs` interface.
- **Exporting**: Writing the pin number to `/sys/class/gpio/export`.
- **Direction**: Writing `in` or `out` to `/sys/class/gpio/direction`.
- **Value**: Reading or writing `0` or `1` to `/sys/class/gpio/gpioX/value`.

### 3. Direct Register Access via `/dev/mem`
For high-performance FPGA fabric cores or MSS registers not covered by a kernel driver, the FSW can use `mmap()` on `/dev/mem`.
- The FSW opens `/dev/mem` (requiring root or specific group privileges).
- It maps the physical address range of the MPFS peripheral into the process's virtual memory space.
- Registers are then accessed via volatile pointer offsets.

---

## F´ Driver Component Pattern

To maintain the modularity of the F´ framework, hardware interactions are encapsulated in **Driver Components**. These components follow a specific implementation pattern to bridge the gap between Linux's file-based I/O and F´'s port-based messaging.

### Implementation Structure

A typical hardware driver component in this deployment consists of:
- **FPP Model**: Defines the input/output ports (e.g., `dataSend`, `dataRecv`) and telemetry/events for monitoring the hardware state.
- **C++ Implementation**:
    - **Initialization**: The `init()` or a custom `open()` method handles the `open()` system call to the Linux device node.
    - **Data Handling**: Input ports trigger logic that performs synchronous or asynchronous Linux system calls.
    - **Error Handling**: Failures in system calls (returning -1) are caught and emitted as F´ Events.

**Driver Component Interaction**
```mermaid
classDiagram
    class "Drv::TcpClient" {
        <<Passive Component>>
        -m_socketFd : int
        +init(int instanceId)
        +open(const char* hostname, U16 port)
        +send_handler(int portNum, Fw::Buffer &buffer)
    }
    class "Svc::LinuxTimer" {
        <<Passive Component>>
        -m_timerId : timer_t
        +startTimer(U32 interval)
    }
    class "Linux_POSIX_API" {
        <<System>>
        +socket()
        +connect()
        +send()
        +timer_create()
    }
    "Drv::TcpClient" --> "Linux_POSIX_API" : "socket/connect/send"
    "Svc::LinuxTimer" --> "Linux_POSIX_API" : "timer_create/timer_settime"
```
**Sources:** [PfSocLinux/Top/instances.fpp:59-61]()

---

## Key Hardware Interfaces on PolarFire SoC

The following table details the mapping of F´ component instances to Linux hardware interfaces as defined in the system topology.

| Interface | Component Instance | Linux Interface / System Call | Purpose |
| :--- | :--- | :--- | :--- |
| **System Clock** | `posixTime` | `clock_gettime(CLOCK_REALTIME)` | High-resolution timestamping for telemetry. |
| **Scheduling** | `linuxTimer` | `timer_create(CLOCK_REALTIME)` | Drives the FSW 1Hz/10Hz rate groups. |
| **GDS Link** | `comDriver` | `socket(AF_INET, SOCK_STREAM)` | TCP/IP connection to the Ground Data System. |
| **Resources** | `systemResources` | `/proc/meminfo`, `/proc/stat` | CPU and memory utilization telemetry. |

**Sources:** [PfSocLinux/Top/instances.fpp:53-61]()

### Execution Driving via LinuxTimer
The `linuxTimer` component [PfSocLinux/Top/instances.fpp:59-59]() is critical as it serves as the heartbeat of the system. It utilizes the Linux `timer_create` and `timer_settime` APIs to generate periodic signals. These signals are caught and translated into F´ port calls to the `rateGroupDriverComp` [PfSocLinux/Top/instances.fpp:55-55](), which then dispatches to the active rate groups:
- `rateGroup1Comp` (Priority 43) [PfSocLinux/Top/instances.fpp:29-32]()
- `rateGroup2Comp` (Priority 42) [PfSocLinux/Top/instances.fpp:34-37]()
- `rateGroup3Comp` (Priority 41) [PfSocLinux/Top/instances.fpp:39-42]()

**Sources:** [PfSocLinux/Top/instances.fpp:29-61]()
