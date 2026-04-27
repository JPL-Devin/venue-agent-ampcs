# Frontend Unit and E2E Tests

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Dockerfile-e2e-testing-ci](Dockerfile-e2e-testing-ci)
- [Dockerfile-unit-testing-ci](Dockerfile-unit-testing-ci)
- [docker-compose-e2e-tests.yml](docker-compose-e2e-tests.yml)
- [src/client/config/test.env.js](src/client/config/test.env.js)

</details>



This page documents the testing infrastructure for the Ingenium UI frontend, covering both isolated unit testing of Vue components and full end-to-end (E2E) browser automation. The testing suite ensures the reliability of the procedure authoring, execution, and administrative interfaces.

## Unit Testing Infrastructure

The frontend unit testing suite is built using **Karma** as the test runner and **Jasmine** as the assertion framework. Tests are executed against the Vue.js components and Vuex stores in an automated fashion.

### Configuration and Environment
Unit tests are configured to run in a simulated browser environment. The environment configuration for tests is defined in `src/client/config/test.env.js`, which merges the development environment settings and sets `NODE_ENV` to `"test"` [src/client/config/test.env.js:1-7]().

### Test Organization
Unit tests are located in `src/client/test/unit/` and are organized to mirror the `src/client/src/modules/` directory structure. Key areas covered include:

*   **Dashboard and Venues**: Specs for `Venues.vue`, `VenueTile.vue`, `VenueDetails.vue`, and `VenueActionLink.vue`. These verify that venue statuses (Active, Suspended, etc.) render correctly and that action links trigger the appropriate Vuex actions.
*   **Real-time Communication**: WebSocket specs ensure that the frontend correctly handles incoming status updates and execution events from the backend.
*   **Feature Modules**: Subdirectories contain specific specs for:
    *   **Authoring**: Logic for procedure creation, versioning, and element editing.
    *   **Execution**: Verification of the execution toolbar, step progress tracking, and audio feedback triggers.
    *   **Reporting**: Validation of execution selection and report generation logic.
    *   **Project Config**: Tests for dictionary mappings and custom script configurations.

### CI Execution
For Continuous Integration, unit tests are executed within a dedicated container defined by `Dockerfile-unit-testing-ci`. This Dockerfile uses a Node 8.11.1 base image, installs dependencies via `npm install`, and executes the `npm run unit-ci` command [Dockerfile-unit-testing-ci:1-13]().

### Unit Test Component Flow
The following diagram illustrates how the unit testing suite interacts with the frontend source code.

**Frontend Unit Testing Architecture**
```mermaid
graph TD
    subgraph "TestRunnerSpace"
        ["KarmaRunner"] -- "executes" --> ["JasmineSpecs"]
        ["JasmineSpecs"] -- "imports" --> ["VueTestUtils"]
    end

    subgraph "CodeEntitySpace"
        ["VueTestUtils"] -- "mounts" --> ["VenueTile.vue"]
        ["VueTestUtils"] -- "mounts" --> ["VenueActionLink.vue"]
        ["JasmineSpecs"] -- "mocks" --> ["venue-store.js"]
        ["JasmineSpecs"] -- "asserts" --> ["WebSocketHandler"]
    end

    subgraph "SourceModules"
        ["VenueTile.vue"] --- ["src/client/src/modules/dashboard/VenueTile.vue"]
        ["venue-store.js"] --- ["src/client/src/modules/common/stores/venue-store.js"]
    end
```
Sources: [Dockerfile-unit-testing-ci:1-13](), [src/client/config/test.env.js:1-7]()

---

## End-to-End (E2E) Testing

End-to-end tests validate the entire system stack by driving a real Chrome browser to interact with the UI, which in turn communicates with the Django backend and underlying microservices.

### Protractor Setup
The project uses **Protractor** (a wrapper around WebDriverJS) for E2E testing. The tests are designed to run against a fully deployed instance of the application.

*   **Fixtures**: Located in `src/client/test/e2e/fixtures/`, these provide baseline data (e.g., sample procedures or user profiles) to ensure consistent test states.
*   **Helpers**: Utility functions in `src/client/test/e2e/helpers/` abstract common browser actions like logging in, waiting for elements to appear, or interacting with the Froala editor.

### Dockerized E2E Environment
E2E tests require a complex environment involving the UI, backend services, and a Selenium-controlled browser. This is managed via `docker-compose-e2e-tests.yml`.

| Service | Role | Image/Source |
| :--- | :--- | :--- |
| `chrome` | Selenium Standalone Chrome browser for test execution [docker-compose-e2e-tests.yml:4-10]() | `selenium/standalone-chrome:3.10.0` |
| `ingenium_e2e` | The test runner container that executes Protractor [docker-compose-e2e-tests.yml:11-15]() | `Dockerfile-e2e-testing-ci` |

### Environment Configuration
The `ingenium_e2e` service is configured with several environment variables to point to the various backend microservices and the Nginx entry point:
*   `CORE_API_URL`: Points to the Core server [docker-compose-e2e-tests.yml:20]().
*   `UI_NGINX_URL`: The URL of the Nginx proxy serving the UI [docker-compose-e2e-tests.yml:24]().
*   `TEST_USER` / `TEST_PASS`: Credentials used by the automated scripts to authenticate [docker-compose-e2e-tests.yml:17-18]().

**E2E Test Execution Flow**
```mermaid
graph LR
    subgraph "TestingContainer"
        ["Protractor"] -- "commands" --> ["SeleniumDriver"]
    end

    subgraph "SeleniumContainer"
        ["SeleniumDriver"] -- "controls" --> ["ChromeBrowser"]
    end

    subgraph "ApplicationStack"
        ["ChromeBrowser"] -- "HTTP Requests" --> ["ui_nginx"]
        ["ui_nginx"] -- "Proxies" --> ["DjangoBackend"]
        ["DjangoBackend"] -- "API Calls" --> ["core_server"]
    end

    ["Protractor"] -- "reports to" --> ["test-reports/"]
```
Sources: [docker-compose-e2e-tests.yml:1-34](), [Dockerfile-e2e-testing-ci:1-13]()

---

## CI/CD Integration and Reporting

Both unit and E2E tests are designed to run in CI environments (such as Jenkins or GitLab CI) using the provided Dockerfiles.

### CI Dockerfiles
*   **Unit Testing**: `Dockerfile-unit-testing-ci` installs the Node environment and runs `npm run unit-ci` [Dockerfile-unit-testing-ci:1-13]().
*   **E2E Testing**: `Dockerfile-e2e-testing-ci` follows a similar pattern but executes `npm run e2e-ci` [Dockerfile-e2e-testing-ci:1-13]().

### Volume Mapping and Artifacts
In the `docker-compose-e2e-tests.yml` configuration, a volume is mapped from the host's `$REPO_DIR/tests/test-reports` to the container's `/src/client/test/test-reports` [docker-compose-e2e-tests.yml:28-29](). This allows the CI runner to persist and archive test results (XML/HTML reports) even after the containers have exited.

### Network Configuration
The E2E tests utilize an external network defined by `${SINGLENODE_COMPOSE_NETWORK}` [docker-compose-e2e-tests.yml:31-33](). This ensures that the test runner and the Chrome browser can resolve the hostnames of the actual application services (like `ui_nginx` or `core_server`) running in a separate compose stack.

Sources: [Dockerfile-unit-testing-ci:1-13](), [Dockerfile-e2e-testing-ci:1-13](), [docker-compose-e2e-tests.yml:1-34]()
