# Jenkins CI Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Jenkinsfile](Jenkinsfile)

</details>



This page details the Jenkins CI pipeline defined in the `Jenkinsfile` [Jenkinsfile:1-94]() for the `execution-monitor-service` repository. It explains the declarative pipeline structure, the branch-based logic for `devel` versus pull request (PR) or feature branches, the calls to shared Ingenium Jenkins jobs, post-execution notifications, and workspace cleanup.

## Pipeline Structure and Branch-Based Logic

The Jenkins pipeline uses a declarative syntax [Jenkinsfile:1-94]() and is designed to execute different sets of stages based on the branch name. The primary distinction is made between the `devel` branch and all other branches (typically feature branches or those associated with pull requests).

### Diagram: Jenkins Pipeline Branching Logic

```mermaid
graph TD
    A[Start Pipeline] --> B{Branch Name?};
    B -- "BRANCH_NAME == 'devel'" --> C[Devel Branch Flow];
    B -- "BRANCH_NAME != 'devel'" --> D[PR/Feature Branch Flow];

    C --> C1["Build Image for Devel" (Ingenium/build_image)];
    C1 --> C2["Update CI Image for Devel" (Ingenium/update_ci_image)];
    C2 --> E[Post-build Actions];

    D --> D1["Build Image for PR/Feature" (Ingenium/build_image)];
    D1 --> D2["Run Repo Tests for PR" (Ingenium/run_repo_tests)];
    D2 --> E;

    E --> F{Pipeline Status?};
    F -- "Success" --> G[Notify Success];
    F -- "Failure" --> H[Notify Failure];
    F -- "Aborted" --> I[Notify Aborted];
    G,H,I --> J[Cleanup Workspace];
    J --> K[End Pipeline];
```
Sources:
* Jenkinsfile:9-54

### Devel Branch Workflow

When the `BRANCH_NAME` environment variable is `devel` [Jenkinsfile:9](), the pipeline executes two main stages:

1.  **Build Image for Devel**: This stage calls the shared Jenkins job `Ingenium/build_image` [Jenkinsfile:15]() to build a Docker image for the `execution-monitor-service`. The `REPO` parameter is set to `execution-monitor-service` and `REPO_BRANCH` is set to `devel` [Jenkinsfile:17-18]().
2.  **Update CI Image for Devel**: Following a successful image build, this stage calls the `Ingenium/update_ci_image` [Jenkinsfile:24]() job. This job is responsible for updating the CI environment with the newly built `devel` image. It also passes `REPO` as `execution-monitor-service` and `REPO_BRANCH` as `devel` [Jenkinsfile:26-27]().

This workflow ensures that the `devel` branch always has the latest built image and that the CI environment is updated accordingly.

Sources:
* Jenkinsfile:9-30

### PR/Feature Branch Workflow

For any branch other than `devel` (e.g., feature branches, pull request branches) [Jenkinsfile:31](), the pipeline executes a different set of stages:

1.  **Build Image for PR or Other Branch**: This stage also calls the `Ingenium/build_image` [Jenkinsfile:37]() job. However, instead of `REPO_BRANCH`, it uses the `REPO_TAG` parameter, setting its value to the current Git commit hash (`env.GIT_COMMIT`) [Jenkinsfile:7, Jenkinsfile:40](). This ensures that each PR or feature branch build is tagged with its specific commit, allowing for traceability and preventing conflicts.
2.  **Run Repo Tests for PR**: After the image is built, this stage invokes the `Ingenium/run_repo_tests` [Jenkinsfile:46]() job. This job is configured to run only the tests specific to the current repository (`ONLY_REPO_TESTS: true`) [Jenkinsfile:49](). It also passes the `REPO` name, the `REPO_TAG` (commit hash), and specifies `CLUSTER_BRANCH` as `devel` [Jenkinsfile:48-51](). This ensures that changes on feature branches are thoroughly tested against the `devel` environment before being merged.

Sources:
* Jenkinsfile:31-54

## Shared Jenkins Job Calls

The pipeline leverages several shared Jenkins jobs from the `Ingenium` folder. These jobs encapsulate common CI/CD tasks across the Ingenium ecosystem.

### Diagram: Shared Jenkins Job Calls

```mermaid
graph TD
    A[Jenkinsfile] --> B{"BRANCH_NAME"};
    B -- "devel" --> C["Ingenium/build_image" (REPO: "execution-monitor-service", REPO_BRANCH: "devel")];
    C --> D["Ingenium/update_ci_image" (REPO: "execution-monitor-service", REPO_BRANCH: "devel")];

    B -- "other" --> E["Ingenium/build_image" (REPO: "execution-monitor-service", REPO_TAG: commitHash)];
    E --> F["Ingenium/run_repo_tests" (REPO: "execution-monitor-service", ONLY_REPO_TESTS: true, REPO_TAG: commitHash, CLUSTER_BRANCH: "devel")];
```
Sources:
* Jenkinsfile:15-19
* Jenkinsfile:24-28
* Jenkinsfile:37-41
* Jenkinsfile:46-52

### `Ingenium/build_image`

This job is responsible for building Docker images.
*   **Parameters for `devel` branch**: `REPO` (`execution-monitor-service`), `REPO_BRANCH` (`devel`) [Jenkinsfile:17-18]().
*   **Parameters for PR/feature branches**: `REPO` (`execution-monitor-service`), `REPO_TAG` (current Git commit hash) [Jenkinsfile:39-40]().

### `Ingenium/update_ci_image`

This job updates the CI environment with the newly built image.
*   **Parameters**: `REPO` (`execution-monitor-service`), `REPO_BRANCH` (`devel`) [Jenkinsfile:26-27](). This job is only called for the `devel` branch.

### `Ingenium/run_repo_tests`

This job executes repository-specific tests.
*   **Parameters**: `REPO` (`execution-monitor-service`), `ONLY_REPO_TESTS` (`true`), `REPO_TAG` (current Git commit hash), `CLUSTER_BRANCH` (`devel`) [Jenkinsfile:48-51](). This job is only called for PR/feature branches.

Sources:
* Jenkinsfile:15-52

## Post-Execution Actions

The `post` section of the pipeline defines actions to be taken regardless of the pipeline's outcome [Jenkinsfile:59-93]().

### Notifications

Based on the pipeline's status (success, failure, or aborted) and the branch name, an `echo` message is printed to the console [Jenkinsfile:60-86]().

*   **Success**:
    *   `devel` branch: "Build and update for "devel" branch completed successfully." [Jenkinsfile:63]()
    *   Other branches: "Build and tests for PR or other branches completed successfully." [Jenkinsfile:65]()
*   **Failure**:
    *   `devel` branch: "Build and update for "devel" branch failed." [Jenkinsfile:72]()
    *   Other branches: "Build and tests for PR or other branches failed." [Jenkinsfile:74]()
*   **Aborted**:
    *   `devel` branch: "Build and update for "devel" branch was aborted." [Jenkinsfile:81]()
    *   Other branches: "Build and tests for PR or other branches were aborted." [Jenkinsfile:83]()

### Workspace Cleanup

Regardless of the pipeline's status, the `cleanup` block ensures that the Jenkins workspace is cleared using the `cleanWs()` function [Jenkinsfile:87-92](). This helps maintain a clean build environment and prevents issues from leftover files from previous runs.

Sources:
* Jenkinsfile:59-93
