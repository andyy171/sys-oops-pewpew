# Learning Corner

Markdown knowledge base for infrastructure, cloud, DevOps, SRE, Linux,
networking, storage, Kubernetes, OpenStack, Ceph, observability, automation,
and related engineering topics.

## Repository Layout

- `docs/01-architecture/`: architecture fundamentals, design principles,
  tradeoffs, patterns, reliability, disaster recovery, and SRE concepts.
- `docs/02-core-infrastructure/`: Linux, networking, storage, databases,
  hardware, bare-metal operations, and Windows Server notes.
- `docs/03-compute-and-orchestration/`: compute platforms, Docker, Kubernetes,
  orchestration, and messaging or streaming systems.
- `docs/04-cloud-edge/`: cloud fundamentals, AWS, Azure, GCP, Huawei Cloud,
  OpenStack, and cloud operations.
- `docs/05-Infrastructure-Automation/`: observability, security hardening,
  CI/CD, infrastructure as code, Python automation, Git, and configuration
  management.
- `docs/06-programming-languages/`: programming language notes and
  cross-language implementation patterns.

## Local Development

Install dependencies:

```bash
pip install -r requirements.txt
```

Serve the documentation locally:

```bash
mkdocs serve
```

Build the static site:

```bash
mkdocs build
```

## Documentation Rules

- Keep reusable knowledge in canonical topic folders under `docs/`.
- Prefer Vietnamese explanations while keeping common technical terms in
  English when they are clearer.
- Do not commit local agent configuration, workspace metadata, secrets, private
  keys, large media files, or generated site output.
- Use relative links for local Markdown pages and keep path casing exact because
  CI runs on a case-sensitive Linux filesystem.
