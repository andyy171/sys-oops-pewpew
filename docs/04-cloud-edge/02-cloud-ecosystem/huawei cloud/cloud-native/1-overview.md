# 1 overview

#

## Cloud computing development
Cloud computing has evolved through three major phases:

1. Virtualization Era (2006-2010)
Infrastructure virtualization through hypervisors

Resource pooling and allocation

Early IaaS offerings emerged

2. Cloud Era (2010-2015)
Automated resource provisioning

Self-service portals and APIs

Emergence of PaaS platforms

Container technology development (Docker, 2013)

3. Cloud Native Era (2015-Present)
Microservices architecture adoption

Container orchestration (Kubernetes dominance)

Serverless computing emergence

GitOps and DevOps practices

Service mesh technologies

## definition of cloud native 
Cloud native is an approach to building and running applications that leverages the advantages of the cloud computing delivery model. It encompasses:

Key Characteristics:

- Containerized: Each part packaged in its own container

- Dynamically orchestrated: Containers are actively scheduled and managed

- Microservices-oriented: Applications are segmented into microservices

**Official CNCF Definition:**
"Cloud native technologies empower organizations to build and run scalable applications in modern, dynamic environments such as public, private, and hybrid clouds. Techniques include containers, service meshes, microservices, immutable infrastructure, and declarative APIs."

## cloud native applications
### Characteristics of Cloud Native Applications
Loosely coupled with clear bounded contexts

Resilient to failures and disruptions

Manageable through automated processes

Observable with comprehensive monitoring

Automatically deployable through CI/CD pipelines

### Benefits of Cloud Native Applications
Faster time-to-market: Rapid development and deployment cycles

Improved scalability: Automatic scaling based on demand

Enhanced resilience: Built-in fault tolerance

Cost optimization: Pay only for resources consumed

Portability: Run anywhere across cloud environments
## principles of the cloud native architecture
1. Microservices Architecture
Decompose applications into small, independent services

Each service has a single responsibility

Services communicate through well-defined APIs

2. Containerization
Package applications with dependencies

Ensure consistency across environments

Isolate applications for security and stability

3. Dynamic Orchestration
Automated deployment, scaling, and management

Self-healing capabilities

Optimal resource utilization

4. DevOps Culture
Collaboration between development and operations

Automation of software delivery processes

Continuous integration and continuous delivery

5. API-Driven Communication
Services interact through well-defined APIs

Standardized communication protocols

Loose coupling between components

6. Infrastructure as Code (IaC)
Define and manage infrastructure through code

Version control for infrastructure

Reproducible environments

7. Declarative Configuration
Specify desired state rather than procedures

System works to maintain declared state

Simplified management and operations

8. Immutable Infrastructure
Replace rather than modify components

Consistent, versioned deployments

Reduced configuration drift
## Huawei Cloud native solutions
1. Cloud Container Engine (CCE)
Fully managed Kubernetes service

Supports hybrid cluster management

Integrated with Huawei Cloud services

Key Features:

Enterprise-grade Kubernetes clusters

GPU/NPU accelerated containers

Multi-zone high availability

Enhanced security with CIS compliance

2. Cloud Container Instance (CCI)
Serverless container platform

No need to manage underlying infrastructure

Pay-per-use billing model

Key Features:

Instant container startup

No cluster management required

Seamless integration with CCE

Fine-grained billing by second

3. Microservice Engine (CSE)
Full-lifecycle microservices management

Supports multiple frameworks (Spring Cloud, ServiceComb)

Enhanced service governance

Key Features:

Service registration and discovery

Dynamic configuration management

Traffic management and circuit breaking

Distributed tracing

4. Application Orchestration Service (AOS)
Unified application lifecycle management

Template-based application deployment

Multi-environment consistency

Key Features:

Visual application topology editing

One-click application deployment

Cross-region application migration

Integrated DevOps workflows

5. Function Graph (FunctionStage)
Serverless function computing service

Event-driven execution model

Automatic scaling with zero administration

Key Features:

Multiple language support

Visual function编排

Microservice framework integration

Pay-per-use billing model

6. Service Mesh (ASM)
Fully managed service mesh platform

Based on Istio open source technology

Fine-grained traffic management

Key Features:

Zero-trust security model

Canary releases and blue-green deployments

Comprehensive observability

Multi-cluster management
## cloud native trends 
1. Multi-Cluster and Hybrid Cloud Management
Unified management across environments

Federated Kubernetes clusters

Workload portability across clouds

2. GitOps Adoption
Declarative infrastructure management

Version-controlled configuration

Automated synchronization

3. Serverless Containers
Abstracted infrastructure management

Event-driven container execution

Finer-grained billing models

4. Edge Computing Integration
Cloud native technologies at the edge

Lightweight Kubernetes distributions

Distributed application management

5. AI/ML Workloads on Kubernetes
Specialized operators for AI workloads

GPU/NPU resource scheduling

MLOps practices integration

6. Enhanced Security Practices
Zero-trust security models

Policy-as-code implementation

Runtime security monitoring

7. Sustainability Focus
Resource efficiency optimization

Carbon-aware scheduling

Energy-efficient infrastructure

8. Platform Engineering
Internal developer platforms

Self-service capabilities

Standardized development environments

9. WebAssembly (Wasm) in Cloud Native
Portable binary instruction format

Multi-language support

Secure runtime environments

10. Database Modernization
Cloud native databases

Database operators for Kubernetes

Automated management operations
