# Page: Issue Templates and Pull Request Process

# Issue Templates and Pull Request Process

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/issue-project-automation.yml](.github/workflows/issue-project-automation.yml)

</details>



The `pds4-jparser` repository follows a structured contribution workflow designed to maintain high code quality and alignment with NASA PDS standards. This process is governed by specific GitHub issue templates for reporting bugs or requesting features and a rigorous pull request (PR) checklist that triggers automated CI/CD pipelines.

## Issue Templates

The repository utilizes standardized issue templates to ensure that all necessary technical context is captured before development begins. Each issue is automatically triaged and added to the NASA-PDS project board via the `Issue Project Automation` workflow [`.github/workflows/issue-project-automation.yml`:1-23]().

### 1. Bug Report (`bug_report.md`)
Used for reporting unexpected behavior or crashes in the library. Reporters are expected to provide:
*   **PDS4 Information Model (IM) Version**: Essential for determining which JAXB-generated classes are involved [`.github/ISSUE_TEMPLATE/bug_report.md`]().
*   **Environment**: Java version and OS.
*   **Logs/Stack Traces**: Crucial for identifying failures in `ObjectAccess` or `TableReader` [`.github/ISSUE_TEMPLATE/bug_report.md`]().

### 2. Feature Request (`feature_request.md`)
Used for proposing new functionality, such as support for a new PDS4 data type or an additional export format in `TwoDImageExporter`.
*   **Problem Statement**: Description of the gap in current functionality.
*   **Proposed Solution**: Technical suggestion for implementation.

### 3. PDS4 Standards Change Request (`pds4-standards-change-request.md`)
This unique template is used when a change in the library is necessitated by an update to the PDS4 Information Model or a specific Data Dictionary.
*   **SCR Reference**: Links to the official PDS4 Software Change Request.
*   **Impacted Schemas**: Identifies which `.xsd` files need to be updated in the `src/main/resources/schema` directory.

### 4. Vulnerability Issue (`vulnerability-issue.md`)
Used for reporting security flaws or outdated/insecure dependencies. These issues are often cross-referenced with the `CodeQL` and `Dependabot` automated scans [`.github/workflows/stable-cicd.yml`:1-10]().

### 5. Integration Test (I-T) Bug Report (`i-t-bug-report.md`)
Specifically for failures discovered during integration testing, particularly when running `ExtractTable` against large-scale PDS4 archives or during the `validate` tool downstream testing.

### 6. Requirement (`requirement.md`)
Used to document formal functional or non-functional requirements. These often map directly to the documents found in `docs/requirements/`.

**Sources:**
*   [`.github/workflows/issue-project-automation.yml`:1-36]()
*   [`.github/ISSUE_TEMPLATE/bug_report.md`]() (implied by context)

---

## Pull Request Process

The PR process is the primary gatekeeper for the `pds4-jparser` codebase. It ensures that every change is vetted by both automated systems and human reviewers (defined in `CODEOWNERS`).

### Automation and Data Flow
When a PR is opened, several GitHub Actions are triggered to validate the integrity of the Java codebase.

#### PR Automation Flow
Title: PR Validation and Project Tracking
```mermaid
graph TD
    "PR_Opened[PR Opened/Labeled]" --> "Label_Check{Label: 'bug' or 'enhancement'}"
    "Label_Check" -->|"Yes"| "Project_Auto[Issue Project Automation]"
    "PR_Opened" --> "CI_Workflow[branch-cicd.yml]"
    
    subgraph "branch-cicd Pipeline"
        "CI_Workflow" --> "Build[mvn clean install]"
        "Build" --> "Tests[TestNG Unit Tests]"
        "Tests" --> "Downstream[Downstream Validate Testing]"
    end
    
    "Project_Auto" --> "Project_Board[NASA-PDS Project 6]"
    "Downstream" --> "Review_Ready[Ready for Reviewer]"
```
**Sources:**
*   [`.github/workflows/issue-project-automation.yml`:8-18]()
*   [`.github/workflows/branch-cicd.yml`]() (referenced for CI context)

### Pull Request Checklist
Contributors must complete a checklist before a PR is considered for merging:
1.  **Issue Linkage**: Every PR must reference a specific issue number (e.g., `Closes #123`).
2.  **Code Standards**: Compliance with the project's formatting and license header requirements.
3.  **Test Coverage**: New features must include TestNG unit tests in `src/test/java`.
4.  **Documentation**: Updates to the Wiki or Javadoc if public APIs in `gov.nasa.pds.label` or `gov.nasa.pds.objectAccess` are modified.

### Review and Merge Strategy
The project uses a strict review hierarchy:
*   **Reviewers**: At least one approval from a member of the `NASA-PDS/validate-committers` team is required.
*   **Project Automation**: The `handle-label` job in `issue-project-automation.yml` moves the associated issue through the sprint backlog based on the labels applied to the PR [`.github/workflows/issue-project-automation.yml`:26-33]().
*   **Merge**: Squash and merge is preferred to maintain a clean history on the `main` branch.

#### Code Entity Association
Title: Mapping PR Actions to Workflow Code
```mermaid
graph LR
    subgraph "GitHub Actions Entities"
        "Job: add-new-issue-to-project"["add-new-issue-to-project"]
        "Job: handle-label"["handle-label"]
        "Workflow: issue-project-automation.yml"["issue-project-automation.yml"]
    end

    subgraph "External Integration"
        "Secret: ORG_PROJECT_PAT"["ORG_PROJECT_PAT"]
        "Action: add-issue-to-project.yml"["add-issue-to-project.yml@main"]
    end

    "Workflow: issue-project-automation.yml" --> "Job: add-new-issue-to-project"
    "Workflow: issue-project-automation.yml" --> "Job: handle-label"
    "Job: add-new-issue-to-project" --> "Action: add-issue-to-project.yml"
    "Action: add-issue-to-project.yml" -.-> "Secret: ORG_PROJECT_PAT"
```
**Sources:**
*   [`.github/workflows/issue-project-automation.yml`:9-11]()
*   [`.github/workflows/issue-project-automation.yml`:21-23]()
*   [`.github/workflows/issue-project-automation.yml`:26-28]()

## Project Automation Details
The project management is highly automated to reduce administrative overhead for developers.

| Trigger Event | Workflow Job | Target Project | Action |
| :--- | :--- | :--- | :--- |
| Issue Opened | `add-new-issue-to-project` | Project "6" | Adds issue to the triage column [`.github/workflows/issue-project-automation.yml`:11-18]() |
| Label Added | `handle-label` | Project "6" | Moves issue based on `label_name` [`.github/workflows/issue-project-automation.yml`:28-32]() |
| Label Removed | `handle-label` | Project "6" | Updates status in the project board [`.github/workflows/issue-project-automation.yml`:33]() |

The `gh_token` used for these operations must be a Personal Access Token (PAT) with `project` scope, stored as `ORG_PROJECT_PAT`, as the standard `GITHUB_TOKEN` lacks permissions for organization-level projects [`.github/workflows/issue-project-automation.yml`:20-23]().

**Sources:**
*   [`.github/workflows/issue-project-automation.yml`:1-36]()
