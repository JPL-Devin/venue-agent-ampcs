# Page: Documentation Generation

# Documentation Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Doxyfile](Doxyfile)
- [docs/_static/css/rtd_width.css](docs/_static/css/rtd_width.css)
- [docs/conf.py](docs/conf.py)
- [docs/gendoc.bash](docs/gendoc.bash)
- [docs/index.rst](docs/index.rst)

</details>



The `fprime-gds` documentation system utilizes a multi-tiered approach to generate technical references for both developers and end-users. It combines **Sphinx** for high-level documentation and Python API references with **Doxygen** for cross-language source code analysis. The system is designed to automatically extract metadata from the Python package and generate a searchable, indexed web interface.

## Documentation Architecture

The documentation generation process flows from the source code and package metadata into a unified HTML output. Sphinx acts as the primary orchestrator, using extensions to parse Python docstrings and Markdown files.

### Documentation Data Flow

The following diagram illustrates how source files and metadata are transformed into the final documentation suite.

**Documentation Build Pipeline**
```mermaid
graph TD
    subgraph "Input Space"
        [src_dir] -- "Python Source" --> [Sphinx_AutoAPI]
        [Package_Metadata] -- "importlib.metadata" --> [conf_py]
        [MD_RST_Files] -- "Manual Docs" --> [Sphinx_Builder]
    end

    subgraph "Processing Space"
        [conf_py] -- "Configuration" --> [Sphinx_Builder]
        [Sphinx_AutoAPI] -- "AST Parsing" --> [Sphinx_Builder]
        [Doxyfile] -- "Source Scan" --> [Doxygen_Engine]
    end

    subgraph "Output Space"
        [Sphinx_Builder] -- "HTML/CSS" --> [HTML_Docs]
        [Doxygen_Engine] -- "XML/HTML" --> [Doxy_Output]
    end

    [HTML_Docs] -- "Published to" --> [UsersGuide]
```
Sources: `docs/conf.py:24-51`(), `docs/gendoc.bash:4-7`(), `Doxyfile:56-61`()

## Sphinx Configuration

The Sphinx configuration is managed in `docs/conf.py`. It dynamically extracts project information (name, version, author) directly from the `fprime-gds` package metadata using `importlib.metadata` [docs/conf.py:17-32]().

### Key Extensions
Sphinx is configured with several powerful extensions to handle the diverse needs of the GDS documentation:
*   **`autoapi.extension`**: Automatically generates API documentation by scanning the `src` directory, eliminating the need for manual `rst` stubs for every module [docs/conf.py:47-93]().
*   **`sphinx.ext.napoleon`**: Enables support for Google-style and NumPy-style docstrings [docs/conf.py:45]().
*   **`recommonmark`**: Allows documentation to be written in Markdown (`.md`) in addition to reStructuredText (`.rst`) [docs/conf.py:48-56]().
*   **`sphinxcontrib.mermaid`**: Renders Mermaid diagrams directly within the documentation pages [docs/conf.py:50]().

### UI Customization
The documentation uses the `sphinx_rtd_theme` (Read the Docs theme) [docs/conf.py:72](). A custom CSS override is applied via `docs/_static/css/rtd_width.css` to remove the default maximum width constraints, allowing tables and large diagrams to render across the full screen [docs/_static/css/rtd_width.css:6-18]().

Sources: `docs/conf.py:37-51`(), `docs/conf.py:72-77`(), `docs/_static/css/rtd_width.css:1-20`()

## Doxygen Configuration

The `Doxyfile` provides a secondary documentation path, primarily used for deep source analysis. It is configured to output documentation into `./docs/doxy` [Doxyfile:61]().

| Setting | Value | Description |
| :--- | :--- | :--- |
| `PROJECT_NAME` | "My Project" | Identifier for the generated docs [Doxyfile:35]() |
| `OUTPUT_DIRECTORY` | `./docs/doxy` | Target path for Doxygen output [Doxyfile:61]() |
| `FULL_PATH_NAMES` | `YES` | Prepends full paths to files in listings [Doxyfile:143]() |
| `BRIEF_MEMBER_DESC` | `YES` | Includes brief descriptions in class listings [Doxyfile:101]() |

Sources: `Doxyfile:1-150`()

## Integration Test API Documentation

A significant portion of the documentation focuses on the `IntegrationTestAPI` (the "testAPI"). This documentation is structured to support developers writing GDS integration tests.

### Structure and Generation
The documentation for the test API is generated using the `autoapi` plugin, which points to the `src` directory [docs/conf.py:92](). The entry point for the documentation is `docs/index.rst`, which defines the top-level Table of Contents [docs/index.rst:16-19]().

**Test API Documentation Entity Mapping**
```mermaid
graph LR
    subgraph "Code Entities (src/fprime_gds/)"
        [IntegrationTestAPI] --> [common/testing_fw/api.py]
        [History_Classes] --> [common/history/]
        [Predicates] --> [common/testing_fw/predicates.py]
    end

    subgraph "Documentation Entities"
        [API_Index] --> [docs/index.rst]
        [Auto_Generated_API] --> [docs/api/index.rst]
    end

    [common/testing_fw/api.py] -- "Parsed by AutoAPI" --> [docs/api/index.rst]
```
Sources: `docs/conf.py:91-93`(), `docs/index.rst:1-28`()

## Build Execution

The documentation build is triggered via `docs/gendoc.bash`. This script:
1.  Defines the target directory: `../../docs/UsersGuide/api/python/fprime-gds/html` [docs/gendoc.bash:4]().
2.  Ensures the output directory exists [docs/gendoc.bash:5]().
3.  Executes `sphinx-build` using the current directory as the source [docs/gendoc.bash:7]().

Sources: `docs/gendoc.bash:1-8`()
