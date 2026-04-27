# Page: Sequence Generation & Data Products

# Sequence Generation & Data Products

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/fprime_gds/common/encoders/seq_writer.py](src/fprime_gds/common/encoders/seq_writer.py)
- [src/fprime_gds/common/parsers/seq_file_parser.py](src/fprime_gds/common/parsers/seq_file_parser.py)
- [src/fprime_gds/common/tools/seqgen.py](src/fprime_gds/common/tools/seqgen.py)
- [src/fprime_gds/executables/data_products.py](src/fprime_gds/executables/data_products.py)

</details>



This page provides a high-level overview of the tools and libraries within the F´ GDS used to generate command sequences and process data products. These tools bridge the gap between human-readable text/JSON definitions and the binary formats required by flight software.

## Overview

The F´ GDS provides two primary specialized data handling pipelines:
1.  **Sequence Generation**: Converting human-readable `.seq` files into binary `.bin` files for the `Svc/CmdSequencer` component.
2.  **Data Products**: Decoding and validating binary `.fdp` files produced by the `Svc/DataProduct` system into structured JSON or human-readable formats.

Both systems rely on the GDS dictionary system to resolve mnemonics, IDs, and data types.

### System Data Flow

The following diagram illustrates how these tools interact with the GDS core and flight software artifacts.

**Sequence and Data Product Toolchain**
```mermaid
graph LR
    subgraph "Sequence Generation"
        "Input.seq"["Input .seq File"] --> "SeqFileParser"["SeqFileParser"]
        "Dictionary.json"["JSON Dictionary"] --> "SeqGen"["fprime-seqgen"]
        "SeqFileParser" --> "SeqGen"
        "SeqGen" --> "SeqBinaryWriter"["SeqBinaryWriter"]
        "SeqBinaryWriter" --> "Output.bin"["Binary Sequence (.bin)"]
    end

    subgraph "Data Product Handling"
        "Product.fdp"["Binary Product (.fdp)"] --> "DP_CLI"["fprime-dp"]
        "DP_CLI" --> "DP_Decoder"["DataProductDecoder"]
        "DP_CLI" --> "DP_Validator"["DataProductValidator"]
        "DP_Decoder" --> "Output.json"["Decoded JSON"]
    end

    "Output.bin" -.-> "FSW"["Flight Software"]
    "FSW" -.-> "Product.fdp"
```
Sources: [src/fprime_gds/common/tools/seqgen.py:44-121](), [src/fprime_gds/executables/data_products.py:8-44]()

---

## Sequence Generator (fprime-seqgen)

The `fprime-seqgen` tool (implemented in `seqgen.py`) is a compiler for F´ command sequences. It transforms a list of time-tagged commands in a text file into a packed binary format that the flight `CmdSequencer` can execute.

### Key Components
*   **SeqFileParser**: Processes `.seq` files, handling comments (`;`), relative (`R`) vs. absolute (`A`) time descriptors, and command arguments [src/fprime_gds/common/parsers/seq_file_parser.py:8-17]().
*   **generateSequence**: The core logic function that coordinates loading the `CmdJsonLoader`, parsing the input, and invoking the writer [src/fprime_gds/common/tools/seqgen.py:44-121]().
*   **SeqBinaryWriter**: Serializes the `CmdData` objects into the specific binary format, including sequence headers (size, record count, timebase) and a CRC32 checksum [src/fprime_gds/common/encoders/seq_writer.py:16-170]().

For detailed information on the sequence format, timebase configuration, and integration with the GDS Web UI, see the **[Sequence Generator (fprime-seqgen)](#9.1)** child page.

---

## Data Products (fprime-dp)

The `fprime-dp` tool provides utilities for managing Data Products—large sets of telemetry or science data captured on-board and downlinked as files.

### Key Components
*   **DataProductDecoder**: Uses the `Dictionaries` and `DpJsonLoader` to transform binary product files into structured JSON. It maps the product ID to a `DpRecordTemplate` to understand the internal record structure [src/fprime_gds/common/dp/decoder.py](), [src/fprime_gds/executables/data_products.py:32-32]().
*   **DataProductValidator**: Checks the integrity of `.fdp` files, specifically verifying the CRC and header consistency [src/fprime_gds/common/dp/validator.py](), [src/fprime_gds/executables/data_products.py:35-40]().
*   **CLI Interface**: Provides `decode` and `validate` sub-commands for manual or scripted data processing [src/fprime_gds/executables/data_products.py:10-22]().

For details on the `.fdp` file format, CRC validation logic, and decoding complex types, see the **[Data Products (fprime-dp)](#9.2)** child page.

---

## Tooling Relationships

The following table summarizes the primary classes and their roles in these two pipelines.

| Tool / Pipeline | Primary Class | Input Format | Output Format | Dictionary Dependency |
| :--- | :--- | :--- | :--- | :--- |
| **Sequence Gen** | `SeqBinaryWriter` [src/fprime_gds/common/encoders/seq_writer.py:16]() | `.seq` (Text) | `.bin` (Binary) | `CmdJsonLoader` |
| **DP Decoding** | `DataProductDecoder` [src/fprime_gds/common/dp/decoder.py]() | `.fdp` (Binary) | `.json` (Text) | `DpJsonLoader` |
| **DP Validation** | `DataProductValidator` [src/fprime_gds/common/dp/validator.py]() | `.fdp` (Binary) | Status Code | Optional |

### Code Mapping: Logic to Entities

This diagram maps the conceptual "Generation" and "Processing" tasks to the specific classes in the codebase.

**Logic to Code Entity Mapping**
```mermaid
classDiagram
    class "fprime-seqgen CLI" {
        +main()
        +generateSequence()
    }
    class "fprime-dp CLI" {
        +main()
    }
    
    "fprime-seqgen CLI" ..> "SeqFileParser" : uses
    "fprime-seqgen CLI" ..> "SeqBinaryWriter" : uses
    "fprime-seqgen CLI" ..> "CmdJsonLoader" : loads
    
    "fprime-dp CLI" ..> "DataProductDecoder" : uses
    "fprime-dp CLI" ..> "DataProductValidator" : uses
    "fprime-dp CLI" ..> "Dictionaries" : loads

    style "fprime-seqgen CLI" stroke-dasharray: 5 5
    style "fprime-dp CLI" stroke-dasharray: 5 5
```
Sources: [src/fprime_gds/common/tools/seqgen.py:152-181](), [src/fprime_gds/executables/data_products.py:8-44]()

---
**Next Steps:**
*   To learn how to write `.seq` files and compile them, visit **[Sequence Generator (fprime-seqgen)](#9.1)**.
*   To learn how to process science data products, visit **[Data Products (fprime-dp)](#9.2)**.
