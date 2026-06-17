# PostgreSQL

PostgreSQL là relational database mạnh về SQL, transaction, type system, extension, MVCC và khả năng vận hành production. Nhánh này tập trung vào góc nhìn hạ tầng: schema, data load, role/security, backup/restore, HA và day-2 operations.

## Reading Order

1. [Architecture And Core Concepts](./01-architecture-and-core-concepts.md)
2. [Schema, Query And Data Loading](./02-schema-query-and-data-loading.md)
3. [Roles, Privileges And Security](./03-roles-privileges-and-security.md)
4. [Backup And Restore](./04-backup-restore.md)
5. [High Availability And Replication](./05-high-availability-and-replication.md)
6. [Operations And Troubleshooting](./06-operations-and-troubleshooting.md)

## Production Mental Model

- PostgreSQL correctness dựa trên transaction, constraints, WAL và MVCC.
- `pg_dump`/`pg_restore` tốt cho logical backup; PITR/base backup/WAL archive cần cho RPO/RTO nghiêm túc.
- Role/privilege nên được thiết kế theo least privilege; app không dùng superuser.
- HA không chỉ là streaming replication; còn cần failover, replication slot, monitoring lag, backup và client routing.
- Extension, trigger, FDW và PL/pgSQL rất mạnh nhưng phải được quản trị như code production.

