# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/fprime-tools-ci.yml](.github/workflows/fprime-tools-ci.yml)
- [.github/workflows/integration-tests.yml](.github/workflows/integration-tests.yml)
- [.github/workflows/publish.yml](.github/workflows/publish.yml)
- [.gitignore](.gitignore)
- [LICENSE.txt](LICENSE.txt)
- [NOTICE.txt](NOTICE.txt)
- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [setup.py](setup.py)
- [src/fprime/__init__.py](src/fprime/__init__.py)
- [src/fprime/common/__init__.py](src/fprime/common/__init__.py)
- [src/fprime/common/models/__init__.py](src/fprime/common/models/__init__.py)

</details>



The `fprime-tools` package provides the primary command-line interface (CLI) and support infrastructure for developing flight software with the F´ (F Prime) framework. It serves as the orchestration layer that bridges high-level developer intent with low-level build systems (CMake, Ninja/Make), modeling languages (FPP), and project scaffolding (Cookiecutter).

## Purpose and Scope

`fprime-tools` is designed to simplify the F´ development lifecycle by providing a unified entry point, `fprime-util` [[project.scripts]:73-73](). It solves several key problems in the F´ ecosystem:
*   **Build Complexity:** Automates CMake cache management and target execution.
*   **Model-Driven Development:** Integrates FPP (F Prime Prime) tools for implementation generation and topology visualization.
*   **Boilerplate Reduction:** Provides standardized templates for components, ports, and deployments.
*   **Environment Validation:** Ensures the developer's environment matches the requirements of the F´ framework version being used [[project.scripts]:74-74]().

### System Context Diagram
The following diagram illustrates how `fprime-util` acts as the central dispatcher for various subsystems within the codebase.

**fprime-tools Subsystem Dispatch**
```mermaid
graph TD
    "fprime-util"["fprime-util (fprime.util.__main__:main)"] --> "fbuild"["fbuild Subsystem (fprime.fbuild)"]
    "fprime-util" --> "fpp"["FPP Integration (fprime.fpp)"]
    "fprime-util" --> "cookiecutter"["Scaffolding (fprime.cookiecutter_templates)"]
    "fprime-util" --> "version_check"["fprime-version-check (fprime.util.versioning:main)"]

    "fbuild" --> "CMake"["CMake / Ninja / Make"]
    "fpp" --> "FPP_Tools"["FPP Binaries (fpp-check, fpp-to-cpp)"]
    "cookiecutter" --> "Templates"["Jinja2 Templates"]
```
**Sources:** [pyproject.toml:72-74](), [README.md:1-7]()

---

## Core Components

### 1. Build Management (`fbuild`)
The `fbuild` package is a Python abstraction over CMake. It manages build directories (caches), detects toolchains, and executes specific build targets like `generate`, `build`, and `check`. It handles the logic for locating the nearest project root and managing `settings.ini` configurations.

For details, see [Build System: fbuild Subsystem](#3).

### 2. FPP Tooling Integration (`fpp`)
This component wraps the F Prime Prime (FPP) modeling toolchain. It provides the logic for the `fprime-util impl` command, which generates C++ implementation stubs from FPP models, and the `fprime-util visualize` command for architectural diagrams.

For details, see [FPP Tooling Integration](#4).

### 3. Project Scaffolding
Using `cookiecutter`, `fprime-tools` allows developers to quickly generate new F´ entities (Components, Deployments, Modules) that follow project standards and include necessary CMake registration.

For details, see [Project Scaffolding: cookiecutter Templates](#5).

### 4. Serialization and Common Models
The package includes a compatibility layer for F´ data types. While many models have migrated to `fprime-gds`, `fprime-tools` maintains shims to ensure backward compatibility and core type definitions.

For details, see [Serialization Compatibility Layer](#6).

---

## Code Entity Mapping

The following diagram maps the logical functional areas to their specific entry points and package locations within the `src/fprime` directory.

**Functional to Code Entity Mapping**
```mermaid
graph LR
    subgraph "CLI Entry Points"
        "main"["fprime.util.__main__:main"]
        "v_main"["fprime.util.versioning:main"]
    end

    subgraph "Logic Packages"
        "fbuild_pkg"["fprime.fbuild"]
        "fpp_pkg"["fprime.fpp"]
        "template_pkg"["fprime.cookiecutter_templates"]
        "common_pkg"["fprime.common"]
    end

    "main" -- "dispatches to" --> "fbuild_pkg"
    "main" -- "dispatches to" --> "fpp_pkg"
    "main" -- "uses" --> "template_pkg"
    "v_main" -- "validates" --> "common_pkg"
```
**Sources:** [pyproject.toml:72-74](), [pyproject.toml:89-93]()

---

## Navigation

To explore the codebase further, refer to the following child pages:

*   **[Getting Started](#1.1):** Covers installation via `pip` [[README.md:3-7]()] and developer setup using `pip install -e .` [[README.md:22-24]()]. It also lists key dependencies like `pexpect`, `cookiecutter`, and `gcovr` [[pyproject.toml:34-42]()].
*   **[Repository Layout](#1.2):** Provides a map of the `src-layout` directory structure [[pyproject.toml:89-93]()] and explains where to find build logic, templates, and tests.

### Continuous Integration
The project maintains rigorous testing through GitHub Actions, ensuring compatibility across Python versions (3.9–3.13) [[.github/workflows/fprime-tools-ci.yml:19-19]()] and F´ framework releases [[.github/workflows/integration-tests.yml:21-21]()].

**Sources:** [.github/workflows/fprime-tools-ci.yml:1-34](), [.github/workflows/integration-tests.yml:1-67]()
