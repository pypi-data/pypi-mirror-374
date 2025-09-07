# 🌍 DigitalMeve — The .MEVE Standard

👉 The first global platform to certify and verify the authenticity of your documents.

![quality](https://img.shields.io/badge/quality-passing-brightgreen)
![tests](https://img.shields.io/badge/tests-passing-brightgreen)
[![publish](https://github.com/BACOUL/digitalmeve/actions/workflows/publish.yml/badge.svg)](https://github.com/BACOUL/digitalmeve/actions/workflows/publish.yml)
![coverage](https://img.shields.io/badge/coverage-90%25-green)

![DigitalMeve](https://img.shields.io/badge/DigitalMeve-v1.7.1-blue)
[![PyPI version](https://img.shields.io/pypi/v/digitalmeve.svg)](https://pypi.org/project/digitalmeve/)
![Python](https://img.shields.io/pypi/pyversions/digitalmeve.svg)

![downloads](https://img.shields.io/badge/downloads-2k-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Security](https://img.shields.io/badge/Security%20(Bandit%20%26%20pip--audit)-passing-brightgreen)
![Analyze](https://img.shields.io/badge/Analyze%20(CodeQL)-passing-brightgreen)

## 📑 Table of Contents

1. [Overview](#overview)
2. [🚀 Patches Snapshot](#patches)
3. [📖 TL;DR](#tldr)
4. [🔧 Quickstart](#quickstart)
5. [✨ Features](#features)
6. [📚 Documentation](#documentation)
7. [🧪 Examples](#examples)
8. [🔑 Certification Levels](#certification-levels)
9. [🛡 Security](#security)
10. [📊 Use Cases](#use-cases)
11. [🚀 Roadmap](#roadmap)
12. [🌐 Web Integration](#web-integration)
13. [💻 Development & Contribution](#development)
14. [📦 Releases](#releases)
15. [⚖ License](#license)

---

<a id="overview"></a>
## 1. Overview

**DigitalMeve** provides a **fast and universal** way to verify the authenticity of any `.meve` proof.

Verification ensures:
- **Integrity** → the document has not been tampered with (SHA-256 validation).
- **Timestamp** → the proof contains a valid UTC timestamp.
- **Issuer** → the identity level (Personal, Pro, Official) matches expectations.

---

<a id="patches"></a>
## 2. 🚀 Patches Snapshot (already implemented)

- ✅ **Core library**: `generator.py` + `verifier.py`
- ✅ **CLI**: `digitalmeve generate / verify / inspect`
- ✅ **Tests**: `pytest` passing on Python 3.10 → 3.12
- ✅ **Official Schema**: [`schemas/meve-1.schema.json`](schemas/meve-1.schema.json)
- ✅ **CI/CD GitHub Actions**:
  - [tests.yml](.github/workflows/tests.yml)
  - [quality.yml](.github/workflows/quality.yml)
  - [publish.yml](.github/workflows/publish.yml)
- ✅ **Docs**: overview, specification, guides, roadmap, security, API usage
- ✅ **Examples**: reproducible scripts (`examples/make_examples.sh`)
- ✅ **Governance**: [LICENSE](LICENSE), [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md), [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md)

---

<a id="tldr"></a>
## 3. 📖 TL;DR

**DigitalMeve** defines the universal format `.meve` (Memory Verified) to timestamp, hash, and certify digital documents.

👉 Goal: make `.meve` the **“PDF of digital proof”**.

Why `.meve`?
- **Existence** → the file existed at a given time.
- **Integrity** → SHA-256 hash guarantees no tampering.
- **Authenticity** → issuer is visible.
- **Metadata** → optional custom key/values.
- **Portable** → sidecar `.meve.json` works with any file type.


## 4. 🔧 Quickstart <a id="quickstart"></a>

### Install

pip install digitalmeve

CLI

digitalmeve generate path/to/file.pdf --issuer "Alice"
digitalmeve verify path/to/file.pdf.meve.json --issuer "Alice"
digitalmeve inspect path/to/file.pdf.meve.json

Python API

from digitalmeve.generator import generate_meve
from digitalmeve.verifier import verify_meve

proof = generate_meve("mydoc.pdf", issuer="Alice")
ok, info = verify_meve(proof, expected_issuer="Alice")
print(ok, info["subject"]["hash_sha256"])

✅ With .meve, you can prove existence, integrity, and authenticity in seconds.

## 5. ✨ Features <a id="features"></a>

- **SHA-256 hashing** → guarantees file integrity
- **Timestamp (UTC ISO-8601)** → proof of existence at a given time
- **Issuer levels** → Personal / Pro / Official
- **JSON Schema validation** → machine-verifiable against [`schemas/meve-1.schema.json`](schemas/meve-1.schema.json)
- **Metadata embedding** → free-form key/values (author, project, notes…)
- **Sidecar `.meve.json`** → scalable for any file type or size
- **CLI & Python API** → generate, verify, inspect in seconds
- **CI/CD ready** → GitHub Actions (tests, quality, publish)

## 6. 📚 Documentation <a id="documentation"></a>

- [Overview](docs/overview.md)
- [Specification](docs/specification.md)
- [Generator Guide](docs/generator-guide.md)
- [Verification Guide](docs/verification-guide.md)
- [API Usage](docs/API_USAGE.md)
- [Security](docs/security.md)
- [Examples](docs/examples.md)
- [Pro](docs/PRO.md)
- [Official](docs/OFFICIAL.md)
- [Roadmap](docs/roadmap.md)
- [FAQ](docs/faq.md)
- [Glossary](docs/glossary.md)

## 7. 🧪 Examples <a id="examples"></a>

- Scripts disponibles :
  - [make_examples.sh](examples/make_examples.sh) → génère des fichiers `.meve`
  - [verify_examples.sh](examples/verify_examples.sh) → vérifie les preuves générées

- Ressources complémentaires :
  - [examples/](examples/) (répertoire complet)
  - [docs/examples.md](docs/examples.md) (documentation détaillée)

## 8. 🔑 Certification Levels <a id="certification-levels"></a>

- **Personal** → auto-certification (preuve d’existence uniquement)
- **Pro** → vérification par e-mail (identité liée à un professionnel réel)
- **Official** → vérification institutionnelle (DNS / organisation validée)

ℹ️ Le niveau est déterminé par le **verifier**, et non auto-déclaré.

## 9. 🛡 Security <a id="security"></a>

- **Hashing (SHA-256) & immutability** → toute modification invalide la preuve
- **Schema validation** (`MEVE/1`) → validation automatique contre le schéma officiel
- **Pro verification** → authentification par e-mail (magic-link)
- **Official verification** → vérification DNS via enregistrement TXT `_meve.<domaine>`
- **Ed25519-ready** → support des signatures numériques (`key_id`, `signature`)
- **Transparency-ready** → intégration future dans des journaux de transparence

🔐 Pour les détails de sécurité et la divulgation responsable, voir [SECURITY.md](SECURITY.md).

## 10. 📊 Use Cases <a id="use-cases"></a>

DigitalMeve can be used across different contexts:

- **Individuals** → authorship proof, personal archives, evidence of existence
- **Professionals** → invoices, contracts, certifications, automation workflows
- **Institutions** → diplomas, tenders, official archives, public records

✅ The `.meve` standard ensures **existence, integrity, and authenticity** regardless of the use case.

## 11. 🚀 Roadmap <a id="roadmap-snapshot"></a>

The project is evolving in clear phases:

- **Phase 1 (MVP)** → core library (`generator`, `verifier`), CLI, schema v1, CI/CD pipelines
- **Phase 2 (≤ 6 months)** → Pro/Official onboarding, PDF/PNG embedding, public API, web integration
- **Phase 3 (1–2 years)** → standardization, external integrations, transparency logs, broader adoption

✅ The roadmap is tracked in [`docs/roadmap.md`](docs/roadmap.md).

## 12. 🌐 Web Integration <a id="web-integration-planned"></a>

Planned integration with web services and APIs:

- **Endpoints (future)**
  - `POST /api/generate` → returns `.meve.json` or embedded `.meve.pdf/.png`
  - `POST /api/verify` → returns `{ ok, info }` JSON object

- **Integration with Framer / Websites**
  - Simple drag-and-drop of documents
  - Proof verification directly in the browser

- **Security for the API**
  - CORS enabled (restricted in production)
  - X-API-Key required for private endpoints

📌 More details: [`docs/web-integration.md`](docs/web-integration.md)

## 13. 💻 Development & Contribution <a id="development--contribution"></a>

We welcome contributions from the community 🤝

### 🛠 Setup (local dev)

# Clone the repository
git clone https://github.com/BACOUL/digitalmeve.git
cd digitalmeve

# Install in editable mode with dev dependencies
pip install -e .[dev]

🧪 Run tests

pytest -q --cov=digitalmeve --cov-report=term-missing

📐 Code style

Linting: Ruff

Formatting: Black

Type checking: mypy


📜 Contribution Guidelines

Please read CONTRIBUTING.md before submitting a PR.

Follow CODE_OF_CONDUCT.md.

All new code should include tests.


✅ Contributions = issues, documentation, code, and feedback are all welcome!

## 14. 📦 Releases <a id="releases"></a>

DigitalMeve uses **semantic versioning** (MAJOR.MINOR.PATCH).

### 🔄 Release process
1. Bump version in `pyproject.toml`
2. Update [CHANGELOG.md](CHANGELOG.md)
3. Commit & tag:

   git commit -am "chore(release): v1.x.x"
   git tag v1.x.x
   git push --tags

   4. GitHub Actions (publish.yml) will automatically publish to PyPI.



📦 Current version

Development: 1.7.1-dev

Stable: see PyPI DigitalMeve


📝 Changelog

See CHANGELOG.md for a history of added / changed / fixed features.

✅ Guarantee: the latest GitHub tag = latest PyPI release.

## 15. ⚖ License <a id="license"></a>

DigitalMeve is released under the **MIT License**.

- You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software.
- Attribution is required: include the original copyright and license notice in any copy.
- The software is provided **“as is”**, without warranty of any kind.

📄 See the full license text here → [LICENSE](LICENSE)
