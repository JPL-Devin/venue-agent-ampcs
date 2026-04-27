# Page: Deployment and Infrastructure

# Deployment and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docker/README.md](docker/README.md)
- [terraform/README.md](terraform/README.md)
- [terraform/aws/api_uri_rewrite.js](terraform/aws/api_uri_rewrite.js)
- [terraform/aws/test_api_uri_rewrite.html](terraform/aws/test_api_uri_rewrite.html)
- [terraform/ecs.tf](terraform/ecs.tf)
- [terraform/provider.tf](terraform/provider.tf)
- [terraform/variables.tf](terraform/variables.tf)

</details>



The NASA PDS Registry API is designed for flexible deployment, ranging from local development environments using **Docker** to highly available production clusters on **AWS ECS Fargate**. The infrastructure is managed as code using **Terraform**, ensuring reproducible deployments across different venues (dev, test, prod).

### Infrastructure Overview

The deployment architecture centers on a containerized Spring Boot application. In a cloud environment, this container is orchestrated by AWS ECS, fronted by an Application Load Balancer (ALB), and integrated with a CloudFront URI rewrite function for path normalization.

#### System Mapping: Infrastructure to Code
The following diagram bridges high-level AWS infrastructure components to their specific definitions in the Terraform configuration.

| Infrastructure Component | Terraform Resource / Code Entity | Role |
| --- | --- | --- |
| **ECS Cluster** | `aws_ecs_cluster.pds-registry-api-ecs` | Orchestration boundary for Fargate tasks [terraform/ecs.tf:79-87](). |
| **Fargate Service** | `aws_ecs_service.pds-registry-reg-service` | Maintains the desired count of running containers [terraform/ecs.tf:169-194](). |
| **Task Definition** | `aws_ecs_task_definition.pds-registry-ecs-task` | Defines container image, CPU (256), and Memory (512) [terraform/ecs.tf:108-164](). |
| **Load Balancer** | `aws_lb.registry-api-lb` | Public entry point for API traffic [terraform/ecs.tf:1-21](). |
| **Health Check** | `path = "/health"` | ALB target group health monitoring [terraform/ecs.tf:41-47](). |

### Deployment Options

#### 1. Docker Containers
The application is packaged as a Docker image using a multi-stage build process. It supports various configurations, including HTTP/HTTPS variants and development-specific overrides.
*   **Build Argument**: The `api_jar` argument is used to specify the location of the compiled JAR artifact [docker/README.md:12-15]().
*   **Environment Variables**: Runtime behavior is controlled via `SPRING_BOOT_APP_ARGS` and `SERVER_PORT` [docker/README.md:45-49]().

For details on image variants and local execution, see **[Docker Images (#7.1)]**.

#### 2. AWS ECS Fargate (Terraform)
Production deployments utilize Terraform to provision a serverless container environment. This setup requires several external dependencies, such as a VPC shared with OpenSearch and specific IAM roles (`ecs_task_execution_role`) [terraform/README.md:11-23]().
*   **Networking**: Uses `awsvpc` network mode for Fargate [terraform/ecs.tf:157-157]().
*   **Configuration**: The `spring_boot_args` variable allows passing OpenSearch host and discipline node settings directly to the container [terraform/variables.tf:16-18]().

For details on the Terraform modules and AWS resources, see **[Terraform AWS ECS Fargate Deployment (#7.2)]**.

### URI Normalization and Routing

To support standardized API pathing (e.g., `/api/search-en/v1/products`), a CloudFront Function named `api_uri_rewrite.js` is utilized. This script performs two critical tasks before the request reaches the load balancer:
1.  **Path Stripping**: It transforms complex paths into the simple paths expected by the Spring Boot controllers (e.g., stripping `/api/search-en/v1/`) [terraform/aws/api_uri_rewrite.js:51-57]().
2.  **Header Injection**: It injects `x-request-node` and `x-forwarded-prefix` headers, which are used for internal routing logic and Swagger UI compatibility [terraform/aws/api_uri_rewrite.js:58-59]().

#### Request Transformation Flow

```mermaid
graph TD
    subgraph "Public Internet"
        "UserRequest"["User Request: /api/search-en/v1/products"]
    end

    subgraph "CloudFront Edge"
        "Handler"["api_uri_rewrite.js: handler(event)"]
        "Rewrite"["Strip Prefix & Set x-request-node"]
    end

    subgraph "AWS Infrastructure"
        "ALB"["aws_lb: registry-api-lb"]
        "ECS"["aws_ecs_service: pds-registry-reg-service"]
    end

    "UserRequest" --> "Handler"
    "Handler" --> "Rewrite"
    "Rewrite" -- "Internal URI: /products" --> "ALB"
    "ALB" --> "ECS"
```
**Sources:** [terraform/aws/api_uri_rewrite.js:22-71](), [terraform/ecs.tf:49-58]()

### Infrastructure Requirements
| Requirement | Description |
| --- | --- |
| **OpenSearch** | Must contain indices like `registry` and `registry-refs` [terraform/README.md:19-19](). |
| **VPC/Subnets** | Fargate tasks require private subnets with access to the OpenSearch cluster [terraform/README.md:14-15](). |
| **ACM Certificate** | An SSL certificate ARN is required for the HTTPS listener on port 443 [terraform/ecs.tf:51-53](). |

**Sources:**
- [terraform/ecs.tf:1-194]()
- [terraform/variables.tf:1-73]()
- [terraform/README.md:1-42]()
- [docker/README.md:1-49]()
- [terraform/aws/api_uri_rewrite.js:1-71]()
