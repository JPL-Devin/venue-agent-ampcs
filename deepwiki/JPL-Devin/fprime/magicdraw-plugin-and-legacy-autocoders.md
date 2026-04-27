# Page: MagicDraw Plugin and Legacy Autocoders

# MagicDraw Plugin and Legacy Autocoders

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/codeql/security-pack.yml](.github/actions/codeql/security-pack.yml)
- [Fw/Deprecate.hpp](Fw/Deprecate.hpp)

</details>



The F´ framework historically relied on graphical modeling within MagicDraw (now Cameo Systems Modeler) to define component architectures and topologies. While the framework has transitioned toward the FPP (F´ Prime Prime) modeling language, the **MagicDrawCompPlugin** and the **Legacy Python Autocoders** remain critical for supporting existing missions and XML-based workflows. These tools bridge the gap between UML/SysML models and the C++ implementation by automating the generation of component base classes, port interfaces, and ground system dictionaries.

## MagicDraw Component Plugin

The MagicDraw plugin is a Java-based extension (`Autocoders/MagicDrawCompPlugin`) designed to export Integrated Simulation Framework (ISF/F´) metadata from UML models into the F´ XML format. It validates the model structure and serializes component definitions, port interfaces, and topology connections into the standard AI-XML (Autocode Interface XML) schema.

### Key Export Entities and Logic

The plugin processes UML elements through a set of specialized classes that map graphical nodes to F´ architectural constructs:

| Class | Responsibility |
| :--- | :--- |
| `ProcessISFTopology` | Traverses the UML model to identify component instances and their port-to-port connections (static routing). |
| `ISFComponent` | Extracts component metadata, including kind (Active, Passive, Queued), commands, telemetry channels, events, and parameters. |
| `IsfCompXmlWriter` | Serializes the extracted `ISFComponent` data into the final `.xml` files used by the Python autocoders. |

### Data Flow: Model to XML
The plugin operates within the MagicDraw JVM, accessing the model via the MagicDraw Open API.

1.  **Selection**: The user selects a Package or Component in the MagicDraw containment tree.
2.  **Extraction**: `ISFComponent` parses UML stereotypes (e.g., `«Component»`, `«Port»`) to build an internal representation of the F´ entity.
3.  **Validation**: The plugin checks for naming collisions, missing port types, or invalid component kind assignments.
4.  **Serialization**: `IsfCompXmlWriter` generates the XML file, which includes sections for `<commands>`, `<telemetry>`, `<events>`, and `<ports>`.

## Legacy Python Autocoders

The legacy autocoding suite (`Autocoders/Python`) is a collection of Python scripts that consume AI-XML files to produce C++ source code and GDS metadata. These tools are invoked by the CMake build system during the generation phase.

### Core Generation Scripts

The suite is divided into functional generators, each responsible for a specific aspect of the F´ lifecycle:

*   **`codegen.py`**: The primary entry point for component generation. It parses the component XML and produces the `ComponentAc.hpp` and `ComponentAc.cpp` base classes.
*   **`implgen.py`**: Generates "template" implementation files (`ComponentImpl.hpp` and `ComponentImpl.cpp`). These are intended to be generated once and then modified by the developer to add business logic.
*   **`testgen.py`**: Generates the unit test harness, including `TesterBase.hpp`, `GTestBase.hpp`, and the `Tester` class skeletons.
*   **`gds_dictgen.py`**: Processes the XML to create Python dictionaries and XML descriptors used by the Ground Data System (GDS) to decode telemetry and encode commands.

### Implementation Mapping: XML to C++

The following diagram illustrates how the legacy autocoder maps system-level concepts defined in XML to specific C++ code entities within the generated base classes.

**Diagram: Legacy Autocoder Entity Mapping**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        ["XML Component Definition"]
        ["Command: <command>"]
        ["Channel: <channel>"]
        ["Port: <port>"]
    end

    subgraph "CodeEntitySpace"
        ["codegen.py"]
        
        subgraph "ComponentAc.hpp"
            ["cmdHandler_OPCODE()"]
            ["tlmWrite_ID()"]
            ["portIn_PortName()"]
            ["regCommands()"]
        end
    end

    ["XML Component Definition"] --> ["codegen.py"]
    ["Command: <command>"] -- "Triggers" --> ["cmdHandler_OPCODE()"]
    ["Channel: <channel>"] -- "Generates" --> ["tlmWrite_ID()"]
    ["Port: <port>"] -- "Generates" --> ["portIn_PortName()"]
    ["Command: <command>"] -- "Registration" --> ["regCommands()"]
```

**Sources:**
- `Autocoders/Python/src/fprime_ac/utils/DiffAndRename.py:18-19`() (Legacy utility reference)

## Data Flow and Schema Validation

To ensure the integrity of the generated code, the legacy autocoders utilize **RELAX NG (RNG)** schemas to validate the input XML before processing. This prevents malformed XML from causing cryptic C++ compiler errors.

### The Validation Pipeline

1.  **Schema Check**: The autocoder locates the appropriate `.rng` schema (e.g., `component_schema.rng`, `topology_schema.rng`) in `Autocoders/Python/schema/`.
2.  **Parsing**: The Python `lxml` or `xml.etree` modules parse the XML.
3.  **Model Construction**: The scripts build a Python object model representing the component or topology.
4.  **Template Rendering**: The autocoder uses the **Cheetah** template engine to inject the object model data into C++ code templates (`.tmpl` files).

**Diagram: Legacy Autocode Data Flow**
```mermaid
graph LR
    subgraph "InputPhase"
        ["MagicDraw Model"]
        ["MagicDrawCompPlugin"]
        ["AI-XML File"]
    end

    subgraph "ValidationPhase"
        ["RNG Schemas"]
        ["XML Validator"]
    end

    subgraph "GenerationPhase"
        ["codegen.py"]
        ["Cheetah Templates (.tmpl)"]
        ["Generated C++ (.cpp/.hpp)"]
        ["GDS Dictionary (.py)"]
    end

    ["MagicDraw Model"] --> ["MagicDrawCompPlugin"]
    ["MagicDrawCompPlugin"] --> ["AI-XML File"]
    ["AI-XML File"] --> ["XML Validator"]
    ["RNG Schemas"] --> ["XML Validator"]
    ["XML Validator"] --> ["codegen.py"]
    ["codegen.py"] --> ["Cheetah Templates (.tmpl)"]
    ["Cheetah Templates (.tmpl)"] --> ["Generated C++ (.cpp/.hpp)"]
    ["Cheetah Templates (.tmpl)"] --> ["GDS Dictionary (.py)"]
```

## Integration with Modern F´

While FPP is the modern standard, the legacy system is still supported through a "bridge" in the build system. Components defined in FPP are first translated to AI-XML by the `fpp-to-xml` tool, allowing the legacy `codegen.py` to remain the underlying engine for C++ generation in many configurations.

### Deprecation and Maintenance
As the framework evolves, certain legacy patterns are marked with the `DEPRECATED` macro defined in `Fw/Deprecate.hpp`. This macro provides a compiler-specific attribute (e.g., `__attribute__((deprecated(message)))` for GCC) to alert developers during the build process [Fw/Deprecate.hpp:10-15]().

```cpp
#ifdef __GNUC__
#define DEPRECATED(func, message) func __attribute__((deprecated(message)))
#else
#warning "No implementation of DEPRECATED for given compiler. Please check for use of DEPRECATED() functions"
#define DEPRECATED(func) func
#endif
```
[Fw/Deprecate.hpp:10-15]()

This ensures that developers using older MagicDraw-generated patterns or legacy port interfaces are alerted to migrate to modern FPP-based equivalents while maintaining backward compatibility for active missions.

**Sources:**
- `Fw/Deprecate.hpp:1-20`()
- `Autocoders/Python/src/fprime_ac/utils/DiffAndRename.py:18-19`()
- `.github/actions/codeql/security-pack.yml:18-19`() (Exclusion of legacy autocoder utilities from specific security scans)
