# Page: Licensing, Security, and Repository Hygiene

# Licensing, Security, and Repository Hygiene

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.gitignore](.gitignore)
- [.pre-commit-config.yaml](.pre-commit-config.yaml)
- [.secrets.baseline](.secrets.baseline)
- [LICENSE.md](LICENSE.md)
- [NOTICE.txt](NOTICE.txt)
- [SECURITY.md](SECURITY.md)
- [repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.jar](repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.jar)
- [repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.jar.md5](repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.jar.md5)
- [repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.jar.sha1](repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.jar.sha1)
- [repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.pom](repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.pom)
- [repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.pom.md5](repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.pom.md5)
- [repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.pom.sha1](repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.pom.sha1)
- [repo/gov/nasa/pds/opencsv/maven-metadata.xml](repo/gov/nasa/pds/opencsv/maven-metadata.xml)

</details>



This page documents the administrative and structural standards of the `pds4-jparser` codebase. It covers the legal framework under the Apache 2.0 license, the security protocols for vulnerability reporting and secret detection, and the automated repository hygiene maintained through Git configuration and pre-commit hooks.

## Licensing and Attribution

The `pds4-jparser` project is licensed under the **Apache License, Version 2.0** [LICENSE.md:1-4](). This permissive license allows for the use, reproduction, and distribution of the software in both source and object forms [LICENSE.md:7-13]().

### NOTICE and Copyright
As required by Section 4(d) of the Apache License, the project includes a `NOTICE.txt` file. Any derivative works must retain the attribution notices contained within this file [LICENSE.md:100-112](). The project is copyrighted by the California Institute of Technology (Caltech), with U.S. Government sponsorship acknowledged [NOTICE.txt:3-4]().

### Third-Party Dependencies
The project includes "vendored" or locally hosted dependencies within the `repo/` directory, such as a modified version of `opencsv` [repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.pom:1-30](). These dependencies are subject to their own licensing terms, but their presence in the repository is managed to ensure compliance with NASA PDS distribution requirements.

**Sources:**
- [LICENSE.md:1-134]()
- [NOTICE.txt:1-32]()
- [repo/gov/nasa/pds/opencsv/5.5/opencsv-5.5.pom:1-100]()

---

## Security Policy

The security of the PDS4 parsing infrastructure is managed through a formal vulnerability reporting process and automated scanning.

### Supported Versions
Security updates are only provided for the latest stable releases. Currently, version `2.0.3` is the only supported branch for security patches [SECURITY.md:10-15]().

### Vulnerability Reporting
Security vulnerabilities should not be reported via public GitHub issues. Instead, the project provides a specific `vulnerability-issue.md` template to facilitate triaging by the development team [SECURITY.md:20-21]().

### Automated Secret Detection
The repository utilizes `detect-secrets` to prevent the accidental commitment of sensitive information (e.g., AWS keys, private keys, or high-entropy strings).

- **Baseline File**: The `.secrets.baseline` file contains a snapshot of existing "known" strings that are ignored by the scanner [ .secrets.baseline:1-134]().
- **Plugins**: The scanner uses multiple plugins, including `AWSKeyDetector`, `PrivateKeyDetector`, and `GitHubTokenDetector` [.secrets.baseline:11-65]().
- **Exclusions**: Files like `.git`, `target/` directories, and the `.secrets.baseline` itself are excluded from scanning to reduce noise [.secrets.baseline:126-133]().

**Sources:**
- [SECURITY.md:1-21]()
- [.secrets.baseline:1-134]()

---

## Repository Hygiene and Automation

To maintain a clean and consistent codebase, the project employs Git configuration and pre-commit hooks.

### .gitignore Conventions
The `.gitignore` file is structured to prevent build artifacts and IDE-specific metadata from entering the version control system.

| Category | Patterns |
| :--- | :--- |
| **Java/Maven** | `target/`, `*.javac`, `dependency-reduced-pom.xml` |
| **IDE Metadata** | `.idea/`, `.settings/`, `.vscode/`, `*.iml`, `*.project` |
| **Binaries/OS** | `*.dll`, `*.so`, `*.exe`, `.DS_Store` |
| **Test Artifacts** | Specific large test files (e.g., `i943630r.PNG`) |

**Sources:**
- [.gitignore:33-91]()

### Pre-commit Hooks
The project uses the `pre-commit` framework to enforce security checks before code is committed to the local repository [.pre-commit-config.yaml:4-6]().

- **Hook Implementation**: The primary hook is `detect-secrets` from the `NASA-AMMOS/slim-detect-secrets` repository [.pre-commit-config.yaml:20-24]().
- **Execution**: This hook runs against the current `.secrets.baseline` to ensure no new secrets are introduced in a commit [.pre-commit-config.yaml:26-27]().

### Code Ownership
The `.github/CODEOWNERS` file defines the individuals or teams responsible for specific parts of the codebase. By default, the `@NASA-PDS/validate-committers` team is required for reviews on all pull requests [.github/CODEOWNERS:43]().

**Sources:**
- [.pre-commit-config.yaml:1-38]()
- [.github/CODEOWNERS:1-47]()

---

## Implementation Diagrams

### Security and Secret Detection Flow
This diagram illustrates how the `pre-commit` hook interacts with the `detect-secrets` tool and the baseline file during the developer workflow.

**Secret Detection Workflow**
```mermaid
graph TD
    "Developer" -- "git commit" --> "Pre-Commit Hook"
    subgraph "Local Environment"
        "Pre-Commit Hook" -- "exec" --> "detect-secrets"
        "detect-secrets" -- "reads" --> ".secrets.baseline"
        "detect-secrets" -- "scans" --> "Staged Files"
    end
    "detect-secrets" -- "Success" --> "Commit Created"
    "detect-secrets" -- "Failure (New Secret Found)" --> "Commit Blocked"
    "Commit Blocked" -- "Action" --> "Audit/Update Baseline"
```
**Sources:**
- [.pre-commit-config.yaml:20-34]()
- [.secrets.baseline:1-134]()

### Repository Hygiene and Code Review Structure
This diagram maps the repository's hygiene configuration to the GitHub pull request and code ownership process.

**Code Entity to Repository Policy Mapping**
```mermaid
graph LR
    subgraph "Repository Hygiene"
        "GIT_IGNORE[.gitignore]" --> "Filtered Artifacts"
        "PRE_COMMIT[.pre-commit-config.yaml]" --> "Quality Gates"
    end

    subgraph "Governance"
        "OWNERS[.github/CODEOWNERS]" --> "PR Reviewers"
        "LICENSE[LICENSE.md]" --> "Legal Framework"
        "NOTICE[NOTICE.txt]" --> "Attribution Requirements"
    end

    "Filtered Artifacts" -- "Prevents" --> "Dirty Repository"
    "Quality Gates" -- "Enforces" --> "Security Standards"
    "PR Reviewers" -- "Approves" --> "Code Merge"
    "@NASA-PDS/validate-committers" -- "Acts As" --> "PR Reviewers"
```
**Sources:**
- [.gitignore:1-91]()
- [.github/CODEOWNERS:34-43]()
- [LICENSE.md:1-12]()
