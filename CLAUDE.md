# CLAUDE.md

## Project Overview

**Wenche** is a Python CLI/web tool for Norwegian holding companies and small enterprises to submit financial reports and tax documents to Norwegian authorities (Brønnøysundregistrene, Skatteetaten, Altinn). It handles annual accounts (årsregnskap), shareholder register reports (RF-1086), and tax returns (RF-1028/RF-1167).

## Tech Stack

- **Language:** Python 3.11+
- **Build:** Hatchling (pyproject.toml)
- **CLI:** Click
- **Web UI:** Streamlit
- **HTTP:** httpx
- **Auth:** Maskinporten via authlib (JWT grant)
- **Config:** YAML + python-dotenv
- **Docs:** MkDocs Material (Norwegian)
- **Tests:** pytest
- **CI/CD:** GitHub Actions

## Repository Structure

```
wenche/                  # Main source package
├── cli.py               # Click CLI entry point
├── models.py            # Core dataclasses (Selskap, Aarsregnskap, etc.)
├── auth.py              # Maskinporten authentication
├── altinn_client.py     # Altinn 3 API client
├── skd_client.py        # Skatteetaten API client
├── aarsregnskap.py      # Annual accounts submission
├── aksjonaerregister.py # Shareholder register (RF-1086)
├── skattemelding.py     # Tax return generation (RF-1028/RF-1167)
├── brg_xml.py           # BRG XML document generation
├── xbrl.py              # iXBRL document generation
├── systembruker.py      # Altinn system user management
└── ui.py                # Streamlit web interface
tests/                   # Pytest test suite
docs/                    # MkDocs documentation (Norwegian)
.github/workflows/       # CI: test, docs, publish, release
```

## Development Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Install with UI support
pip install -e ".[ui]"

# Run tests
pytest tests/ -v

# Build documentation
mkdocs build

# Run the CLI
wenche --help
```

## Key Conventions

- **Language:** Code identifiers and docstrings are in Norwegian (matching the domain)
- **Naming:** snake_case for files/functions, PascalCase for classes, UPPER_SNAKE_CASE for constants
- **Models:** Financial data structures use Python dataclasses with `@property` for computed values
- **File organization:** One module per submission type / domain concept
- **API clients:** Use context managers for resource management
- **Config:** Loaded from YAML via `yaml.safe_load()`, validated through dataclass constructors
- **Private functions:** Prefixed with underscore (`_les_resultat()`, `_row_id()`)

## Testing

- Tests live in `tests/` with shared fixtures in `conftest.py`
- Key fixtures: `eksempel_selskap()`, `eksempel_regnskap()`, `regnskap_med_utbytte()`
- Tests cover imports, model validation, XML/XBRL generation, and financial calculations
- CI runs pytest on Python 3.11 for pushes to main and feature branches

## CI/CD

- **test.yml:** Runs `pytest tests/ -v` on push to main/feature/fix/bump/docs branches and PRs
- **docs.yml:** Builds and deploys MkDocs to GitHub Pages
- **publish.yml:** Publishes to PyPI on version tags (`v*`) using trusted publishing
- **release.yml:** Creates GitHub releases on version tags

## Environment Variables

- `MASKINPORTEN_CLIENT_ID` – Client ID from Digdir
- `MASKINPORTEN_PRIVAT_NOKKEL` – Path to private RSA key
- `MASKINPORTEN_KID` – Key ID (UUID) from Digdir
- `WENCHE_ENV` – Environment: `test` or `prod` (default: prod)
- `ORG_NUMMER` – Organization number for system registration
- `SKD_TEST_ORG_NUMMER` – Synthetic org number for SKD testing (Tenor)

See `.env.example` for reference and `config.example.yaml` for full configuration options.

## Git Branch Conventions

- `main` – production branch
- `feature/*` – new features
- `fix/*` – bug fixes
- `bump/*` – version bumps
- `docs/*` – documentation changes
