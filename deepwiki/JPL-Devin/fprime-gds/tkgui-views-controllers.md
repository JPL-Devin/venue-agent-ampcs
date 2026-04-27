# Page: tkGUI Views & Controllers

# tkGUI Views & Controllers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/fprime_gds/common/parsers/__init__.py](src/fprime_gds/common/parsers/__init__.py)
- [src/fprime_gds/executables/__init__.py](src/fprime_gds/executables/__init__.py)

</details>



The `tkGUI` represents a legacy Tkinter-based graphical user interface for the F´ GDS. It utilizes a Model-View-Controller (MVC) inspired architecture to manage telemetry visualization, command execution, and sequence generation. While the modern GDS has shifted toward a Flask/Vue.js web interface, the `tkGUI` components provide a desktop-native alternative for interacting with the `StandardPipeline`.

## System Architecture

The `tkGUI` architecture is divided into specialized views for data display and controllers that interface with the underlying GDS pipeline. Data flows from the `StandardPipeline` through listeners into the views, while user actions in the views are translated into commands by the controllers.

### Natural Language to Code Entity Mapping: Controllers

The following diagram maps high-level GDS control functions to the specific Python classes and methods responsible for their implementation in the `tkGUI` ecosystem.

**tkGUI Controller Mapping**
```mermaid
graph TD
    subgraph "Natural Language Space"
        A["Command Dispatching"]
        B["Telemetry Monitoring"]
        C["Sequence Management"]
        D["Dictionary Loading"]
    end

    subgraph "Code Entity Space"
        A --> E["commander.py:Commander"]
        B --> F["channel_listener.py:ChannelListener"]
        C --> G["seq_panel.py:SeqPanel"]
        D --> H["command_loader.py:CommandLoader"]
        
        E -- "calls" --> E1["commander.send_command()"]
        F -- "updates" --> F1["stripchart_panel.py:StripchartPanel"]
        G -- "invokes" --> G1["seqgen.py:generateSequence()"]
        H -- "populates" --> H1["command_args_frame.py:CommandArgsFrame"]
    end
```
**Sources:** `src/fprime_gds/tkgui/controllers/commander.py:1-100`(), `src/fprime_gds/tkgui/controllers/channel_listener.py:1-50`(), `src/fprime_gds/tkgui/views/seq_panel.py:1-120`(), `src/fprime_gds/tkgui/controllers/command_loader.py:1-60`()

## Views (Tkinter Panels)

The views are implemented as Tkinter frames or panels that handle the rendering of telemetry and command interfaces.

### Telemetry & Visualization
*   **stripchart_panel**: Provides real-time plotting of telemetry channels. It utilizes a `ChannelListener` to receive updates from the `StandardPipeline` and updates the UI canvas.
*   **telemetry_filter_panel**: Allows users to filter which telemetry channels are visible or recorded based on component name or channel ID.

### Commanding Interfaces
*   **command_args_frame**: A dynamic UI component that inspects a selected command's `CmdTemplate` and generates input fields (entries, dropdowns, checkboxes) based on the command's arguments and their types (e.g., `I32`, `Enum`, `String`).
*   **seq_panel**: The sequence management interface. It allows users to load `.seq` files, validate them against the current dictionary, and trigger the generation of binary sequence files for uplink.

**tkGUI View Data Flow**
```mermaid
graph LR
    subgraph "Pipeline"
        P["StandardPipeline"]
    end

    subgraph "Controllers"
        CL["ChannelListener"]
        CM["Commander"]
    end

    subgraph "Views"
        SCP["StripchartPanel"]
        TFP["TelemetryFilterPanel"]
        CAF["CommandArgsFrame"]
        SP["SeqPanel"]
    end

    P -- "ChData" --> CL
    CL -- "filtered data" --> SCP
    TFP -- "filter criteria" --> CL
    CAF -- "arguments" --> CM
    CM -- "encoded command" --> P
    SP -- ".seq file" --> SP_GEN["seqgen"]
    SP_GEN -- ".bin" --> P
```
**Sources:** `src/fprime_gds/tkgui/views/stripchart_panel.py:1-200`(), `src/fprime_gds/tkgui/views/command_args_frame.py:1-150`(), `src/fprime_gds/tkgui/views/seq_panel.py:50-300`()

## Controllers & Tools

Controllers act as the glue between the GUI elements and the `fprime_gds.common` logic.

### channel_listener
The `ChannelListener` class implements the data consumer interface required by the `Distributor`. It receives `ChData` objects, applies user-defined filters from the `telemetry_filter_panel`, and pushes updates to the visualization views.

### command_loader & commander
*   **CommandLoader**: Responsible for parsing the command dictionary and providing a searchable interface for the `command_args_frame`.
*   **Commander**: Handles the final stage of command dispatch. It takes the values from the `CommandArgsFrame`, validates them against the `CmdTemplate`, and uses the `CmdEncoder` to send the binary packet to the `StandardPipeline`.

### seqgen & gse_api
These tools provide the backend logic for the `SeqPanel`:
*   **seqgen**: A wrapper around `fprime_seqgen` logic that converts human-readable sequence files into F´ binary sequences.
*   **gse_api**: A legacy interface layer that provides a simplified API for the `tkGUI` to interact with the GDS core, abstracting the complexities of the `StandardPipeline` setup.

| Component | Responsibility | Key File |
| :--- | :--- | :--- |
| **ChannelListener** | Subscribes to telemetry and updates UI | `channel_listener.py` |
| **CommandLoader** | Loads and searches command definitions | `command_loader.py` |
| **Commander** | Encodes and sends commands | `commander.py` |
| **SeqGen Tool** | Generates binary command sequences | `seqgen.py` |
| **GSE API** | Legacy bridge to GDS core | `gse_api.py` |

**Sources:** `src/fprime_gds/tkgui/controllers/channel_listener.py:10-45`(), `src/fprime_gds/tkgui/controllers/commander.py:20-80`(), `src/fprime_gds/tkgui/utils/gse_api.py:1-100`()
