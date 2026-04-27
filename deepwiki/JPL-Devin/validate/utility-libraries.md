# Page: Utility Libraries

# Utility Libraries

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/main/java/gov/nasa/pds/tools/label/validate/DefaultDocumentValidator.java](src/main/java/gov/nasa/pds/tools/label/validate/DefaultDocumentValidator.java)
- [src/main/java/gov/nasa/pds/tools/label/validate/DocumentValidator.java](src/main/java/gov/nasa/pds/tools/label/validate/DocumentValidator.java)
- [src/main/java/gov/nasa/pds/tools/util/LabelParser.java](src/main/java/gov/nasa/pds/tools/util/LabelParser.java)
- [src/main/java/gov/nasa/pds/tools/util/Utility.java](src/main/java/gov/nasa/pds/tools/util/Utility.java)
- [src/main/java/gov/nasa/pds/tools/util/XMLErrorListener.java](src/main/java/gov/nasa/pds/tools/util/XMLErrorListener.java)
- [src/main/java/gov/nasa/pds/tools/util/XMLExtractor.java](src/main/java/gov/nasa/pds/tools/util/XMLExtractor.java)
- [src/main/java/gov/nasa/pds/tools/util/XslURIResolver.java](src/main/java/gov/nasa/pds/tools/util/XslURIResolver.java)
- [src/main/java/gov/nasa/pds/tools/validate/ContentProblem.java](src/main/java/gov/nasa/pds/tools/validate/ContentProblem.java)
- [src/main/java/gov/nasa/pds/tools/validate/ValidationProblem.java](src/main/java/gov/nasa/pds/tools/validate/ValidationProblem.java)
- [src/main/java/gov/nasa/pds/tools/validate/ValidationTarget.java](src/main/java/gov/nasa/pds/tools/validate/ValidationTarget.java)
- [src/main/java/gov/nasa/pds/tools/validate/content/table/InventoryTableValidator.java](src/main/java/gov/nasa/pds/tools/validate/content/table/InventoryTableValidator.java)
- [src/main/java/gov/nasa/pds/validate/constants/Constants.java](src/main/java/gov/nasa/pds/validate/constants/Constants.java)
- [src/main/java/gov/nasa/pds/validate/ri/UserInput.java](src/main/java/gov/nasa/pds/validate/ri/UserInput.java)
- [src/test/resources/github476/bundle_mars2020_spice_v003.xml](src/test/resources/github476/bundle_mars2020_spice_v003.xml)
- [src/test/resources/github476/readme.txt](src/test/resources/github476/readme.txt)
- [src/test/timing_metrics.sh](src/test/timing_metrics.sh)

</details>



The `validate` tool relies on a robust set of utility libraries to handle common tasks such as XML extraction, file system operations, PDS4 label parsing, and data format validation. These utilities are primarily located in the `gov.nasa.pds.tools.util` and `gov.nasa.pds.validate.util` packages.

### Overview of Utility Categories

The utility ecosystem is divided into three primary functional areas:

1.  **XML and Label Utilities**: Classes designed for querying PDS4 labels via XPath, transforming Schematron files into XSLT, and managing XML parsing errors.
2.  **Data Format and File Utilities**: Helpers for calculating file sizes, verifying MD5 checksums, mapping MIME types, and performing content-specific checks on images or PDFs.
3.  **Inventory and User Input Utilities**: Specialized readers for PDS4 Collection inventories and CLI input processors that resolve LIDVIDs from labels or manifest files.

### Core Utility Interactions

The following diagram illustrates how core utility classes bridge the gap between raw file system/URL resources and the high-level validation logic used by the tool.

**Utility Entity Relationship**
```mermaid
graph TD
    subgraph "Natural Language Space"
        "Label Querying"["Label Querying"]
        "File Operations"["File Operations"]
        "MIME Mapping"["MIME Mapping"]
        "Input Resolution"["Input Resolution"]
    end

    subgraph "Code Entity Space"
        "XMLExtractor"["XMLExtractor"]
        "MimeTable"["MimeTable"]
        "UserInput"["UserInput"]
        "LabelParser"["LabelParser"]
        "Utility"["Utility"]
    end

    "Label Querying" --> "XMLExtractor"
    "MIME Mapping" --> "MimeTable"
    "Input Resolution" --> "UserInput"
    "File Operations" --> "LabelParser"
    "File Operations" --> "Utility"

    "XMLExtractor" -- "uses" --> "net.sf.saxon.xpath.XPathEvaluator"
    "UserInput" -- "uses" --> "LabelParser"
    "UserInput" -- "uses" --> "XMLExtractor"
    "LabelParser" -- "uses" --> "Utility"
    "MimeTable" -- "reads" --> "validate_default_mime_types.txt"
```
**Sources:** [src/main/java/gov/nasa/pds/tools/util/XMLExtractor.java:38-43](), [src/main/java/gov/nasa/pds/validate/ri/UserInput.java:21-58](), [src/main/java/gov/nasa/pds/tools/util/LabelParser.java:46-46](), [src/main/java/gov/nasa/pds/tools/util/Utility.java:43-60]().

---

### 6.1 XML and Label Utilities
The XML utility suite provides the backbone for PDS4 metadata extraction. Central to this is the `XMLExtractor`, which wraps the Saxon `XPathEvaluator` to provide simplified access to label elements [src/main/java/gov/nasa/pds/tools/util/XMLExtractor.java:43-64](). It handles namespace resolution and XInclude support by querying the `Utility.supportXincludes()` configuration [src/main/java/gov/nasa/pds/tools/util/XMLExtractor.java:68-70]().

Key components include:
*   **XMLExtractor**: Evaluates XPath expressions against XML sources [src/main/java/gov/nasa/pds/tools/util/XMLExtractor.java:140-145](). It can be initialized from a `Source`, `URL`, `File`, or `InputSource` [src/main/java/gov/nasa/pds/tools/util/XMLExtractor.java:62-128]().
*   **LabelParser**: A utility to parse XML into a Saxon `TreeInfo` object while optionally ignoring errors via a custom `ErrorReporter` [src/main/java/gov/nasa/pds/tools/util/LabelParser.java:26-51]().
*   **XMLErrorListener**: Implements both `ErrorListener` and `ErrorHandler` to catch and rethrow parsing exceptions during XML processing [src/main/java/gov/nasa/pds/tools/util/XMLErrorListener.java:28-38]().
*   **XslURIResolver**: Manages the resolution of imports within XSLT and Schematron files, specifically looking within the tool's JAR resources.
*   **InventoryTableValidator**: A specialized utility that uses `XMLExtractor` and `InventoryTableReader` to ensure unique LID/LIDVID references within Bundle and Collection aggregates [src/main/java/gov/nasa/pds/tools/validate/content/table/InventoryTableValidator.java:22-60]().

For details, see [XML and Label Utilities](#6.1).

### 6.2 Data Format and File Utilities
These utilities handle physical file attributes and non-XML data formats. They bridge the gap between PDS4 label definitions (like `document_standard_id`) and actual file extensions or MIME types. The `Utility` class provides low-level network and file system helpers, including SSL hostname verification for `pds.nasa.gov` and redirect handling for URL connections [src/main/java/gov/nasa/pds/tools/util/Utility.java:48-75]().

**Data Mapping Logic**
```mermaid
graph LR
    subgraph "Code Entity Space"
        "MimeTable"["MimeTable"]
        "DocumentsChecker"["DocumentsChecker"]
        "Constants"["Constants"]
        "Utility"["Utility"]
    end

    "DocumentsChecker" -- "calls" --> "MimeTable"
    "MimeTable" -- "loads" --> "validate_default_mime_types.txt"
    "Constants" -- "provides" --> "BUNDLE_LABEL_PATTERN_STRING"
    "Constants" -- "defines" --> "ALLOWABLE_LABEL_EXTENSIONS"
    "Utility" -- "provides" --> "openConnection"
    "Utility" -- "provides" --> "toURL"
```
**Sources:** [src/main/java/gov/nasa/pds/tools/util/Utility.java:69-125](), [src/main/java/gov/nasa/pds/validate/constants/Constants.java:45-50]().

Key components include:
*   **Utility**: General-purpose helpers for URL normalization, directory detection, and opening streams with TLS 1.2 support [src/main/java/gov/nasa/pds/tools/util/Utility.java:69-156]().
*   **MimeTable**: Encapsulates a mapping of MIME types to file extensions.
*   **Constants**: Centralized repository for regex patterns used to identify bundle/collection labels and valid XML extensions (`.xml`, `.lblx`) [src/main/java/gov/nasa/pds/validate/constants/Constants.java:36-52]().
*   **DefaultDocumentValidator**: Implements `DocumentValidator` to perform semantic checks on labels, such as verifying Schematron `schematypens` attributes using `XMLExtractor` and checking against `Constants.SCHEMATRON_SCHEMATYPENS_PATTERN` [src/main/java/gov/nasa/pds/tools/label/validate/DefaultDocumentValidator.java:40-71]().

For details, see [Data Format and File Utilities](#6.2).

### 6.3 User Input and Manifest Utilities
The `UserInput` utility is specifically designed to resolve logical identifiers (LIDs) or LIDVIDs from various input types provided during validation, such as direct LIDVID strings, label files, or manifest files.

Key components include:
*   **UserInput**: Processes CLI arguments to expand manifests or extract LIDVIDs from labels using `LabelParser` and `XMLExtractor` [src/main/java/gov/nasa/pds/validate/ri/UserInput.java:21-58]().
*   **LIDVID Extraction**: Specifically targets the `//logical_identifier` node within a label to identify the product during the referential integrity workflow [src/main/java/gov/nasa/pds/validate/ri/UserInput.java:48-49]().

---
**Sources:**
* [src/main/java/gov/nasa/pds/tools/util/Utility.java]()
* [src/main/java/gov/nasa/pds/tools/util/XMLExtractor.java]()
* [src/main/java/gov/nasa/pds/tools/util/LabelParser.java]()
* [src/main/java/gov/nasa/pds/tools/util/XMLErrorListener.java]()
* [src/main/java/gov/nasa/pds/tools/validate/content/table/InventoryTableValidator.java]()
* [src/main/java/gov/nasa/pds/validate/constants/Constants.java]()
* [src/main/java/gov/nasa/pds/tools/label/validate/DefaultDocumentValidator.java]()
* [src/main/java/gov/nasa/pds/validate/ri/UserInput.java]()
