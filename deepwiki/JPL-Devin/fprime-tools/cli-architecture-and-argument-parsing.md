# Page: CLI Architecture and Argument Parsing

# CLI Architecture and Argument Parsing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/fprime/fbuild/cli.py](src/fprime/fbuild/cli.py)
- [src/fprime/util/__main__.py](src/fprime/util/__main__.py)
- [src/fprime/util/cli.py](src/fprime/util/cli.py)
- [src/fprime/util/commands.py](src/fprime/util/commands.py)
- [src/fprime/util/help_text.py](src/fprime/util/help_text.py)

</details>



The `fprime-util` CLI is the primary developer interface for the F´ ecosystem. It provides a unified entry point that abstracts the underlying build system (CMake/Ninja/Make), the FPP modeling toolchain, and various project scaffolding utilities. Its architecture is built around a hierarchical `argparse` structure that dynamically registers sub-parsers from different subsystems.

## Entrypoint and Execution Flow

The CLI execution begins at `fprime.util.__main__.main`, which delegates to `utility_entry` [src/fprime/util/__main__.py:13-15]().

### The `utility_entry` Pipeline
The `utility_entry` function manages the high-level lifecycle of a command execution [src/fprime/util/cli.py:32-57]():
1.  **Argument Parsing**: Calls `parse_args` to decompose `sys.argv` into structured namespaces and raw build system arguments.
2.  **Build Loading**: Unless the command is explicitly marked to skip loading (e.g., `version-check`), it initializes a `Build` object via `load_build` [src/fprime/util/cli.py:37-41]().
3.  **Dispatch**: Uses the `runners` dictionary to find the function associated with the parsed command and executes it [src/fprime/util/cli.py:44-46]().

### CLI Execution Logic
The following diagram illustrates the flow from the shell to the specific command runner.

**CLI Dispatch Flow**
```mermaid
graph TD
    "shell_invocation" --> "utility_entry()"
    "utility_entry()" --> "parse_args()"
    "parse_args()" --> "argparse_hierarchy"
    "utility_entry()" --> "load_build()"
    "load_build()" --> "Build_Object"
    "utility_entry()" --> "dispatch_to_runner"
    
    subgraph "Runners_Dict" [runners Dictionary]
        "dispatch_to_runner" -- "command=='build'" --> "run_fbuild_cli()"
        "dispatch_to_runner" -- "command=='new'" --> "run_new()"
        "dispatch_to_runner" -- "command=='impl'" --> "fpp_generate_implementation()"
    end

    subgraph "fprime_util_cli" [fprime.util.cli]
        "utility_entry()"
        "parse_args()"
    end
```
Sources: [src/fprime/util/cli.py:32-57](), [src/fprime/util/__main__.py:13-15]()

## Argument Parsing Hierarchy

`fprime-util` uses a complex `argparse` setup to handle three distinct types of arguments simultaneously:
1.  **Global Arguments**: Arguments like `-p/--path` or `-u/--ut` that apply to almost all commands.
2.  **Sub-command Arguments**: Arguments specific to a tool (e.g., `--overwrite` for `new`).
3.  **Pass-through Arguments**: Arguments intended for CMake or the underlying build tool (Make/Ninja), separated by `--`.

### Parser Registration
The `parse_args` function constructs the parser by aggregating subparsers from different modules [src/fprime/util/cli.py:238-323]():
*   **`add_fbuild_parsers`**: Registers build-related targets (generate, build, check, etc.) [src/fprime/fbuild/cli.py:205-245]().
*   **`add_fpp_parsers`**: Registers FPP modeling tools (fpp-check, fpp-to-dict).
*   **`add_fpp_impl_parsers`**: Registers implementation template generation [src/fprime/util/cli.py:28]().
*   **`add_fpp_viz_parsers`**: Registers the visualization tool [src/fprime/util/cli.py:29]().
*   **`add_special_parsers`**: Registers utility commands like `info`, `new`, and `format` [src/fprime/util/cli.py:84-235]().

### The `validate()` Pattern
Many commands require a valid build cache to function. The CLI architecture handles this through conditional loading:
*   **`skip_build_loading`**: Commands like `version-check` do not require a `Build` object [src/fprime/util/cli.py:60-66]().
*   **`skip_build_cache_validation`**: Commands like `purge`, `info`, and `format` need a `Build` object but don't require the CMake cache to be valid/current [src/fprime/util/cli.py:69-81]().

Sources: [src/fprime/util/cli.py:32-81](), [src/fprime/util/cli.py:238-323]()

## HelpText System

To maintain consistent and detailed documentation, `fprime-util` uses a dedicated `HelpText` class [src/fprime/util/help_text.py:32-87](). 

The system maps command mnemonics to strings formatted for `argparse.RawDescriptionHelpFormatter`. Each entry in the `MNEMONIC_HELP_MAP` follows a specific convention:
*   **Short Help**: The first line of the string, used in the top-level `--help` summary [src/fprime/util/help_text.py:8-14]().
*   **Long Help**: The full string, including examples and detailed flag descriptions, shown when running `fprime-util <command> --help`.

**Code Entity to Help Association**
```mermaid
graph LR
    subgraph "HelpText_System" [fprime.util.help_text]
        "MNEMONIC_HELP_MAP" -- "key: 'build'" --> "Build_Description_String"
        "MNEMONIC_HELP_MAP" -- "key: 'impl'" --> "Impl_Description_String"
    end

    subgraph "CLI_Registration" [fprime.fbuild.cli]
        "add_target_parser()" -- "calls" --> "HelpText.short()"
        "add_target_parser()" -- "calls" --> "HelpText.long()"
    end

    "HelpText.short()" -- "extracts first line" --> "argparse.help"
    "HelpText.long()" -- "extracts full block" --> "argparse.description"
```
Sources: [src/fprime/util/help_text.py:1-31](), [src/fprime/fbuild/cli.py:135-172]()

## Runners and Dispatching

The `runners` dictionary is the core dispatch mechanism. It maps command names to callable functions that implement the logic.

| Command | Runner Function | Source |
| :--- | :--- | :--- |
| `build`, `generate`, `purge` | `run_fbuild_cli` | [src/fprime/fbuild/cli.py:38]() |
| `info` | `run_info` | [src/fprime/util/commands.py:35]() |
| `new` | `run_new` | [src/fprime/util/commands.py:126]() |
| `format` | `run_code_format` | [src/fprime/util/commands.py:151]() |
| `hash-to-file` | `run_hash_to_file` | [src/fprime/util/commands.py:103]() |
| `version-check` | `run_version_check` | [src/fprime/util/commands.py:226]() |

### Target-Based Dispatch (fbuild)
For build commands, the dispatch is further refined by the `Target` system. `run_fbuild_cli` uses `get_target(parsed)` to identify the specific `Target` class (e.g., `BuildTarget`, `CheckTarget`) based on the command mnemonic and active flags (like `--ut`) [src/fprime/fbuild/cli.py:20-35]().

Sources: [src/fprime/util/cli.py:43-46](), [src/fprime/fbuild/cli.py:38-52](), [src/fprime/util/commands.py:1-12]()
