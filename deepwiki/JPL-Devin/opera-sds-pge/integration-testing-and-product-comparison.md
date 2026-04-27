# Page: Integration Testing and Product Comparison

# Integration Testing and Product Comparison

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.ci/scripts/cslc_s1/compare_cslc_s1_products.sh](.ci/scripts/cslc_s1/compare_cslc_s1_products.sh)
- [.ci/scripts/cslc_s1/compare_cslc_s1_static_products.sh](.ci/scripts/cslc_s1/compare_cslc_s1_static_products.sh)
- [.ci/scripts/cslc_s1/test_cslc_s1.sh](.ci/scripts/cslc_s1/test_cslc_s1.sh)
- [.ci/scripts/disp_ni/test_disp_ni.sh](.ci/scripts/disp_ni/test_disp_ni.sh)
- [.ci/scripts/disp_s1/compare_disp_s1_products.sh](.ci/scripts/disp_s1/compare_disp_s1_products.sh)
- [.ci/scripts/disp_s1/compare_disp_s1_static_products.sh](.ci/scripts/disp_s1/compare_disp_s1_static_products.sh)
- [.ci/scripts/disp_s1/disp_s1_compare.py](.ci/scripts/disp_s1/disp_s1_compare.py)
- [.ci/scripts/disp_s1/test_disp_s1.sh](.ci/scripts/disp_s1/test_disp_s1.sh)
- [.ci/scripts/disp_s1/test_int_disp_s1.sh](.ci/scripts/disp_s1/test_int_disp_s1.sh)
- [.ci/scripts/dist_s1/compare_dist_s1_products.sh](.ci/scripts/dist_s1/compare_dist_s1_products.sh)
- [.ci/scripts/dist_s1/dist_s1_compare.py](.ci/scripts/dist_s1/dist_s1_compare.py)
- [.ci/scripts/dist_s1/test_int_dist_s1.sh](.ci/scripts/dist_s1/test_int_dist_s1.sh)
- [.ci/scripts/dswx_hls/compare_dswx_hls_products.sh](.ci/scripts/dswx_hls/compare_dswx_hls_products.sh)
- [.ci/scripts/dswx_hls/dswx_hls_compare.py](.ci/scripts/dswx_hls/dswx_hls_compare.py)
- [.ci/scripts/dswx_hls/test_dswx_hls.sh](.ci/scripts/dswx_hls/test_dswx_hls.sh)
- [.ci/scripts/dswx_ni/test_dswx_ni.sh](.ci/scripts/dswx_ni/test_dswx_ni.sh)
- [.ci/scripts/dswx_s1/diff_dswx_files.py](.ci/scripts/dswx_s1/diff_dswx_files.py)
- [.ci/scripts/dswx_s1/test_dswx_s1.sh](.ci/scripts/dswx_s1/test_dswx_s1.sh)
- [.ci/scripts/metrics/plot_metric_data.py](.ci/scripts/metrics/plot_metric_data.py)
- [.ci/scripts/metrics/process_metric_data.py](.ci/scripts/metrics/process_metric_data.py)
- [.ci/scripts/rtc_s1/compare_rtc_s1_products.sh](.ci/scripts/rtc_s1/compare_rtc_s1_products.sh)
- [.ci/scripts/rtc_s1/compare_rtc_s1_static_products.sh](.ci/scripts/rtc_s1/compare_rtc_s1_static_products.sh)
- [.ci/scripts/rtc_s1/rtc_s1_compare.py](.ci/scripts/rtc_s1/rtc_s1_compare.py)
- [.ci/scripts/rtc_s1/test_rtc_s1.sh](.ci/scripts/rtc_s1/test_rtc_s1.sh)
- [.ci/scripts/tropo/compare_tropo_products.sh](.ci/scripts/tropo/compare_tropo_products.sh)

</details>



Integration testing in the OPERA SDS PGE repository ensures that the full Product Generation Executable (PGE) lifecycle—from input validation to SAS execution and output metadata generation—functions correctly within a containerized environment. This process involves executing PGE Docker images against known datasets and performing bit-for-bit or statistically significant comparisons against "golden" reference products.

## Integration Test Orchestration

Integration tests are managed by per-PGE shell scripts (e.g., `test_int_*.sh`) located in `.ci/scripts/<pge_name>/`. These scripts automate the lifecycle of an integration test run.

### Test Lifecycle
1.  **Environment Setup**: Scripts source `test_int_util.sh` and `util.sh` to load helper functions for directory management and argument parsing [.ci/scripts/disp_s1/test_int_disp_s1.sh:8-10]().
2.  **Data Acquisition**: Test data (input and expected output) is typically downloaded from S3 and extracted into a temporary workspace [.ci/scripts/disp_s1/test_int_disp_s1.sh:39-43]().
3.  **Container Execution**: The PGE Docker image is run with specific volume mounts for `runconfig`, `input_dir`, `output_dir`, and `scratch_dir` [.ci/scripts/disp_s1/test_int_disp_s1.sh:106-113]().
4.  **Metrics Collection**: Resource usage is tracked during the container run [.ci/scripts/disp_s1/test_int_disp_s1.sh:103-118]().
5.  **Product Comparison**: After the PGE completes, an orchestration script (e.g., `compare_disp_s1_products.sh`) is invoked to validate the generated outputs against golden references [.ci/scripts/disp_s1/test_int_disp_s1.sh:132-136]().

### Integration Test Data Flow
The following diagram illustrates how the integration test scripts bridge the gap between the host environment and the PGE container.

**Diagram: Integration Test Data Flow**
```mermaid
graph TD
    subgraph "Host Environment"
        [test_int_disp_s1.sh] -- "test_int_setup_test_data" --> [TMP_DIR]
        [TMP_DIR] -- "Mounts" --> [Docker_Container]
        [test_int_disp_s1.sh] -- "metrics_collection_start" --> [run_metrics.sh]
    end

    subgraph "Docker Container (PGE)"
        [Docker_Container] -- "Executes" --> [pge_main.py]
        [pge_main.py] -- "Generates" --> [OUTPUT_DIR]
        [OUTPUT_DIR] -- "Triggers" --> [compare_disp_s1_products.sh]
    end

    subgraph "Comparison Logic"
        [compare_disp_s1_products.sh] -- "Calls" --> [disp_s1_compare.py]
        [disp_s1_compare.py] -- "Reads" --> [EXPECTED_DIR]
        [disp_s1_compare.py] -- "Reads" --> [OUTPUT_DIR]
        [disp_s1_compare.py] -- "Writes" --> [results.html]
    end
```
Sources: [.ci/scripts/disp_s1/test_int_disp_s1.sh:100-113](), [.ci/scripts/disp_s1/compare_disp_s1_products.sh:13-16](), [.ci/scripts/disp_s1/disp_s1_compare.py:1-10]()

---

## Product Comparison Framework

The comparison framework consists of shell orchestrators and Python-based comparison logic.

### Comparison Orchestrators
The `compare_<pge>_products.sh` scripts iterate through the files in the PGE output directory and find their counterparts in the expected (golden) directory.
*   **Pairing Logic**: Files are matched based on filename patterns or embedded metadata, such as tile codes or acquisition dates [.ci/scripts/dist_s1/compare_dist_s1_products.sh:47-58](), [.ci/scripts/disp_s1/compare_disp_s1_products.sh:52-65]().
*   **Result Reporting**: Results are aggregated into an HTML report (`results.html`) using helpers from `test_int_util.sh` [.ci/scripts/dist_s1/compare_dist_s1_products.sh:28-30]().
*   **Status Codes**: The orchestrator writes a return code to a `.rc` file, which is then read by the parent integration script to determine the final test status [.ci/scripts/dist_s1/compare_dist_s1_products.sh:89-91]().

### Specialized Comparison Scripts
Different product types require different comparison strategies implemented in Python:

| Script | Product Type | Comparison Strategy |
| :--- | :--- | :--- |
| `disp_s1_compare.py` | DISP-S1 (HDF5) | Recursive group comparison, attribute matching, and tolerance-based dataset validation (e.g., `displacement`, `connected_component_labels`) [.ci/scripts/disp_s1/disp_s1_compare.py:64-135](). |
| `dist_s1_compare.py` | DIST-S1 (Directory) | Validates directory structure and content using `DistS1ProductDirectory` models [.ci/scripts/dist_s1/dist_s1_compare.py:35-41](). |
| `dswx_hls_compare.py` | DSWx-HLS (GeoTIFF) | GDAL-based comparison of bands, geotransforms, and metadata with specific exclusions for dynamic fields like `PROCESSING_DATETIME` [.ci/scripts/dswx_hls/dswx_hls_compare.py:52-126](). |
| `rtc_s1_compare.py` | RTC-S1 (HDF5/TIFF) | Deep comparison of HDF5 structures and GDAL datasets with relative/absolute error tolerances [.ci/scripts/rtc_s1/rtc_s1_compare.py:17-34](). |

**Diagram: HDF5 Comparison Logic (disp_s1_compare.py)**
```mermaid
graph TD
    [compare_groups] --> [Check_Keys]
    [Check_Keys] -- "Mismatch" --> [ComparisonError]
    [Check_Keys] -- "Match" --> [Iterate_Keys]
    [Iterate_Keys] -- "Is Group" --> [compare_groups_Recursive]
    [Iterate_Keys] -- "Is Dataset" --> [compare_datasets_attr]
    [compare_datasets_attr] --> [validate_dataset]
    [validate_dataset] -- "Numerical" --> [np.allclose]
    [validate_dataset] -- "Labels" --> [validate_conncomp_labels]
```
Sources: [.ci/scripts/disp_s1/disp_s1_compare.py:64-135](), [.ci/scripts/disp_s1/disp_s1_compare.py:209-213]()

---

## Metrics Pipeline

The metrics pipeline tracks the OS-level resource consumption of the PGE during integration tests.

### Execution Flow
1.  **`run_metrics.sh`**: Triggered by `metrics_collection_start`, this script samples system metrics (CPU, Memory, Disk I/O) at a defined `SAMPLE_TIME` interval [.ci/scripts/disp_s1/test_int_disp_s1.sh:103]().
2.  **`process_metric_data.py`**: After the test completes, this script parses the raw sampled data and calculates peak usage and averages.
3.  **`plot_metric_data.py`**: Generates visual representations of the resource usage over time, which are archived as part of the Jenkins build artifacts.

Sources: [.ci/scripts/disp_s1/test_int_disp_s1.sh:103-118](), [.ci/scripts/dist_s1/test_int_dist_s1.sh:97-111]()

---

## Shared Helpers (`util.sh` and `test_int_util.sh`)

These shell scripts provide the foundational functions used across all integration tests.

### Key Functions in `test_int_util.sh`
*   `test_int_setup_results_directory`: Initializes the directory where logs, HTML reports, and comparison RC files are stored [.ci/scripts/disp_s1/test_int_disp_s1.sh:37]().
*   `test_int_setup_test_data`: Handles the retrieval and extraction of zipped test datasets [.ci/scripts/disp_s1/test_int_disp_s1.sh:43]().
*   `initialize_html_results_file`: Creates the header and structure for the `results.html` file [.ci/scripts/dist_s1/compare_dist_s1_products.sh:28]().
*   `update_html_results_file`: Appends a row to the HTML report for each file compared, including the status (PASS/FAIL) and the output from the comparison script [.ci/scripts/dist_s1/compare_dist_s1_products.sh:84]().
*   `test_int_trap_cleanup`: Ensures temporary directories are removed upon script exit (unless debugging is enabled) [.ci/scripts/disp_s1/test_int_disp_s1.sh:46]().

### Key Functions in `util.sh`
*   `parse_build_args`: Standardizes argument parsing for CI scripts, handling flags like `--tag` or `--workspace` [.ci/scripts/rtc_s1/test_rtc_s1.sh:12]().

Sources: [.ci/scripts/disp_s1/test_int_disp_s1.sh:8-13](), [.ci/scripts/dist_s1/compare_dist_s1_products.sh:11-30](), [.ci/scripts/rtc_s1/test_rtc_s1.sh:7-12]()
