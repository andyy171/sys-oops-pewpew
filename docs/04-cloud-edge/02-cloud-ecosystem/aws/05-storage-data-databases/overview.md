# AWS Storage, Data And Databases

## Overview

Nhóm này chứa S3, EBS, EFS, FSx, DataSync/Snowball, RDS, Aurora, DynamoDB, ElastiCache, Athena, Glue và QuickSight.

## Pages

- [S3 Object Storage Patterns](./01-s3-object-storage-patterns.md)
- [EBS, EFS, FSx And Data Migration](./02-ebs-efs-fsx-data-migration.md)
- [RDS, Aurora, DynamoDB And Caching](./03-rds-aurora-dynamodb-caching.md)
- [Storage And Database Selection Patterns](./04-storage-and-database-selection-patterns.md)

## Service Selection

| Need | Common choice |
|---|---|
| Object, backup, static content, data lake | S3 |
| Block volume cho EC2/database | EBS |
| Shared Linux file system | EFS |
| Windows SMB hoặc Lustre/HPC | FSx |
| Relational SQL managed DB | RDS/Aurora |
| Key-value/document low-latency NoSQL | DynamoDB |
| Cache | ElastiCache/DAX |
| Query data trong S3 | Athena + Glue catalog |
