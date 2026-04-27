# Build, Testing & Distribution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.eslintrc.js](.eslintrc.js)
- [README.md](README.md)
- [dist/lithosphere.js](dist/lithosphere.js)
- [dist/src/core/cameras.d.ts](dist/src/core/cameras.d.ts)
- [dist/src/core/events.d.ts](dist/src/core/events.d.ts)
- [docs/assets/images/screenshot1.png](docs/assets/images/screenshot1.png)
- [package-lock.json](package-lock.json)
- [package.json](package.json)
- [travis.yml](travis.yml)
- [webpack.config.js](webpack.config.js)

</details>



This page details the LithoSphere build pipeline, quality assurance configurations, and the relationship between source files and distribution artifacts. LithoSphere utilizes a modern JavaScript toolchain centered around Webpack and TypeScript to transform source code into browser-compatible bundles.

### Build Pipeline

The build process is managed by Webpack, which orchestrates several loaders to process TypeScript, modern JavaScript, and CSS. The configuration handles dependency resolution, code transpilation, and asset optimization.

#### Key Loaders and Plugins
*   **ts-loader**: Compiles TypeScript files (`.ts`) into JavaScript, adhering to the rules defined in `tsconfig.json` [package.json:97]().
*   **babel-loader**: Transpiles JavaScript to ensure compatibility with older browsers using `@babel/core` [package.json:76, 81]().
*   **postcss-loader**: Processes CSS with `autoprefixer` to ensure cross-browser style compatibility [package.json:80, 92](), [webpack.config.js:55-61]().
*   **clean-webpack-plugin**: Ensures the `public/dist/` directory is cleared before each new build to prevent artifact accumulation [webpack.config.js:27-32]().
*   **terser-webpack-plugin**: Handles minification for production builds [package.json:95]().

#### Data Flow: Source to Artifact
The pipeline starts at the entry point `src/lithosphere.ts` [webpack.config.js:11]() and outputs a Universal Module Definition (UMD) bundle that can be used via CommonJS, AMD, or as a global variable in the browser [dist/lithosphere.js:1-10]().

| Stage | Tool | Input | Output |
| :--- | :--- | :--- | :--- |
| **Development** | `npm run start:dev` | `src/` | Unminified `public/dist/lithosphere.js` with `--watch` [package.json:18]() |
| **Production** | `npm run build:prod` | `src/` | Minified `public/dist/lithosphere.js` [package.json:22]() |
| **Analysis** | `npm run analyze` | Bundled JS | Visual report of module sizes via `webpack-bundle-analyzer` [package.json:30]() |

**Sources:** [package.json:16-31](), [webpack.config.js:8-21](), [dist/lithosphere.js:94]()

### Configuration & Linting

LithoSphere enforces strict code quality through TypeScript and ESLint.

#### TypeScript Configuration
The project uses TypeScript for type safety and modern language features. The build system generates both the JavaScript bundle and a declaration file (`lithosphere.d.ts`) for consumers [package.json:12]().

#### ESLint & Prettier
Code style is enforced via ESLint with TypeScript-specific plugins. Key rules include:
*   **Strictness**: Disallows `var` [ .eslintrc.js:26](), enforces `prefer-const` [ .eslintrc.js:30](), and requires explicit error handling for TypeScript expectations [ .eslintrc.js:25]().
*   **Formatting**: Prettier is integrated to handle code aesthetics [ .eslintrc.js:11-12]().
*   **Exclusions**: Third-party modules in `src/secondary/` and test files are ignored by certain linting rules to maintain compatibility [ .eslintrc.js:19]().

**Sources:** [package.json:24-26](), [ .eslintrc.js:1-35]()

### Testing Framework

Testing is implemented using **Jest**, a JavaScript testing framework.

#### Jest Setup
*   **ts-jest**: Allows Jest to consume and test TypeScript files directly [package.json:96]().
*   **jest-canvas-mock**: Since LithoSphere relies heavily on HTML5 Canvas for rendering (e.g., in `Clamped` layers and sprite generation), this mock is required to simulate Canvas APIs in a Node.js environment [package.json:90]().

#### Test Execution
Developers can run tests in three modes:
1.  `npm test`: Runs the full test suite once [package.json:27]().
2.  `npm run test:watch`: Re-runs tests automatically when files change [package.json:28]().
3.  `npm run test:cov`: Generates a code coverage report [package.json:29]().

**Sources:** [package.json:27-30](), [package.json:89-96]()

### CI/CD and Distribution

LithoSphere uses **Travis CI** for continuous integration to ensure that every pull request and commit meets quality standards.

#### Travis CI Setup
The CI environment is configured in `travis.yml` to:
1.  Initialize a Node.js environment [travis.yml:1-3]().
2.  Run the linter (`npm run lint`) to check for style violations [travis.yml:5]().
3.  Execute the test suite (`npm test`) to verify logic [travis.yml:6]().

#### Distribution Artifacts
The repository maintains a distinction between source code and distributable files:
*   **src/**: Contains the original TypeScript source code.
*   **dist/**: Contains the compiled JavaScript and type definitions for general use [package.json:11-12]().
*   **public/dist/**: The primary location for the Webpack-bundled library used by the demo and NPM [package.json:14-15](). This folder includes the main UMD bundle `lithosphere.js` [webpack.config.js:16]().

#### Build and Test Entity Mapping
The following diagram illustrates how build and test commands map to specific configuration files and code entities.

**Build and Test Pipeline Mapping**
```mermaid
graph TD
    subgraph "Command Space"
        ["npm run build:prod"]
        ["npm test"]
        ["npm run lint"]
    end

    subgraph "Config Space"
        ["webpack.config.js"]
        ["tsconfig.json"]
        [".eslintrc.js"]
        ["package.json"]
    end

    subgraph "Code Entity Space"
        ["src/lithosphere.ts"]
        ["src/secondary/"]
        ["public/dist/lithosphere.js"]
    end

    ["npm run build:prod"] --> ["webpack.config.js"]
    ["webpack.config.js"] --> ["tsconfig.json"]
    ["tsconfig.json"] --> ["src/lithosphere.ts"]
    ["src/lithosphere.ts"] --> ["public/dist/lithosphere.js"]
    
    ["npm run lint"] --> [".eslintrc.js"]
    [".eslintrc.js"] --> ["src/lithosphere.ts"]
    [".eslintrc.js"] --> ["src/secondary/"]
    
    ["npm test"] --> ["package.json"]
    ["package.json"] --> ["src/lithosphere.ts"]
```
**Sources:** [package.json:16-31](), [ .eslintrc.js:1-19](), [webpack.config.js:8-21](), [travis.yml:4-7]()

### Data Flow for Artifact Generation
The following diagram shows the transformation of source files through the Webpack loaders into the final distribution bundle.

**Artifact Generation Flow**
```mermaid
graph LR
    subgraph "Source (src/)"
        ["src/*.ts"]
        ["src/*.css"]
    end

    subgraph "Loaders (Webpack)"
        ["ts-loader"]
        ["babel-loader"]
        ["postcss-loader"]
        ["style-loader"]
    end

    subgraph "Distribution (public/dist/)"
        ["lithosphere.js (UMD)"]
        ["lithosphere.d.ts"]
    end

    ["src/*.ts"] --> ["ts-loader"]
    ["ts-loader"] --> ["babel-loader"]
    ["babel-loader"] --> ["lithosphere.js (UMD)"]
    ["src/*.css"] --> ["postcss-loader"]
    ["postcss-loader"] --> ["style-loader"]
    ["style-loader"] --> ["lithosphere.js (UMD)"]
    ["ts-loader"] --> ["lithosphere.d.ts"]
```
**Sources:** [package.json:11-15](), [webpack.config.js:35-65](), [dist/lithosphere.js:1-11]()
