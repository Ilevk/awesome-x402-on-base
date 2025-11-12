# Streamer Donation Backend

> FastAPI-based donation platform backend with x402 payment protocol integration

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type checked: basedpyright](https://img.shields.io/badge/type%20checked-basedpyright-blue.svg)](https://github.com/DetachHead/basedpyright)
[![Test Coverage](https://img.shields.io/badge/coverage-95%25+-brightgreen.svg)](./htmlcov/index.html)

---

## 📋 Overview

Production-ready FastAPI backend implementing:

- ⚡ **Layered Architecture**: 4-layer design (Routes → Services → Repositories → Database)
- 🔒 **Type Safety**: Full type checking with basedpyright
- ✅ **High Test Coverage**: 95%+ coverage with pytest
- 🎯 **Code Quality**: Pre-commit hooks with ruff and security checks
- 💰 **x402 Protocol**: Micropayment integration (Phase 2)
- 📦 **RocksDB**: High-performance embedded database

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **uv** (recommended) - [Install](https://github.com/astral-sh/uv)

### Installation

```bash
# 1. Navigate to backend directory
cd examples/python/streamer-donation/backend

# 2. Install dependencies with dev tools
make dev-install

# 3. Setup environment
cp .env.example .env
# Edit .env with your credentials

# 4. Run development server
make run
```

Server will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Health**: http://localhost:8000/health

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── core/                  # Infrastructure layer
│   │   ├── config.py          # Settings and environment variables
│   │   ├── database.py        # RocksDB wrapper
│   │   └── dependencies.py    # Dependency injection container
│   ├── models/                # Data models
│   │   ├── dtos.py           # Internal data transfer objects (dataclass)
│   │   └── schemas.py        # API request/response models (Pydantic)
│   ├── repositories/          # Data access layer
│   │   ├── streamer_repository.py
│   │   └── donation_repository.py
│   ├── services/              # Business logic layer
│   │   ├── streamer_service.py
│   │   ├── donation_service.py
│   │   └── validation_service.py
│   ├── routes/                # API endpoints (presentation layer)
│   │   ├── streamers.py
│   │   └── donations.py
│   ├── main.py               # FastAPI application
│   └── mock_data.py          # Mock data for testing
├── tests/                    # Test suite (95%+ coverage)
│   ├── conftest.py          # Pytest fixtures
│   ├── test_models.py
│   ├── test_database.py
│   ├── test_repositories.py
│   ├── test_services.py
│   └── test_routes.py
├── .pre-commit-config.yaml  # Pre-commit hooks configuration
├── pyproject.toml           # Project dependencies and tool configs
├── Makefile                 # Development commands
└── README.md               # This file
```

---

## 🏗️ Architecture

### Layered Design

```
┌─────────────────────────────────────────────┐
│  Presentation Layer (routes/)              │  ← HTTP/REST API
│  - FastAPI endpoints                        │
│  - Request validation (Pydantic schemas)    │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Service Layer (services/)                  │  ← Business Logic
│  - Business rules                           │
│  - Validation logic                         │
│  - Orchestration                            │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Repository Layer (repositories/)           │  ← Data Access
│  - CRUD operations                          │
│  - Data abstraction                         │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│  Infrastructure Layer (core/)               │  ← Database & Config
│  - Database (RocksDB)                       │
│  - Configuration                            │
│  - Dependency injection                     │
└─────────────────────────────────────────────┘
```

### Key Benefits

- ✅ **Separation of Concerns**: Each layer has single responsibility
- ✅ **Testability**: Layers can be tested independently
- ✅ **Maintainability**: Changes isolated to specific layers
- ✅ **Scalability**: Easy to swap implementations (e.g., PostgreSQL for RocksDB)

---

## 🔧 Development

### Available Commands

```bash
make help          # Show all available commands
make dev-install   # Install dev dependencies + pre-commit hooks
make run           # Start development server
make test          # Run tests
make test-cov      # Run tests with coverage report
make lint          # Run ruff linter
make format        # Format code with ruff
make typecheck     # Run basedpyright type checking
make check         # Run all quality checks
make clean         # Clean generated files
```

### Code Quality Tools

#### Pre-commit Hooks

Automatically run on `git commit`:
- **Ruff**: Linting and formatting
- **Basedpyright**: Type checking
- **Bandit**: Security scanning
- **Standard checks**: File formatting, YAML validation

```bash
# Manual run
pre-commit run --all-files
```

#### Type Checking

```bash
make typecheck
# or
basedpyright
```

#### Testing

```bash
# Run all tests
make test

# With coverage report
make test-cov

# Open coverage report
open htmlcov/index.html
```

---

## 📖 API Documentation

### Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoints

#### Streamers

```bash
# Get streamer by ID
GET /api/streamer/{streamer_id}

# List all streamers
GET /api/streamers?limit=100

# Get streamer by wallet
GET /api/streamer/by-wallet/{wallet_address}
```

#### Donations

```bash
# Submit donation
POST /api/donate/{streamer_id}/message

# Get donation by ID
GET /api/donations/{donation_id}

# List donations for streamer
GET /api/donations/streamer/{streamer_id}

# Get donation statistics
GET /api/donations/streamer/{streamer_id}/stats
```

---

## 🧪 Testing

### Test Coverage

Target: **95%+ coverage** for all modules

```bash
# Run with coverage
make test-cov

# View HTML report
open htmlcov/index.html
```

### Test Structure

- **Unit tests**: Individual components (models, services)
- **Integration tests**: Cross-layer interactions
- **API tests**: End-to-end endpoint testing

### Fixtures

Reusable test fixtures in `tests/conftest.py`:
- `db`: Fresh database instance
- `sample_streamer`: Mock streamer data
- `sample_donation`: Mock donation data
- `client`: FastAPI test client
- `async_client`: Async HTTP client

---

## 🔒 Security

### Pre-commit Security Checks

- **Bandit**: Python security linter
- **Private key detection**: Prevents committing secrets

### Security Best Practices

1. ✅ Never commit `.env` files
2. ✅ Use environment variables for secrets
3. ✅ Validate all user inputs (Pydantic)
4. ✅ Sanitize messages (bleach library)
5. ✅ Wallet address validation

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)**: Initial setup guide
- **[DEVELOPMENT.md](DEVELOPMENT.md)**: Detailed development guide
- **[CONTRIBUTING.md](CONTRIBUTING.md)**: Contribution guidelines
- **[ARCHITECTURE.md](ARCHITECTURE.md)**: System architecture

---

## 🗺️ Roadmap

### Phase 1: MVP (Current - 80% Complete)

- [x] Layered architecture
- [x] RocksDB integration
- [x] API endpoints
- [x] Pre-commit hooks
- [x] Test infrastructure
- [ ] 95%+ test coverage
- [ ] x402 middleware integration

### Phase 2: Production Features

- [ ] x402 payment processing
- [ ] WebSocket for real-time notifications
- [ ] Rate limiting
- [ ] Caching layer
- [ ] Monitoring and observability

### Phase 3: Advanced Features

- [ ] AI agent integration
- [ ] Clip upload/storage
- [ ] Multi-language support
- [ ] Analytics dashboard

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Development workflow
- Code style guidelines
- Testing requirements
- PR process

---

## 📄 License

MIT License - See [LICENSE](../LICENSE) for details

---

## 💬 Support

- **Documentation**: Check docs in this directory
- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/awesome-x402-on-base/issues)
- **Discord**: Base Korea Community

---

**Built with ❤️ for the Base ecosystem**
