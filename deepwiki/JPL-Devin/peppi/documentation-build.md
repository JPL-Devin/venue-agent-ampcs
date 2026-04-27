# Page: Documentation Build

# Documentation Build

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [DOCUMENTATION_UPDATES.md](DOCUMENTATION_UPDATES.md)
- [docs/source/conf.py](docs/source/conf.py)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/reference.rst](docs/source/reference.rst)
- [sonar-project.properties](sonar-project.properties)
- [tox.ini](tox.ini)

</details>



The documentation for `pds.peppi` is built using **Sphinx**, utilizing the **Read the Docs (RTD)** theme to provide a navigable, professional interface for both researchers and developers. The build process is automated via `tox` and integrates `autodoc` to generate API references directly from the source code.

## Sphinx Configuration

The primary configuration for the documentation engine is located in `docs/source/conf.py`. It establishes the project identity, enables necessary extensions, and configures the visual theme.

### Key Extensions
The project uses several standard Sphinx extensions to bridge the gap between human-readable prose and the Python codebase:
*   `sphinx.ext.autodoc`: Automatically pulls docstrings from the source code into the documentation [docs/source/conf.py:29-29]().
*   `sphinx.ext.autosummary`: Generates summary tables for functions and classes [docs/source/conf.py:34-34]().
*   `sphinx.ext.viewcode`: Adds links to the highlighted source code for documented entities [docs/source/conf.py:32-32]().
*   `sphinx.ext.doctest`: Allows for testing code snippets within the documentation [docs/source/conf.py:30-30]().

### Theme and UI Configuration
The documentation uses the `sphinx_rtd_theme` [docs/source/conf.py:48-48](). Customizations include:
*   **Logo**: A PDS-specific logo is defined at `_static/images/PDS_Planets.png` [docs/source/conf.py:57-57]().
*   **CSS Overrides**: Custom styling is applied via `theme_overrides.css` [docs/source/conf.py:66-68]().
*   **GitHub Integration**: The `html_context` is configured to show "Edit on GitHub" links pointing to the `nasa-pds/peppi` repository [docs/source/conf.py:59-64]().

**Sources:**
* [docs/source/conf.py:1-81]()

---

## Source Structure (RST)

The documentation source is organized into a four-tiered hierarchy designed to cater to different user skill levels, from planetary scientists to data engineers [DOCUMENTATION_UPDATES.md:15-20]().

### Documentation Tiers

| Tier | File | Description |
| :--- | :--- | :--- |
| **Getting Started** | `getting_started.rst` | Beginner-friendly introduction and installation [DOCUMENTATION_UPDATES.md:24-35](). |
| **User Guide** | `user_guide.rst` | Conceptual explanations of PDS products and query building [DOCUMENTATION_UPDATES.md:37-51](). |
| **Cookbook** | `cookbook.rst` | 20 practical, copy-paste recipes for common tasks [DOCUMENTATION_UPDATES.md:53-91](). |
| **Reference** | `reference.rst` | Auto-generated API documentation using `automodule` [docs/source/reference.rst:1-36](). |

### Reference Mapping (Natural Language to Code)

The `reference.rst` file maps logical library components to their specific implementation modules.

| Logic Name | Code Entity | Implementation File |
| :--- | :--- | :--- |
| Registry Client | `PDSRegistryClient` | `pds/peppi/client.py` |
| Product Querying | `Products` | `pds/peppi/products.py` |
| Fluent Interface | `QueryBuilder` | `pds/peppi/query_builder.py` |
| Result Engine | `ResultSet` | `pds/peppi/result_set.py` |
| OSIRIS-REx Support | `OrexProducts` | `pds/peppi/orex/products.py` |

**Sources:**
* [docs/source/reference.rst:1-36]()
* [DOCUMENTATION_UPDATES.md:15-91]()

---

## Build Pipeline (tox)

The documentation build is managed by `tox` to ensure a consistent environment. The `docs` environment is defined to use Python 3.12 and installs the `dev` extras, which include Sphinx and the RTD theme [tox.ini:12-16]().

### Build Data Flow

The following diagram illustrates how the build environment transforms source code and RST files into the final HTML output.

**Documentation Build Flow**
```mermaid
graph TD
    subgraph "Environment: tox -e docs"
        "Source_Code"["src/pds/peppi/"]
        "RST_Files"["docs/source/*.rst"]
        "Conf"["docs/source/conf.py"]
    end

    subgraph "Sphinx Build Process"
        "Autodoc"["sphinx.ext.autodoc"]
        "RTD_Theme"["sphinx_rtd_theme"]
        "HTML_Builder"["Sphinx HTML Builder"]
    end

    "Source_Code" --> "Autodoc"
    "RST_Files" --> "HTML_Builder"
    "Conf" --> "HTML_Builder"
    "Autodoc" --> "HTML_Builder"
    "RTD_Theme" --> "HTML_Builder"

    "HTML_Builder" --> "Build_Output"["docs/build/html/"]
```

### Build Command
The specific command executed by tox is:
`sphinx-build -b html docs/source docs/build` [tox.ini:16-16]().

**Sources:**
* [tox.ini:12-16]()

---

## API Reference Generation

The `reference.rst` file uses Sphinx directives to inspect the codebase and generate documentation. This ensures that the documentation stays in sync with the actual implementation.

**Entity Association Diagram**
```mermaid
graph LR
    subgraph "Natural Language Concepts"
        "C1"["Registry Connectivity"]
        "C2"["Product Search"]
        "C3"["Mission Specialization"]
    end

    subgraph "Code Entity Space"
        "E1"["PDSRegistryClient"]
        "E2"["QueryBuilder"]
        "E3"["OrexProducts"]
    end

    subgraph "Documentation Directives"
        "D1"[".. automodule:: pds.peppi.client"]
        "D2"[".. automodule:: pds.peppi.query_builder"]
        "D3"[".. automodule:: pds.peppi.orex.products"]
    end

    "C1" --- "E1"
    "C2" --- "E2"
    "C3" --- "E3"

    "E1" --- "D1"
    "E2" --- "D2"
    "E3" --- "D3"
```

The reference structure covers the following modules:
1.  **Client**: `pds.peppi.client` for the `PDSRegistryClient` [docs/source/reference.rst:9-11]().
2.  **Products**: `pds.peppi.products` for the `Products` wrapper [docs/source/reference.rst:13-16]().
3.  **Query Builder**: `pds.peppi.query_builder` for the `QueryBuilder` logic [docs/source/reference.rst:18-20]().
4.  **Result Set**: `pds.peppi.result_set` for pagination handling [docs/source/reference.rst:22-25]().
5.  **OREX**: Specialized OSIRIS-REx modules at `pds.peppi.orex.products` and `pds.peppi.orex.result_set` [docs/source/reference.rst:27-35]().

**Sources:**
* [docs/source/reference.rst:7-36]()
* [DOCUMENTATION_UPDATES.md:139-148]()
