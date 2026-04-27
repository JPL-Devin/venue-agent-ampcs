# Page: CI/CD Pipelines and Docker

# CI/CD Pipelines and Docker

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/cookiecutter-check/bootstrap.expect](.github/actions/cookiecutter-check/bootstrap.expect)
- [.github/actions/cookiecutter-check/component.expect](.github/actions/cookiecutter-check/component.expect)
- [.github/actions/cookiecutter-check/deployment.expect](.github/actions/cookiecutter-check/deployment.expect)
- [.github/actions/spelling/advice.md](.github/actions/spelling/advice.md)
- [.github/actions/spelling/allow.txt](.github/actions/spelling/allow.txt)
- [.github/actions/spelling/candidate.patterns](.github/actions/spelling/candidate.patterns)
- [.github/actions/spelling/excludes.txt](.github/actions/spelling/excludes.txt)
- [.github/actions/spelling/line_forbidden.patterns](.github/actions/spelling/line_forbidden.patterns)
- [.github/actions/spelling/patterns.txt](.github/actions/spelling/patterns.txt)
- [.github/actions/spelling/reject.txt](.github/actions/spelling/reject.txt)
- [.github/pull_request_template.md](.github/pull_request_template.md)
- [.github/workflows/build-test-macos.yml](.github/workflows/build-test-macos.yml)
- [.github/workflows/build-test-rhel8.yml](.github/workflows/build-test-rhel8.yml)
- [.github/workflows/build-test.yml](.github/workflows/build-test.yml)
- [.github/workflows/codeql-jpl-standard.yml](.github/workflows/codeql-jpl-standard.yml)
- [.github/workflows/codeql-security-scan.yml](.github/workflows/codeql-security-scan.yml)
- [.github/workflows/cppcheck-scan.yml](.github/workflows/cppcheck-scan.yml)
- [.github/workflows/cpplint-scan.yml](.github/workflows/cpplint-scan.yml)
- [.github/workflows/ext-aarch64-linux-led-blinker.yml](.github/workflows/ext-aarch64-linux-led-blinker.yml)
- [.github/workflows/ext-build-examples-repo.yml](.github/workflows/ext-build-examples-repo.yml)
- [.github/workflows/ext-build-hello-world.yml](.github/workflows/ext-build-hello-world.yml)
- [.github/workflows/ext-build-led-blinker.yml](.github/workflows/ext-build-led-blinker.yml)
- [.github/workflows/ext-build-math-comp.yml](.github/workflows/ext-build-math-comp.yml)
- [.github/workflows/ext-cookiecutters-test.yml](.github/workflows/ext-cookiecutters-test.yml)
- [.github/workflows/ext-fprime-zephyr-reference-pico2.yml](.github/workflows/ext-fprime-zephyr-reference-pico2.yml)
- [.github/workflows/ext-fprime-zephyr-reference-teensy41.yml](.github/workflows/ext-fprime-zephyr-reference-teensy41.yml)
- [.github/workflows/ext-raspberry-led-blinker.yml](.github/workflows/ext-raspberry-led-blinker.yml)
- [.github/workflows/fpp-tests.yml](.github/workflows/fpp-tests.yml)
- [.github/workflows/fpp-to-json.yml](.github/workflows/fpp-to-json.yml)
- [.github/workflows/markdown-link-check.yml](.github/workflows/markdown-link-check.yml)
- [.github/workflows/python-format.yml](.github/workflows/python-format.yml)
- [.github/workflows/reusable-get-pr-branch.yml](.github/workflows/reusable-get-pr-branch.yml)
- [.github/workflows/reusable-project-builder.yml](.github/workflows/reusable-project-builder.yml)
- [.github/workflows/reusable-project-ci.yml](.github/workflows/reusable-project-ci.yml)
- [.github/workflows/spelling.yml](.github/workflows/spelling.yml)
- [AI_POLICY.md](AI_POLICY.md)
- [Fw/Obj/CMakeLists.txt](Fw/Obj/CMakeLists.txt)
- [STest/STest/Random/Random.hpp](STest/STest/Random/Random.hpp)
- [STest/STest/Rule/Rule.hpp](STest/STest/Rule/Rule.hpp)
- [STest/STest/Scenario/BoundedIteratedScenario.hpp](STest/STest/Scenario/BoundedIteratedScenario.hpp)
- [STest/STest/Scenario/BoundedScenario.hpp](STest/STest/Scenario/BoundedScenario.hpp)
- [Svc/PassiveRateGroup/docs/sdd.md](Svc/PassiveRateGroup/docs/sdd.md)
- [Svc/SystemResources/docs/sdd.md](Svc/SystemResources/docs/sdd.md)
- [ci/helpers.bash](ci/helpers.bash)
- [ci/tests/30-ints.bash](ci/tests/30-ints.bash)
- [ci/tests/Framework.bash](ci/tests/Framework.bash)
- [ci/tests/Ref.bash](ci/tests/Ref.bash)
- [ci/tests/fputil.bash](ci/tests/fputil.bash)
- [cmake/FPrimeConfig.cmake](cmake/FPrimeConfig.cmake)
- [cmake/settings.cmake](cmake/settings.cmake)
- [cmake/toolchain/aarch64-linux.cmake](cmake/toolchain/aarch64-linux.cmake)
- [cmake/toolchain/arm-hf-linux.cmake](cmake/toolchain/arm-hf-linux.cmake)
- [cmake/toolchain/arm-sf-linux.cmake](cmake/toolchain/arm-sf-linux.cmake)
- [cmake/toolchain/raspberrypi.cmake](cmake/toolchain/raspberrypi.cmake)
- [docs/doxygen/Doxyfile](docs/doxygen/Doxyfile)
- [docs/doxygen/generate_docs.bash](docs/doxygen/generate_docs.bash)
- [docs/doxygen/mainpage.md](docs/doxygen/mainpage.md)

</details>



The F´ framework utilizes a comprehensive Continuous Integration and Continuous Delivery (CI/CD) infrastructure primarily hosted on GitHub Actions. This infrastructure ensures code quality, cross-platform compatibility, security compliance, and documentation accuracy across the framework and its ecosystem of tutorials and reference applications.

## GitHub Actions Workflows

F´ employs multiple workflows to validate changes on `devel` and `release/**` branches. These workflows are triggered by `push` and `pull_request` events, with concurrency controls to cancel in-progress runs when new updates are pushed to a PR [.github/workflows/build-test.yml:5-21]().

### Core Build and Test (Linux and macOS)
The primary CI suite runs on Ubuntu and macOS runners. It is partitioned into several key jobs:

*   **Framework Job**: Validates the core F´ framework (Fw, Os, Svc) using the `ci/tests/Framework.bash` script [.github/workflows/build-test.yml:25-35]().
*   **Ref Job**: Builds and tests the Reference Application (`Ref`) to ensure high-level topology and component integration [.github/workflows/build-test.yml:45-55]().
*   **Integration Job**: Executes system-level integration tests. On Linux, this includes memory leak detection using Valgrind [.github/workflows/build-test.yml:65-79]().
*   **macOS Job**: Mirroring the Linux tests, these run on `macos-latest` but limit parallel jobs to 2 to prevent resource exhaustion [.github/workflows/build-test-macos.yml:25-42]().
*   **RHEL8 Job**: Provides additional Linux distribution coverage by running builds in a Red Hat Enterprise Linux 8 environment [.github/workflows/build-test-rhel8.yml]().

### Cross-Compilation and External Project Validation
F´ maintains workflows to verify cross-compilation for embedded targets, specifically the Raspberry Pi and Zephyr-based platforms.

*   **RPI LedBlinker**: This workflow checks out an external repository (`fprime-workshop-led-blinker`), overlays the current F´ revision, and cross-compiles using the `raspberrypi` toolchain [.github/workflows/ext-raspberry-led-blinker.yml:33-61]().
*   **Self-Hosted Integration**: It uses a `self-hosted` runner on actual Raspberry Pi hardware to execute integration tests against the cross-compiled binary [.github/workflows/ext-raspberry-led-blinker.yml:74-102]().
*   **Zephyr Reference**: Workflows for `fprime-zephyr-reference` validate the framework against microcontrollers like the Teensy 4.1 and Raspberry Pi Pico 2 [.github/workflows/ext-fprime-zephyr-reference-teensy41.yml](), [.github/workflows/ext-fprime-zephyr-reference-pico2.yml]().
*   **Reusable Project Builder**: A shared workflow (`reusable-project-builder.yml`) allows external projects to validate their compatibility with the latest F´ changes by performing `fprime-util generate` and `fprime-util build` steps [.github/workflows/reusable-project-builder.yml:45-77]().

### Static Analysis and Security
Code quality is enforced through several automated scanning tools:

*   **CppCheck**: Generates a compilation database via `fprime-util generate -DCMAKE_EXPORT_COMPILE_COMMANDS=ON` and runs `cppcheck` with a maximum CTU (Cross Translation Unit) depth of 16 [.github/workflows/cppcheck-scan.yml:46-57](). Results are converted to SARIF format for GitHub Code Scanning alerts [.github/workflows/cppcheck-scan.yml:59-70]().
*   **Quality (Clang-Tidy)**: Performs general static analysis using `clang-tidy-12`. It differentiates between flight code (using `release.clang-tidy`) and unit test code [.github/workflows/build-test.yml:89-111]().
*   **Cpplint**: Checks C++ code against the Google C++ Style Guide [.github/workflows/cpplint-scan.yml]().
*   **CodeQL**: Performs deep semantic analysis for security vulnerabilities [.github/workflows/codeql-security-scan.yml]().

### Specialized Test Suites
*   **FppTestProject**: Validates the FPP (F Prime Prime) modeling language by building and running a suite of tests that exercise every FPP construct, including JSON model generation [.github/workflows/fpp-tests.yml:20-47]().
*   **Cookiecutter Tests**: Ensures that the `fprime-util new` templates (component, deployment, project) remain functional using `expect` scripts for automated CLI interaction [.github/workflows/ext-cookiecutters-test.yml](), [.github/actions/cookiecutter-check/bootstrap.expect]().
*   **Spelling**: Uses `check-spelling` with custom regex patterns to ignore autocoded function patterns like `.get\w+\(` and `.set\w+\(` [.github/actions/spelling/patterns.txt:146-149]().

**Sources:** [.github/workflows/build-test.yml:1-112](), [.github/workflows/build-test-macos.yml:1-105](), [.github/workflows/ext-raspberry-led-blinker.yml:1-110](), [.github/workflows/cppcheck-scan.yml:1-81](), [.github/workflows/fpp-tests.yml:1-55](), [.github/actions/spelling/patterns.txt:1-149]().

---

## Test Suites and Shell Infrastructure

The CI environment relies on a set of shell scripts located in `ci/` and `mk/ci/` to standardize test execution across different environments.

### The `fputil_action` Helper
The `ci/tests/fputil.bash` script defines the `fputil_action` function, which wraps `fprime-util` commands. It dynamically assigns a random number of parallel jobs (`JOBS`) to stress-test the build system's dependency tracking and resource management [.ci/tests/fputil.bash:17-36]().

### Integration Test Execution Flow
Integration tests involve orchestrating the GDS, the flight software binary, and a test runner (usually `pytest`).

1.  **GDS Setup**: `fprime-gds` is started headlessly with a specific dictionary [.ci/tests/fputil.bash:72-73]().
2.  **Binary Execution**: The deployment binary is launched. If Valgrind is present, it wraps the binary to detect memory leaks [.ci/tests/fputil.bash:76-89]().
3.  **Test Execution**: `pytest` runs the integration test suite using the `IntegrationTestAPI`, often with a specific deployment configuration `int_config.json` [.ci/tests/fputil.bash:104-111]().
4.  **Teardown**: The script kills the GDS and binary processes, then checks the Valgrind log for errors [.ci/tests/fputil.bash:114-126]().

### CI Data Flow Diagram

The following diagram illustrates how a code change flows through the CI pipeline into the artifact storage, mapping workflow files to the underlying shell scripts.

```mermaid
graph TD
    "DeveloperPush"["Developer Push"] --> "GHA_Trigger"["GitHub Actions Trigger"]
    subgraph "Validation_Layer"
        "GHA_Trigger" --> "BuildTest_YML"["build-test.yml"]
        "GHA_Trigger" --> "CppCheck_YML"["cppcheck-scan.yml"]
        "GHA_Trigger" --> "FppTests_YML"["fpp-tests.yml"]
    end
    subgraph "Execution_Environment"
        "BuildTest_YML" --> "Framework_Bash"["ci/tests/Framework.bash"]
        "BuildTest_YML" --> "Ref_Bash"["ci/tests/Ref.bash"]
        "Framework_Bash" --> "fputil_action"["fputil_action (fputil.bash)"]
        "fputil_action" --> "fprime_util"["fprime-util build/check"]
    end
    subgraph "Integration_Testing"
        "Ref_Bash" --> "30-ints_bash"["ci/tests/30-ints.bash"]
        "30-ints_bash" --> "integration_test"["integration_test (fputil.bash)"]
        "integration_test" --> "fprime_gds"["fprime-gds (headless)"]
        "integration_test" --> "valgrind"["Valgrind + Ref Binary"]
        "integration_test" --> "pytest"["pytest (IntegrationTestAPI)"]
    end
    "fprime_util" --> "Artifacts"["upload-artifact (logs/binaries)"]
    "pytest" --> "Artifacts"
```
**Sources:** [ci/tests/fputil.bash:1-136](), [.github/workflows/build-test.yml:25-87](), [ci/tests/30-ints.bash]().

---

## Autodocs Workflow

The documentation is automatically generated using Doxygen (for C++ API) and a custom Python script for the CMake API.

*   **Generation Script**: `docs/doxygen/generate_docs.bash` manages the lifecycle of documentation generation. It first builds the framework to ensure all autocoded files exist before Doxygen scans the source [.docs/doxygen/generate_docs.bash:48-49]().
*   **Doxygen**: Runs using the configuration in `docs/doxygen/Doxyfile` [.docs/doxygen/generate_docs.bash:58]().
*   **CMake API Docs**: Generated by `cmake/docs/docs.py`, which parses CMake files for documentation strings [.docs/doxygen/generate_docs.bash:67]().
*   **Image Handling**: The script scrapes `Fw`, `Svc`, and `Drv` directories for `.jpg`, `.png`, and `.svg` files to ensure architecture diagrams are included in the HTML output [.docs/doxygen/generate_docs.bash:74-77]().

**Sources:** [docs/doxygen/generate_docs.bash:1-79](), [docs/doxygen/Doxyfile]().

---

## Toolchains and Cross-Compilation

Cross-compilation for CI is driven by CMake toolchain files located in `cmake/toolchain/`.

*   **Raspberry Pi**: The `raspberrypi.cmake` toolchain sets `CMAKE_SYSTEM_PROCESSOR` to `arm` and includes `arm-linux-base.cmake` [.cmake/toolchain/raspberrypi.cmake:11-18](). It expects the `RPI_TOOLCHAIN_DIR` environment variable to point to the cross-compiler [.cmake/toolchain/raspberrypi.cmake:14-16]().
*   **ARM Soft-Float**: The `arm-sf-linux.cmake` toolchain provides support for ARM targets without hardware floating-point units [cmake/toolchain/arm-sf-linux.cmake]().

### Toolchain Mapping Diagram

This diagram shows the relationship between the CI environment variables and the CMake toolchain configuration used in cross-compilation workflows.

```mermaid
graph LR
    "GHA_Workflow"["ext-raspberry-led-blinker.yml"] -- "RPI_TOOLCHAIN_DIR" --> "CMake_Env"["Environment Variables"]
    "CMake_Env" -- "Read" --> "RPi_Toolchain"["cmake/toolchain/raspberrypi.cmake"]
    "RPi_Toolchain" -- "include" --> "ARM_Base"["helpers/arm-linux-base.cmake"]
    "ARM_Base" -- "SET" --> "Compiler"["arm-linux-gnueabihf-gcc"]
    "fprime_util" -- "raspberrypi" --> "RPi_Toolchain"
```
**Sources:** [.github/workflows/ext-raspberry-led-blinker.yml:23](), [cmake/toolchain/raspberrypi.cmake:1-19]().
