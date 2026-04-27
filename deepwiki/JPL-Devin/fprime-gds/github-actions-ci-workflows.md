# Page: GitHub Actions & CI Workflows

# GitHub Actions & CI Workflows

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/codeql/security-pack.yml](.github/actions/codeql/security-pack.yml)
- [.github/actions/spelling/excludes.txt](.github/actions/spelling/excludes.txt)
- [.github/actions/spelling/patterns.txt](.github/actions/spelling/patterns.txt)
- [.github/workflows/codeql-security-scan.yml](.github/workflows/codeql-security-scan.yml)
- [.github/workflows/fprime-gds-tests.yml](.github/workflows/fprime-gds-tests.yml)
- [.github/workflows/gds-cli-tests.yml](.github/workflows/gds-cli-tests.yml)
- [.github/workflows/publish.yml](.github/workflows/publish.yml)
- [.github/workflows/spelling.yml](.github/workflows/spelling.yml)
- [docs/README.md](docs/README.md)
- [src/fprime_gds/common/communication/ccsds/__init__.py](src/fprime_gds/common/communication/ccsds/__init__.py)
- [src/fprime_gds/common/communication/ccsds/chain.py](src/fprime_gds/common/communication/ccsds/chain.py)
- [src/fprime_gds/flask/logs.py](src/fprime_gds/flask/logs.py)

</details>



The `fprime-gds` repository utilizes GitHub Actions to automate testing, security scanning, spell checking, and the release process. These workflows ensure that changes to the `devel` branch maintain system stability across multiple Python versions and that security vulnerabilities are identified early.

## Core Test Workflows

The GDS employs two primary testing workflows to validate both the underlying Python libraries and the Command Line Interface (CLI) functionality.

### fprime-gds-tests.yml
This workflow handles unit testing for the core GDS library. It is triggered on pushes and pull requests targeting the `devel` branch [.github/workflows/fprime-gds-tests.yml:3-8]().

*   **Matrix Strategy:** Tests are executed against a matrix of Python versions: 3.9, 3.10, 3.11, 3.12, and 3.13 [.github/workflows/fprime-gds-tests.yml:18-20]().
*   **Execution:** The workflow installs the package in editable mode (`pip install -e .`) and runs `pytest` [.github/workflows/fprime-gds-tests.yml:31-34]().
*   **Concurrency:** To save resources, in-progress runs are cancelled if a newer run is started on the same PR, except for protected branches like `devel` or `release/*` [.github/workflows/fprime-gds-tests.yml:10-12]().

### gds-cli-tests.yml
This workflow validates the `fprime-cli` tool by performing "smoke tests" using a reference topology dictionary [.github/workflows/gds-cli-tests.yml:15]().

*   **Validation Logic:** It verifies that the CLI can successfully load the application and parse dictionaries for events, channels, and commands [.github/workflows/gds-cli-tests.yml:36-42]().
*   **Commands Tested:**
    *   `fprime-cli events --list`
    *   `fprime-cli channels --list`
    *   `fprime-cli command-send --list`

**CI Test Execution Flow**

```mermaid
graph TD
    "Push/PR"["GitHub Trigger"] --> "Matrix_Setup"["Strategy: Python 3.9-3.13"]
    subgraph "GDS Unit Tests"
        "Matrix_Setup" --> "Install_GDS"["pip install -e ."]
        "Install_GDS" --> "Pytest_Run"["pytest"]
    end
    subgraph "CLI Smoke Tests"
        "Matrix_Setup" --> "Install_CLI"["pip install ."]
        "Install_CLI" --> "Ref_Dict"["Load RefTopologyAppDictionary.xml"]
        "Ref_Dict" --> "Verify_Events"["fprime-cli events --list"]
        "Verify_Events" --> "Verify_Ch"["fprime-cli channels --list"]
        "Verify_Ch" --> "Verify_Cmd"["fprime-cli command-send --list"]
    end
```
Sources: [.github/workflows/fprime-gds-tests.yml:14-35](), [.github/workflows/gds-cli-tests.yml:18-43]()

---

## Static Analysis & Security

### codeql-security-scan.yml
The GDS uses CodeQL for semantic code analysis to detect security vulnerabilities and quality issues [.github/workflows/codeql-security-scan.yml:1-3]().

*   **Configuration:** It uses a custom security pack defined in `.github/actions/codeql/security-pack.yml` [.github/workflows/codeql-security-scan.yml:39]().
*   **Permissions:** The job requires `security-events: write` to upload results to the GitHub Security tab [.github/workflows/codeql-security-scan.yml:23]().
*   **Languages:** Specifically targets the `python` codebase [.github/workflows/codeql-security-scan.yml:28]().

### spelling.yml
Automated spell checking is performed on all pushes and pull requests using the `check-spelling` action [.github/workflows/spelling.yml:1-13]().

*   **Exclusions:** The workflow ignores specific files and patterns that contain non-prose data, such as binary files (`.bin`, `.dat`), logs, and third-party vendor directories [.github/actions/spelling/excludes.txt:7-20]().
*   **Patterns:** It uses regex to ignore technical strings like Git hashes, UUIDs, Python struct packing formats (e.g., `[<>][xcbB?hHiI...]`), and hex digits [.github/actions/spelling/patterns.txt:24-49]().
*   **Dictionaries:** Integrates multiple `cspell` dictionaries including `python`, `cpp`, `software-terms`, and `html` [.github/workflows/spelling.yml:43-57]().

Sources: [.github/workflows/codeql-security-scan.yml:3-45](), [.github/workflows/spelling.yml:30-57](), [.github/actions/spelling/excludes.txt:1-50](), [.github/actions/spelling/patterns.txt:1-50]()

---

## Build and Publish Process

The `publish.yml` workflow automates the distribution of the `fprime-gds` package to PyPI when a new release is published [.github/workflows/publish.yml:1-5]().

### Publish Pipeline
1.  **Environment Setup:** Uses Python 3.11 and installs `build` and `twine` [.github/workflows/publish.yml:19-23]().
2.  **Distribution Building:** Runs `python -m build` to generate source archives and wheels [.github/workflows/publish.yml:25]().
3.  **Verification:** Uses `twine check` to ensure the package metadata is valid [.github/workflows/publish.yml:27]().
4.  **Staging:** First publishes to `test.pypi.org` to verify the upload process [.github/workflows/publish.yml:28-31]().
5.  **Production:** Publishes to the official PyPI repository using Trusted Publishing (OIDC) [.github/workflows/publish.yml:34-36]().

**Publish Data Flow**

```mermaid
graph LR
    "Release_Event"["GitHub Release Published"] --> "Build_Node"["python -m build"]
    "Build_Node" --> "Dist_Files"["dist/* (.tar.gz, .whl)"]
    "Dist_Files" --> "Twine_Check"["twine check"]
    "Twine_Check" --> "TestPyPI"["Upload to TestPyPI"]
    "TestPyPI" --> "PyPI"["Upload to PyPI (Trusted Publishing)"]
    
    style "PyPI" stroke-width:4px
```
Sources: [.github/workflows/publish.yml:7-36]()

---

## Infrastructure Configuration

### Configuration Mapping
The GDS requires alignment between the Python `ConfigManager` and the flight software's `FpConfig.hpp`. CI ensures that these mappings remain valid for the default `U32` configurations used in testing [docs/README.md:16-27]().

| GDS Field (ConfigManager) | FPrime Flag (FpConfig.hpp) |
| :--- | :--- |
| `msg_len` | `TOKEN_TYPE` |
| `msg_desc` | `FwPacketDescriptorType` |
| `op_code` | `FwOpcodeType` |
| `ch_id` | `FwChanIdType` |
| `event_id` | `FwEventIdType` |

### Log Handling in CI
While not a workflow itself, the `LogList` and `LogFile` resources in the Flask server facilitate the retrieval of logs generated during CI runs or local testing by providing RESTful access to the `logdir` [src/fprime_gds/flask/logs.py:10-40]().

Sources: [docs/README.md:12-27](), [src/fprime_gds/flask/logs.py:10-57]()
