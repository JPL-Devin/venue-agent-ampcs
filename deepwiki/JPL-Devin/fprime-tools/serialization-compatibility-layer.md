# Page: Serialization Compatibility Layer

# Serialization Compatibility Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/fprime/common/models/serialize/array_type.py](src/fprime/common/models/serialize/array_type.py)
- [src/fprime/common/models/serialize/serializable_type.py](src/fprime/common/models/serialize/serializable_type.py)
- [src/fprime/common/models/serialize/string_type.py](src/fprime/common/models/serialize/string_type.py)
- [src/fprime/common/models/serialize/time_type.py](src/fprime/common/models/serialize/time_type.py)
- [src/fprime/common/models/serialize/type_base.py](src/fprime/common/models/serialize/type_base.py)

</details>



The `fprime.common.models.serialize` package serves as a backward-compatibility shim for the F´ serialization type system. Historically, these serialization models were part of the core `fprime-tools` repository, but they have since been migrated to the `fprime-gds` package to better align with their primary use case: Ground Data System telemetry and command processing.

This layer ensures that legacy code and existing F´ projects can still import types like `ArrayType`, `SerializableType`, and `TimeType` from their original namespaces without immediate failure, while providing a clear migration path via deprecation warnings.

### Architectural Role: The Redirect Shim

The package functions by intercepting imports and redirecting them to the corresponding modules in `fprime_gds.common.models.serialize`. Each module in this package follows a standard pattern:
1.  Emit a `DeprecationWarning` indicating the new location of the class.
2.  Attempt to import the class from `fprime-gds`.
3.  Raise a descriptive `ImportError` if `fprime-gds` is not installed, guiding the user to install the necessary dependency.

#### Serialization Shim Logic Flow
The following diagram illustrates how an import request for a legacy serialization type is handled by the compatibility layer.

**Diagram: Import Redirection Pipeline**
```mermaid
graph TD
    "User_Code" -- "import fprime.common.models.serialize.time_type" --> "Shim_Module[time_type.py]"
    subgraph "fprime-tools Shim"
        "Shim_Module[time_type.py]" --> "Warn[Emit DeprecationWarning]"
        "Warn[Emit DeprecationWarning]" --> "Try_Import{Try Import from fprime_gds}"
    end
    "Try_Import{Try Import from fprime_gds}" -- "Success" --> "Return_Entity[Return TimeType]"
    "Try_Import{Try Import from fprime_gds}" -- "Failure" --> "Raise_Error[Raise ImportError with Guidance]"
    "Return_Entity[Return TimeType]" --> "User_Code"
```
Sources: [src/fprime/common/models/serialize/time_type.py:20-36](), [src/fprime/common/models/serialize/array_type.py:7-23]()

---

### Type System and Primitive Types
The serialization framework is built upon a hierarchy of types that define how data is packed and unpacked for flight software communication. This includes base classes for all serializable entities, numerical types (integers and floats), and complex structures.

The core of this system is defined in `type_base.py`, which provides the `BaseType`, `ValueType`, and `DictionaryType` abstractions. These classes define the interface for `serialize()` and `deserialize()` operations used throughout the GDS.

For a detailed breakdown of the type hierarchy and primitive definitions, see **[Type System and Primitive Types](#6.1)**.

Sources: [src/fprime/common/models/serialize/type_base.py:16-21]()

---

### GDS Migration Shims
The migration shims cover the primary complex types used in F´ modeling. Each major type has a dedicated shim file that mirrors the structure of the `fprime-gds` package.

| Legacy Module | Redirected Entity | GDS Destination |
|---|---|---|
| `array_type.py` | `ArrayType` | `fprime_gds.common.models.serialize.array_type` |
| `serializable_type.py` | `SerializableType` | `fprime_gds.common.models.serialize.serializable_type` |
| `time_type.py` | `TimeType` | `fprime_gds.common.models.serialize.time_type` |
| `string_type.py` | `StringType` | `fprime_gds.common.models.serialize.string_type` |

These shims ensure that even as the architectural split between "tools" and "GDS" matures, existing autocoded files and manual scripts remain functional.

For details on the implementation of these proxies and the rationale for the package split, see **[GDS Migration Shims: ArrayType, SerializableType, TimeType, StringType](#6.2)**.

#### Entity Mapping
The following diagram maps the shim files in `fprime-tools` to the actual implementation entities they proxy.

**Diagram: Code Entity Proxy Mapping**
```mermaid
classDiagram
    class "fprime.common.models.serialize.array_type" {
        <<module>>
        +ArrayType
    }
    class "fprime.common.models.serialize.time_type" {
        <<module>>
        +TimeType
    }
    class "fprime.common.models.serialize.type_base" {
        <<module>>
        +BaseType
        +ValueType
        +DictionaryType
    }
    
    "fprime.common.models.serialize.array_type" ..> "fprime_gds.common.models.serialize.array_type" : proxies
    "fprime.common.models.serialize.time_type" ..> "fprime_gds.common.models.serialize.time_type" : proxies
    "fprime.common.models.serialize.type_base" ..> "fprime_gds.common.models.serialize.type_base" : proxies
```
Sources: [src/fprime/common/models/serialize/array_type.py:17-17](), [src/fprime/common/models/serialize/time_type.py:30-30](), [src/fprime/common/models/serialize/type_base.py:17-21](), [src/fprime/common/models/serialize/serializable_type.py:18-18](), [src/fprime/common/models/serialize/string_type.py:18-18]()
