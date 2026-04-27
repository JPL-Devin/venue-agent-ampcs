# Page: Testing Infrastructure

# Testing Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/actions/cookiecutter-check/bootstrap.expect](.github/actions/cookiecutter-check/bootstrap.expect)
- [.github/actions/cookiecutter-check/component.expect](.github/actions/cookiecutter-check/component.expect)
- [.github/actions/cookiecutter-check/deployment.expect](.github/actions/cookiecutter-check/deployment.expect)
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
- [ci/tests/fputil.bash](ci/tests/fputil.bash)

</details>



F´ provides a multi-layered testing infrastructure designed to validate software at every level of the development lifecycle, from individual component logic to full-system deployments. The framework integrates automated code generation for test harnesses, a rule-based state-space testing library, and comprehensive CI/CD pipelines.

## Unit Testing with GTest and STest

The primary method for verifying F´ components is through unit tests. F´ leverages an autocoder to generate C++ test harnesses that wrap the component under test, providing a controlled environment to inject port calls and inspect outputs.

- **GTest Harness**: The autocoder generates `GTestBase` and `Tester` classes. These provide `invoke_to_*` methods to call input ports and `from_*` handlers to capture output data.
- **History Assertions**: Generated classes maintain a history of port calls, telemetry, and events, allowing developers to assert that specific actions occurred in response to inputs.
- **STest Framework**: For complex components, the `STest` library provides a "Rule-based" testing approach. It allows developers to define `Rules` (with preconditions and actions) and `Scenarios` (e.g., `RandomScenario`) to explore the component's state space.

For details on writing and running unit tests, see [Unit Testing with GTest and STest](#9.1).

### Component Test Data Flow
The following diagram illustrates how the generated `Tester` class interacts with the Component Under Test (CUT).

**Diagram: Unit Test Harness Architecture**
```mermaid
graph LR
    subgraph "Test_Space"["Test Space"]
        "Tester.cpp" -- "calls" --> "invoke_to_Port"
        "Tester.cpp" -- "asserts" --> "History"
    end

    subgraph "Autocoded_Space"["Autocoded Space"]
        "GTestBase" -- "dispatches" --> "Component_Port_Handler"
        "Component_GTestBase" -- "records" --> "History"
    end

    subgraph "Code_Space"["Code Space"]
        "Component_Port_Handler" -- "executes" --> "Component.cpp_logic"["Component.cpp logic"]
        "Component.cpp_logic" -- "emits" --> "Output_Port"
    end

    "invoke_to_Port" --> "Component_Port_Handler"
    "Output_Port" --> "Component_GTestBase"
```
Sources: [Fw/Obj/CMakeLists.txt:1-10]() (General build structure)

## FppTestProject: Autocoder Validation

The `FppTestProject` is a specialized test suite within the F´ repository dedicated to validating the FPP autocoder itself. It ensures that the C++ code generated from FPP models is correct across a wide variety of edge cases and language features.

- **Coverage**: Tests include arrays, enums, structs, and complex component interactions.
- **State Machines**: Validates both internal and external state machine implementations generated from FPP.
- **Typed Tests**: Uses C++ templates to run the same logic across different data types and configurations.
- **Execution**: These tests are triggered via `fprime-util generate --ut` and `fprime-util check` within the `FppTestProject` directory [.github/workflows/fpp-tests.yml:33-47]().

For details on the FPP validation suite, see [FppTestProject: FPP Autocoder Validation](#9.2).

## CI/CD Pipelines and Docker

F´ utilizes GitHub Actions to maintain high code quality and ensure cross-platform compatibility. Every pull request triggers a suite of workflows that build the framework, run unit tests, and perform static analysis.

- **Build and Test**: Workflows for `ubuntu-22.04` and `macos-latest` execute `./ci/tests/Framework.bash` and `./ci/tests/Ref.bash` [.github/workflows/build-test.yml:25-64](), [.github/workflows/build-test-macos.yml:25-77]().
- **Static Analysis**: Integration of `cppcheck` [.github/workflows/cppcheck-scan.yml:21-81](), `cpplint` [.github/workflows/cpplint-scan.yml:20-75](), and `CodeQL` [.github/workflows/codeql-security-scan.yml:23-60]() to identify security vulnerabilities and style violations.
- **Cross-Compilation**: Automated validation of the Raspberry Pi and AArch64 Linux deployments using `fprime-util generate raspberrypi` [.github/workflows/ext-raspberry-led-blinker.yml:55-61]() and `fprime-util generate aarch64-linux` [.github/workflows/ext-aarch64-linux-led-blinker.yml:61-66]().
- **Integration Tests**: System-level tests using `pytest` and the GDS Integration Test API against running deployments, often wrapped in `valgrind` for memory leak detection [ci/tests/fputil.bash:78-90](), [.github/workflows/ext-aarch64-linux-led-blinker.yml:98-107]().

For details on pipeline configuration and the Docker environment, see [CI/CD Pipelines and Docker](#9.3).

### CI Workflow Relationships
This diagram maps the CI workflow entities to the scripts and tools they execute.

**Diagram: CI Pipeline Execution**
```mermaid
graph TD
    subgraph "GitHub_Actions"["GitHub Actions"]
        ".github/workflows/build-test.yml" --> "Job:Framework"["Job: Framework"]
        ".github/workflows/cppcheck-scan.yml" --> "Job:cppcheck"["Job: cppcheck"]
        ".github/workflows/python-format.yml" --> "Job:format"["Job: format"]
    end

    subgraph "Scripts_Tools"["Scripts & Tools"]
        "Job:Framework" -- "executes" --> "ci/tests/Framework.bash"
        "Job:cppcheck" -- "calls" --> "fprime-util_generate"["fprime-util generate"]
        "Job:cppcheck" -- "runs" --> "cppcheck"
        "Job:format" -- "runs" --> "black"
    end

    subgraph "Results"
        "ci/tests/Framework.bash" -- "produces" --> "ci-logs.tar.gz"
        "cppcheck" -- "produces" --> "cppcheck_err.sarif"
    end
```
Sources: [.github/workflows/build-test.yml:34-42](), [.github/workflows/cppcheck-scan.yml:46-60](), [.github/workflows/python-format.yml:24-27]()

## Testing Infrastructure Summary

| Layer | Tool/Framework | Purpose | Execution Command |
|---|---|---|---|
| **Unit** | GTest / STest | Component logic & state transitions | `fprime-util check` |
| **Autocoder** | FppTestProject | FPP to C++ correctness | `fprime-util check` in `FppTestProject/` |
| **Static** | CppCheck / CodeQL | Security & bug detection | Automated in CI |
| **Integration** | Pytest / GDS API | System-level interaction | `pytest ./int/` |
| **Memory** | Valgrind | Leak and memory error detection | `valgrind --tool=memcheck` [ci/tests/fputil.bash:78-85]() |

Sources: [.github/workflows/build-test.yml:1-112](), [.github/workflows/cppcheck-scan.yml:1-81](), [.github/workflows/ext-raspberry-led-blinker.yml:1-114](), [ci/tests/fputil.bash:75-90]()
