# Page: Component and Module Templates

# Component and Module Templates

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/cookiecutter.json](src/fprime/cookiecutter_templates/cookiecutter-fprime-component/cookiecutter.json)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/hooks/pre_gen_project.py](src/fprime/cookiecutter_templates/cookiecutter-fprime-component/hooks/pre_gen_project.py)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/CMakeLists.txt](src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/CMakeLists.txt)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/docs/sdd.md](src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/docs/sdd.md)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.cpp](src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.cpp)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.fpp](src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.fpp)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.hpp](src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.hpp)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/cookiecutter.json](src/fprime/cookiecutter_templates/cookiecutter-fprime-module/cookiecutter.json)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/CMakeLists.txt](src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/CMakeLists.txt)
- [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/{{cookiecutter.module_name}}.fpp](src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/{{cookiecutter.module_name}}.fpp)

</details>



The `fprime-tools` package provides a standardized scaffolding system using [Cookiecutter](https://cookiecutter.readthedocs.io/) to generate architectural units for F´ projects. These templates ensure that new components and modules adhere to the framework's directory structure, naming conventions, and CMake registration requirements.

## Component Template: cookiecutter-fprime-component

The component template generates a complete F´ component directory including FPP modeling files, C++ placeholders, CMake configuration, and documentation stubs.

### Configuration Variables
The template behavior is driven by `cookiecutter.json`, which defines the parameters collected from the user during the `fprime-util new --component` flow.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `component_name` | The PascalCase name of the component | `MyComponent` |
| `component_namespace` | C++ and FPP namespace for the component | `Components` |
| `component_kind` | Execution semantics: `active`, `passive`, or `queued` | `active` |
| `enable_commands` | Whether to include command dispatching ports | `yes` |
| `enable_telemetry` | Whether to include telemetry channel ports | `yes` |
| `enable_events` | Whether to include event logging ports | `yes` |
| `enable_parameters` | Whether to include parameter management ports | `yes` |

**Sources:** [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/cookiecutter.json:1-20]()

### Component Kind Implementation
The `{{cookiecutter.component_name}}.fpp` file uses Jinja2 logic to enforce F´ architectural constraints based on the `component_kind` selected:

1.  **Active Components**: Require at least one asynchronous input (command or port) to drive the internal thread. The template adds a `TODO` async command or `Svc.Sched` port [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.fpp:4-13]().
2.  **Queued Components**: Require at least one synchronous and one asynchronous input. The template scaffolds both to ensure the component is valid for the autocoder [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.fpp:14-27]().
3.  **Passive Components**: Execute on the thread of the caller and do not require specific port types.

### Standard Ports and Imports
The template conditionally imports standard F´ framework types based on the `enable_*` flags. If enabled, the FPP file includes the necessary `import` statements and standard ports (e.g., `prmGetOut`, `prmSetOut` for parameters) [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.fpp:52-70]().

### Lifecycle Hooks
The template employs a `pre_gen_project.py` hook to validate inputs before any files are written to disk. It calls `is_valid_name` from the `fprime.util.cookiecutter_wrapper` module to ensure the component name does not contain illegal characters or spaces [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/hooks/pre_gen_project.py:1-8]().

### SDD Documentation Standard
Every component is generated with a `docs/sdd.md` (Software Design Document) file. This encourages developers to document requirements, high-level design, and configuration parameters immediately upon creation [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/docs/sdd.md:1-22]().

**Sources:** [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.fpp:1-72](), [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/docs/sdd.md:1-22]()

---

## Module Template: cookiecutter-fprime-module

The module template is used for non-component architectural units, such as shared FPP types (enums, arrays, structs) or port definitions.

### Template Structure
The module template is significantly lighter than the component template. It generates:
1.  **CMakeLists.txt**: Calls `register_fprime_library` with the FPP file as an `AUTOCODER_INPUTS` [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/CMakeLists.txt:13-16]().
2.  **FPP File**: Provides commented-out examples for defining `enum`, `array`, `struct`, and `port` types [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/{{cookiecutter.module_name}}.fpp:1-20]().

**Sources:** [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/cookiecutter.json:1-6](), [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/CMakeLists.txt:1-17]()

---

## Data Flow and Implementation

The following diagrams illustrate how user input flows through the cookiecutter variables into the generated F´ source code.

### Natural Language to FPP Logic Mapping
This diagram shows how the `cookiecutter.json` prompts map to the generated FPP architectural constraints.

Title: Component Generation Logic Flow
```mermaid
graph TD
    "Prompt: Select component kind" -- "active" --> "FPP: active component"
    "Prompt: Select component kind" -- "queued" --> "FPP: queued component"
    
    "FPP: active component" --> "Check: enable_commands?"
    "Check: enable_commands?" -- "yes" --> "FPP: async command TODO"
    "Check: enable_commands?" -- "no" --> "FPP: async input port TODO"
    
    "Prompt: Enable Telemetry?" -- "yes" --> "FPP: import Fw.Channel"
    "Prompt: Enable Events?" -- "yes" --> "FPP: import Fw.Event"
    "Prompt: Enable Parameters?" -- "yes" --> "FPP: param get/set ports"
```
**Sources:** [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/cookiecutter.json:10-19](), [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/{{cookiecutter.component_name}}.fpp:4-70]()

### Build System Integration
This diagram shows how the generated `CMakeLists.txt` interacts with the F´ build system.

Title: CMake Registration Data Flow
```mermaid
graph LR
    subgraph "Generated Files"
        "FPP_FILE [{{name}}.fpp]"
        "CPP_FILE [{{name}}.cpp]"
        "CMAKELISTS [CMakeLists.txt]"
    end

    subgraph "fprime-tools CMake API"
        "register_fprime_library"
    end

    "CMAKELISTS" -- "defines" --> "AUTOCODER_INPUTS"
    "CMAKELISTS" -- "defines" --> "SOURCES"
    "AUTOCODER_INPUTS" -- "contains" --> "FPP_FILE"
    "SOURCES" -- "contains" --> "CPP_FILE"
    
    "CMAKELISTS" -- "calls" --> "register_fprime_library"
    "register_fprime_library" -- "consumes" --> "AUTOCODER_INPUTS"
    "register_fprime_library" -- "consumes" --> "SOURCES"
```
**Sources:** [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/CMakeLists.txt:17-24](), [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/CMakeLists.txt:13-16]()

## Comparison of Templates

| Feature | Component Template | Module Template |
| :--- | :--- | :--- |
| **Primary Output** | `{{name}}.fpp`, `{{name}}.cpp`, `{{name}}.hpp` | `{{name}}.fpp` |
| **CMake Target** | `register_fprime_library` | `register_fprime_library` |
| **Unit Tests** | Scaffolded (commented out) | None |
| **Documentation** | `docs/sdd.md` | None |
| **Complexity** | High (handles threads/ports) | Low (pure types) |

**Sources:** [src/fprime/cookiecutter_templates/cookiecutter-fprime-component/{{cookiecutter.component_name}}/CMakeLists.txt:27-36](), [src/fprime/cookiecutter_templates/cookiecutter-fprime-module/{{cookiecutter.module_name}}/CMakeLists.txt:13-16]()
