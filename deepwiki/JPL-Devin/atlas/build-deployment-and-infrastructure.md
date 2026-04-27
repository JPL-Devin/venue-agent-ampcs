# Page: Build, Deployment, and Infrastructure

# Build, Deployment, and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/CODEOWNERS](.github/CODEOWNERS)
- [.github/dependabot.yml](.github/dependabot.yml)
- [Dockerfile](Dockerfile)
- [NOTICE.txt](NOTICE.txt)
- [config/webpack.config.js](config/webpack.config.js)
- [eslint.config.mjs](eslint.config.mjs)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [public/index.html](public/index.html)
- [src/core/runtimeConfig.js](src/core/runtimeConfig.js)
- [src/index.css](src/index.css)

</details>



This section provides an overview of the Atlas build pipeline, its containerization strategy, and the CI/CD workflows that govern the repository. The infrastructure is designed to support a "build once, deploy anywhere" philosophy by decoupling the build-time assets from runtime environment configurations.

### Build and Infrastructure Overview

The Atlas infrastructure bridges the gap between the React source code and a deployable production environment. It utilizes Webpack for asset bundling, Docker for consistent runtime environments, and GitHub Actions for automated validation and delivery.

#### Code-to-Infrastructure Mapping
The following diagram illustrates how high-level infrastructure concepts map to specific entities within the codebase.

**Infrastructure Entity Mapping**
```mermaid
graph TD
    subgraph "Build System"
        "Webpack_Config"["config/webpack.config.js"]
        "Paths_Resolver"["config/paths.js"]
        "Babel_Pipeline"["babel-loader"]
        "ESLint_Config"["eslint.config.mjs"]
    end

    subgraph "Containerization"
        "Docker_File"["Dockerfile"]
        "Prod_Script"["scripts/start-prod.js"]
        "Package_JSON"["package.json"]
    end

    subgraph "Runtime Configuration"
        "Window_Config"["window.APP_CONFIG"]
        "Runtime_Module"["src/core/runtimeConfig.js"]
    end

    "Webpack_Config" --> "Paths_Resolver"
    "Docker_File" --> "Prod_Script"
    "Docker_File" --> "Package_JSON"
    "Runtime_Module" -.-> "Window_Config"
    "Webpack_Config" -.-> "ESLint_Config"
```
Sources: [config/webpack.config.js:1-25](), [Dockerfile:1-65](), [src/core/runtimeConfig.js:1-20](), [package.json:17-27](), [eslint.config.mjs:1-13]()

---

### 8.1 Webpack Build Configuration
The build process is managed by a Webpack configuration that handles both development and production environments [config/webpack.config.js:50-53](). The pipeline transforms modern JavaScript and assets into optimized bundles served via an Express-based production server [package.json:19]().

*   **Environment Branching**: Logic branches based on `isEnvDevelopment` and `isEnvProduction` to toggle features like Source Maps and HMR [config/webpack.config.js:51-52](), [config/webpack.config.js:147-151]().
*   **Asset Pipeline**: Loaders for CSS/SASS include PostCSS normalization to honor `browserslist` settings in `package.json` [config/webpack.config.js:81-117](), [package.json:100-111]().
*   **HTML & Pug**: Uses `HtmlWebpackPlugin` alongside `html2pug` to manage the entry point template [config/webpack.config.js:7-23]().
*   **Optimization**: Includes `TerserPlugin` for minification and `MiniCssExtractPlugin` for production CSS extraction [config/webpack.config.js:11-12]().

For a deep dive into the Babel pipeline and plugin configurations, see **[Webpack Build Configuration](#8.1)**.

Sources: [config/webpack.config.js:1-151](), [package.json:17-27]()

---

### 8.2 Docker and Runtime Configuration
Atlas uses a multi-stage `Dockerfile` to produce a slim runner image. The `builder` stage compiles the main application [Dockerfile:5-24](), followed by a stage for the Docusaurus-based Documentation project [Dockerfile:30-38](). The final `runner` stage copies only the necessary production artifacts and dependencies [Dockerfile:46-65]().

The application follows a **Runtime Configuration Injection** pattern to avoid environment-specific builds:
*   **`window.APP_CONFIG`**: Service URLs are resolved at runtime via this global object [src/core/runtimeConfig.js:16-18]().
*   **Service Resolution**: `src/core/runtimeConfig.js` provides helper functions like `getApiUrl()`, `getEsUrl()`, and `getFootprintUrl()` which check the runtime config before falling back to build-time environment variables [src/core/runtimeConfig.js:37-64]().

For details on the multi-stage build and the configuration injection pattern, see **[Docker and Runtime Configuration](#8.2)**.

Sources: [Dockerfile:1-65](), [src/core/runtimeConfig.js:1-115]()

---

### 8.3 CI/CD and Repository Governance
The repository is governed by automated workflows and configuration files that ensure code quality and security:

*   **Dependency Management**: `dependabot.yml` is configured for daily NPM updates and weekly Docker/GitHub Actions updates [ .github/dependabot.yml:1-37]().
*   **Code Ownership**: Review requirements are enforced via `CODEOWNERS`, primarily managed by the `@nasa-pds/img-atlas-pmc` team [ .github/CODEOWNERS:43-43]().
*   **Linting & Quality**: A comprehensive ESLint configuration [eslint.config.mjs:1-59]() is enforced during the build process [package.json:25-26]().
*   **Automated Delivery**: Deployment is handled via GitHub Actions workflows that leverage the `roundup-action` for distributing unstable and stable releases.

For details on branch protection, the security pipeline (CodeQL/NASA-Scrub), and automated delivery, see **[CI/CD and Repository Governance](#8.3)**.

**CI/CD Pipeline Flow**
```mermaid
graph LR
    "Push_Branch" --> "Lint_Check"["npm run lint"]
    "Lint_Check" --> "Build_Check"["npm run build"]
    
    "Main_Merge" --> "Unstable_Release"["Roundup Action (Unstable)"]
    "Release_Tag" --> "Stable_Release"["Roundup Action (Stable)"]
    
    "Schedule" --> "Security_Scan"["CodeQL + NASA-Scrub"]
    "Security_Scan" --> "SARIF_Report"["GitHub Security Tab"]
```
Sources: [package.json:17-27](), [ .github/dependabot.yml:1-15](), [ .github/CODEOWNERS:43-43]()
