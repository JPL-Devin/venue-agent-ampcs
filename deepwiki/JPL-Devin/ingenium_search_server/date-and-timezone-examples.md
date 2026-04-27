# Page: Date and Timezone Examples

# Date and Timezone Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [search_examples/date_example.py](search_examples/date_example.py)
- [search_examples/dynamic_mapping_example.py](search_examples/dynamic_mapping_example.py)
- [search_examples/timezone_example.py](search_examples/timezone_example.py)

</details>



This page details the implementation and behavior of date fields, dynamic mapping templates for time-based data, and timezone handling within the Ingenium Search Server ecosystem. These examples, located in the `search_examples/` directory, demonstrate how the system processes various temporal formats, handles null values, and executes range queries across different timezones.

### Date Field Mapping and Ingestion

The `date_example.py` script demonstrates the lifecycle of a date-typed field in Elasticsearch. It specifically explores the `date` type mapping and how the engine handles different input formats during document creation.

#### Implementation Details
*   **Explicit Mapping**: Fields intended for temporal data are explicitly mapped to the `date` type [search_examples/date_example.py:63-69]().
*   **ISO 8601 Support**: The system natively ingests standard ISO 8601 strings (e.g., `2023-06-26T19:39:35.947Z`) [search_examples/date_example.py:81-83]().
*   **Epoch Handling**: Numeric values are interpreted as milliseconds since the Linux epoch. For instance, providing `0` results in a valid date entry for January 1, 1970 [search_examples/date_example.py:127-131]().
*   **Null and Empty Handling**: 
    *   Passing an empty string (`""`) to a date field results in a `400 Bad Request` error as it cannot be parsed [search_examples/date_example.py:117-125]().
    *   Passing `None` (JSON `null`) is accepted; the field is simply not indexed for that document [search_examples/date_example.py:138-147]().

#### Range Query Logic
Range queries use `gte` (greater than or equal to) and `lt` (less than) operators to filter documents based on temporal windows [search_examples/date_example.py:164-172]().

**Date Ingestion Flow**

```mermaid
graph TD
    "InputData"["Input Data"] --> "Parser"["ES Date Parser"]
    "Parser" -- "ISO 8601 String" --> "IndexDoc"["Indexed Document"]
    "Parser" -- "Integer (0)" --> "EpochDoc"["Indexed as 1970-01-01"]
    "Parser" -- "null" --> "NoIndex"["Field Omitted from Index"]
    "Parser" -- "Empty String ''" --> "Error"["400 Bad Request"]

    subgraph "Code Entities"
        "search_examples/date_example.py:81-83"
        "search_examples/date_example.py:127-131"
        "search_examples/date_example.py:138-142"
        "search_examples/date_example.py:117-125"
    end
```
Sources: [search_examples/date_example.py:61-147](), [search_examples/date_example.py:161-178]()

### Dynamic Mapping Templates

The `dynamic_mapping_example.py` script illustrates how the server can automatically assign types to new fields based on naming patterns. This is critical for supporting diverse metadata without requiring manual schema updates for every new field.

#### Template Configurations
The system uses `dynamic_templates` to match field names to specific Elasticsearch types:

| Template Name | Match Pattern | Mapping Type | Purpose |
| :--- | :--- | :--- | :--- |
| `string_as_wildcard` | `match_mapping_type: string` | `wildcard` | Default fallback for all strings to support high-performance partial matching [search_examples/dynamic_mapping_example.py:74-80](). |
| `start_time` | `match: start_time` | `date` | Specific field name match [search_examples/dynamic_mapping_example.py:82-89](). |
| `time_prefix` | `match: time_*` | `date` | Matches any field starting with "time_" [search_examples/dynamic_mapping_example.py:91-98](). |
| `time_postfix` | `match: *_time` | `date` | Matches any field ending with "_time" [search_examples/dynamic_mapping_example.py:100-107](). |
| `scet` / `ert` | `match: scet` / `ert` | `date` | Spacecraft Event Time and Earth Received Time mapping [search_examples/dynamic_mapping_example.py:109-125](). |

Sources: [search_examples/dynamic_mapping_example.py:71-144]()

### Timezone Handling

The `timezone_example.py` script demonstrates how Elasticsearch resolves ambiguities in timezones and how the server queries across different offsets.

#### Key Behaviors
*   **Format Specification**: Using `strict_date_optional_time` allows for flexibility in the presence of time components and offsets [search_examples/timezone_example.py:65-69]().
*   **Implicit UTC**: If a timestamp is provided without a timezone designator (e.g., `2023-07-01T10:00:00.000`), it is treated as UTC by default [search_examples/timezone_example.py:93-94]().
*   **Offset Handling**: Numeric offsets (e.g., `-0700`) are correctly parsed and normalized to UTC for internal storage, while the original string is preserved in the `_source` [search_examples/timezone_example.py:113-116]().
*   **Unsupported Formats**: Named timezones like `PST` or `EST` are not natively supported in the date string and will cause a parsing error [search_examples/timezone_example.py:103-109]().

#### Cross-Timezone Querying
When querying, the search engine normalizes both the query parameter and the indexed data to UTC. A query for `17:00:00.000` (UTC) will successfully match a document stored as `10:00:00.000-0700` because they represent the same point in time [search_examples/timezone_example.py:196-214]().

**Timezone Normalization Mapping**

```mermaid
graph LR
    "Doc1"["'10:00:00Z'"] --> "UTC_Conversion"["Internal UTC Representation"]
    "Doc2"["'10:00:00'"] --> "UTC_Conversion"
    "Doc3"["'10:00:00-0700'"] --> "UTC_Conversion"
    
    "Query"["Query: '17:00:00Z'"] --> "UTC_Conversion"
    
    "UTC_Conversion" --> "Match"["Match Found"]

    subgraph "Code Entities"
        "search_examples/timezone_example.py:83"
        "search_examples/timezone_example.py:93"
        "search_examples/timezone_example.py:113"
        "search_examples/timezone_example.py:196"
    end
```
Sources: [search_examples/timezone_example.py:62-70](), [search_examples/timezone_example.py:80-130](), [search_examples/timezone_example.py:143-234]()
