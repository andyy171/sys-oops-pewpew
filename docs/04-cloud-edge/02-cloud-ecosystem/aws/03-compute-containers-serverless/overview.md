# AWS Compute, Containers And Serverless

## Overview

Nhóm này chứa EC2, AMI, Auto Scaling, Elastic Load Balancing, ECS/ECR/EKS/Fargate, Lambda, API Gateway và các pattern event-driven compute.

## Pages

- [EC2, Auto Scaling And Load Balancing](./01-ec2-auto-scaling-load-balancing.md)
- [Lambda, API Gateway And Event-Driven Compute](./02-lambda-api-gateway-event-driven.md)

## Service Selection

| Need | Common choice |
|---|---|
| VM control, OS-level customization | EC2 |
| Container workload ít vận hành node | ECS/Fargate |
| Kubernetes managed control plane | EKS |
| Short stateless function/event handling | Lambda |
| HTTP API trước serverless/backend | API Gateway |
