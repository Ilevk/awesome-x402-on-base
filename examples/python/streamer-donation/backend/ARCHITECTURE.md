# Architecture Documentation

## Overview

This application implements a **Layered Architecture** pattern with **Dependency Injection** to ensure clean separation of concerns, testability, and maintainability.

## Architecture Layers

```
┌─────────────────────────────────────────────────────┐
│         Presentation Layer (routes/)                │
│   ├─ streamers.py   (Streamer endpoints)          │
│   └─ donations.py   (Donation endpoints)          │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│       Business Logic Layer (services/)              │
│   ├─ validation_service.py  (Input validation)    │
│   ├─ streamer_service.py    (Streamer logic)      │
│   └─ donation_service.py    (Donation logic)      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│         Data Access Layer (repositories/)           │
│   ├─ streamer_repository.py  (Streamer data)      │
│   └─ donation_repository.py  (Donation data)      │
└─────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────┐
│         Infrastructure Layer                         │
│   ├─ database.py   (RocksDB wrapper)              │
│   ├─ config.py     (Settings)                     │
│   └─ models.py     (Data models)                  │
└─────────────────────────────────────────────────────┘
```

## Layer Responsibilities

### 1. Presentation Layer (`app/routes/`)

**Purpose**: Handle HTTP requests and responses

**Responsibilities**:
- Route definition and URL mapping
- Request parsing and validation (Pydantic)
- HTTP status code management
- Error handling and response formatting
- **NO business logic**

**Example** (`routes/donations.py:41-80`):
```python
async def submit_donation_message(
    streamer_id: str,
    donation_data: DonationMessageCreate,
    donation_service: Annotated[DonationService, Depends(get_donation_service)],
) -> DonationResponse:
    try:
        # Delegate to service layer
        return donation_service.process_donation(streamer_id, donation_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

### 2. Business Logic Layer (`app/services/`)

**Purpose**: Implement core business rules and workflows

**Responsibilities**:
- Business rule enforcement
- Workflow orchestration
- Data validation and sanitization
- Cross-domain logic coordination
- **NO direct database access**

**Services**:

#### `ValidationService` (`services/validation_service.py`)
- Wallet address validation
- Message sanitization (XSS prevention)
- Amount range validation
- Tier matching logic

#### `StreamerService` (`services/streamer_service.py`)
- Streamer retrieval by ID/wallet
- Donation tier matching
- Streamer status validation
- Tier amount extraction

#### `DonationService` (`services/donation_service.py`)
- Complete donation processing workflow
- Multi-step validation orchestration
- Statistics calculation
- Donation retrieval

**Example** (`services/donation_service.py:42-92`):
```python
def process_donation(
    self, streamer_id: str, donation_data: DonationMessageCreate
) -> DonationResponse:
    # 1. Validate streamer exists
    streamer = self.streamer_service.get_streamer_by_id(streamer_id)
    if streamer is None:
        raise ValueError(f"Streamer not found: {streamer_id}")

    # 2. Validate wallet addresses
    if not self.validation_service.validate_wallet_address(...):
        raise ValueError("Invalid donor address")

    # 3-7. Additional validation and processing steps
    ...
```

### 3. Data Access Layer (`app/repositories/`)

**Purpose**: Abstract database operations

**Responsibilities**:
- CRUD operations
- Data retrieval and persistence
- Query construction
- Database-specific logic encapsulation
- **NO business logic**

**Repositories**:

#### `StreamerRepository` (`repositories/streamer_repository.py`)
- `get_by_id()`: Retrieve streamer by UUID
- `get_by_wallet()`: Retrieve streamer by wallet address
- `list_all()`: List all streamers
- `save()`: Persist streamer
- `exists()`: Check existence

#### `DonationRepository` (`repositories/donation_repository.py`)
- `get_by_id()`: Retrieve donation by UUID
- `list_by_streamer()`: List donations for streamer
- `save()`: Persist donation
- `get_stats()`: Calculate statistics
- `exists()`: Check existence

**Example** (`repositories/streamer_repository.py:19-31`):
```python
def get_by_id(self, streamer_id: str) -> Optional[Streamer]:
    return self.db.get_streamer(streamer_id)

def save(self, streamer: Streamer) -> None:
    self.db.put_streamer(streamer)
    logger.debug(f"Saved streamer: {streamer.name}")
```

### 4. Infrastructure Layer

**Purpose**: Provide technical capabilities

**Components**:
- `database.py`: RocksDB connection and operations
- `config.py`: Environment configuration
- `models.py`: Pydantic data models
- `dependencies.py`: Dependency injection container

## Dependency Injection

### Container (`app/dependencies.py`)

Centralized dependency management using FastAPI's `Depends()` system.

**Factory Functions**:

```python
# Infrastructure
@lru_cache()
def get_settings() -> Settings:
    return Settings()

def get_db() -> DonationDB:
    global _db_instance
    if _db_instance is None:
        raise RuntimeError("Database not initialized")
    return _db_instance

# Repositories
def get_streamer_repository() -> StreamerRepository:
    db = get_db()
    return StreamerRepository(db)

# Services
def get_validation_service() -> ValidationService:
    settings = get_settings()
    return ValidationService(
        min_donation_usd=settings.min_donation_usd,
        max_donation_usd=settings.max_donation_usd,
    )

def get_donation_service() -> DonationService:
    db = get_db()
    validation_service = get_validation_service()
    streamer_service = get_streamer_service()
    return DonationService(db, validation_service, streamer_service)
```

**Usage in Routes**:

```python
from fastapi import Depends
from typing import Annotated

async def submit_donation_message(
    streamer_id: str,
    donation_data: DonationMessageCreate,
    donation_service: Annotated[DonationService, Depends(get_donation_service)],
) -> DonationResponse:
    return donation_service.process_donation(streamer_id, donation_data)
```

## Lifecycle Management

### Application Startup/Shutdown

FastAPI lifespan context manager (`main.py:24-51`):

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    settings = get_settings()
    db = init_db(settings.rocksdb_path)
    init_mock_data_in_db(db)
    logger.info("Application started")

    yield

    # Shutdown
    close_db()
    logger.info("Application shutdown complete")

app = FastAPI(lifespan=lifespan)
```

## Benefits of This Architecture

### 1. **Separation of Concerns**
- Each layer has a single, well-defined responsibility
- Changes in one layer don't cascade to others
- Clear boundaries between HTTP, business logic, and data access

### 2. **Testability**
- Services can be tested without HTTP layer
- Mock repositories for service testing
- Mock services for route testing
- Independent layer testing

**Example Test**:
```python
def test_process_donation():
    # Mock dependencies
    mock_db = Mock()
    mock_validation = Mock()
    mock_streamer = Mock()

    # Create service with mocks
    service = DonationService(mock_db, mock_validation, mock_streamer)

    # Test business logic in isolation
    result = service.process_donation(...)
    assert result.donation_id is not None
```

### 3. **Maintainability**
- Easy to locate code (routing vs. logic vs. data)
- Clear dependency flow (top-to-bottom)
- Consistent patterns across application
- Self-documenting structure

### 4. **Reusability**
- Services can be used by multiple routes
- Repositories can be used by multiple services
- Validation logic centralized and reusable

### 5. **Extensibility**
- Add new routes without touching business logic
- Add new services without modifying routes
- Swap database implementation by changing repository
- Add caching, logging, monitoring at appropriate layers

## Data Flow Example

**Donation Submission Flow**:

```
1. HTTP POST /api/donate/{streamer_id}/message
   ↓
2. donations.py:submit_donation_message()
   - Parse request body
   - Inject DonationService
   ↓
3. DonationService.process_donation()
   - Validate streamer (via StreamerService)
   - Validate addresses (via ValidationService)
   - Find matching tier (via StreamerService)
   - Sanitize message (via ValidationService)
   - Create donation record
   ↓
4. DonationDB.put_donation()
   - Serialize to JSON
   - Write to RocksDB
   ↓
5. Return DonationResponse
   - Popup message
   - Duration
   ↓
6. HTTP 201 Created
```

## Testing Strategy

### Unit Tests

**Service Layer**:
```python
# Test business logic in isolation
def test_validation_service():
    service = ValidationService(min_donation_usd=0.01, max_donation_usd=1000.0)
    is_valid, error = service.validate_amount_range(5.0)
    assert is_valid is True
    assert error is None
```

**Repository Layer**:
```python
# Test data access logic
def test_streamer_repository():
    mock_db = Mock()
    repo = StreamerRepository(mock_db)
    repo.get_by_id("test-id")
    mock_db.get_streamer.assert_called_once_with("test-id")
```

### Integration Tests

**API Endpoints**:
```python
from fastapi.testclient import TestClient

def test_submit_donation():
    client = TestClient(app)
    response = client.post("/api/donate/streamer-id/message", json={...})
    assert response.status_code == 201
    assert "donation_id" in response.json()
```

## Future Enhancements

### Potential Improvements

1. **Caching Layer**
   - Add Redis caching in Service layer
   - Cache streamer lookups
   - Cache donation statistics

2. **Event System**
   - Publish donation events
   - Webhook notifications
   - Analytics tracking

3. **Transaction Management**
   - Add Unit of Work pattern
   - Transaction boundaries
   - Rollback support

4. **Authentication/Authorization**
   - Add auth middleware
   - Role-based access control
   - API key management

5. **Observability**
   - Structured logging
   - Metrics collection (Prometheus)
   - Distributed tracing (OpenTelemetry)

## File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app + lifespan
│   ├── config.py                  # Settings
│   ├── models.py                  # Pydantic models
│   ├── database.py                # RocksDB wrapper
│   ├── dependencies.py            # DI container
│   ├── mock_data.py               # Test data
│   │
│   ├── routes/                    # Presentation Layer
│   │   ├── __init__.py
│   │   ├── streamers.py
│   │   └── donations.py
│   │
│   ├── services/                  # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── validation_service.py
│   │   ├── streamer_service.py
│   │   └── donation_service.py
│   │
│   └── repositories/              # Data Access Layer
│       ├── __init__.py
│       ├── streamer_repository.py
│       └── donation_repository.py
│
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

## References

- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Service Layer Pattern](https://martinfowler.com/eaaCatalog/serviceLayer.html)
- [Layered Architecture](https://www.oreilly.com/library/view/software-architecture-patterns/9781491971437/ch01.html)
