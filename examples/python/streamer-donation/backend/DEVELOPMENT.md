# Development Guide

## Quick Start

### Prerequisites

- Python 3.10 or higher
- `uv` package manager (recommended) or `pip`
- Base Sepolia testnet access (for testing)

### Installation

1. **Clone and navigate**:
```bash
cd examples/python/streamer-donation/backend
```

2. **Create environment file**:
```bash
cp .env.example .env
```

3. **Edit `.env` file** with your credentials:
```bash
# Required for Phase 1 (optional, mocked)
NETWORK=base-sepolia
CDP_API_KEY_ID=your-api-key-id
CDP_API_KEY_SECRET=your-api-key-secret
CDP_WALLET_SECRET=your-wallet-secret

# Database path
ROCKSDB_PATH=./data/donations.db

# CORS allowed origins
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000

# Donation limits (USD)
MIN_DONATION_USD=0.01
MAX_DONATION_USD=1000.0
```

4. **Install dependencies**:

Using `uv` (recommended):
```bash
uv sync
```

Using `pip`:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows

pip install -e .
```

### Run Development Server

```bash
# Using uv
uv run uvicorn app.main:app --reload

# Using pip
uvicorn app.main:app --reload
```

Server will start at: http://localhost:8000

## API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Streamer Endpoints

#### Get Streamer by ID
```bash
GET /api/streamer/{streamer_id}

curl http://localhost:8000/api/streamer/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

#### List All Streamers
```bash
GET /api/streamers?limit=100

curl http://localhost:8000/api/streamers
```

#### Get Streamer by Wallet
```bash
GET /api/streamer/by-wallet/{wallet_address}

curl http://localhost:8000/api/streamer/by-wallet/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

### Donation Endpoints

#### Submit Donation
```bash
POST /api/donate/{streamer_id}/message

curl -X POST http://localhost:8000/api/donate/a1b2c3d4-e5f6-7890-abcd-ef1234567890/message \
  -H "Content-Type: application/json" \
  -d '{
    "amount_usd": 5.0,
    "donor_address": "0x1234567890123456789012345678901234567890",
    "message": "Great stream!",
    "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
  }'
```

#### Get Donation by ID
```bash
GET /api/donations/{donation_id}

curl http://localhost:8000/api/donations/{donation-uuid}
```

#### List Donations for Streamer
```bash
GET /api/donations/streamer/{streamer_id}?limit=100

curl http://localhost:8000/api/donations/streamer/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

#### Get Donation Statistics
```bash
GET /api/donations/streamer/{streamer_id}/stats

curl http://localhost:8000/api/donations/streamer/a1b2c3d4-e5f6-7890-abcd-ef1234567890/stats
```

## Mock Data

The application comes with 3 mock streamers pre-loaded:

### 1. Logan
- **ID**: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
- **Wallet**: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb`
- **Platforms**: YouTube, Twitch
- **Tiers**: $1, $5, $10, $50

### 2. Kim
- **ID**: `b2c3d4e5-f6a7-4b89-c012-defabcde3456`
- **Wallet**: `0x8765432109fedcba8765432109fedcba87654321`
- **Platforms**: Twitch
- **Tiers**: $2, $5, $10

### 3. Alex
- **ID**: `c3d4e5f6-a7b8-4c90-d123-efabcdef4567`
- **Wallet**: `0xabcdef1234567890abcdef1234567890abcdef12`
- **Platforms**: YouTube
- **Tiers**: $3, $7, $15

## Testing

### Manual Testing with curl

1. **Get a streamer**:
```bash
curl http://localhost:8000/api/streamer/a1b2c3d4-e5f6-7890-abcd-ef1234567890 | jq
```

2. **Submit a donation**:
```bash
curl -X POST http://localhost:8000/api/donate/a1b2c3d4-e5f6-7890-abcd-ef1234567890/message \
  -H "Content-Type: application/json" \
  -d '{
    "amount_usd": 5.0,
    "donor_address": "0x1234567890123456789012345678901234567890",
    "message": "Amazing content!",
    "tx_hash": "0xabcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890"
  }' | jq
```

3. **List donations**:
```bash
curl http://localhost:8000/api/donations/streamer/a1b2c3d4-e5f6-7890-abcd-ef1234567890 | jq
```

4. **Get statistics**:
```bash
curl http://localhost:8000/api/donations/streamer/a1b2c3d4-e5f6-7890-abcd-ef1234567890/stats | jq
```

### Interactive Testing

Use Swagger UI at http://localhost:8000/docs for interactive API testing with auto-generated forms.

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

**Quick Summary**:

```
Routes (HTTP) → Services (Business Logic) → Repositories (Data Access) → Database (RocksDB)
```

### Key Directories

- **`app/routes/`**: FastAPI endpoints (Presentation Layer)
- **`app/services/`**: Business logic (Service Layer)
- **`app/repositories/`**: Data access (Repository Layer)
- **`app/dependencies.py`**: Dependency injection container
- **`app/database.py`**: RocksDB wrapper
- **`app/models.py`**: Pydantic data models

## Common Issues

### Database Already Exists Error

**Symptom**: `rocksdb.errors.RocksIOError: IO error: lock hold by current process`

**Solution**:
```bash
# Stop all running instances
killall uvicorn

# Remove lock file
rm -rf ./data/donations.db/LOCK

# Restart server
uv run uvicorn app.main:app --reload
```

### Import Errors

**Symptom**: `ModuleNotFoundError: No module named 'app'`

**Solution**:
```bash
# Make sure you're in the backend directory
cd examples/python/streamer-donation/backend

# Reinstall in editable mode
uv sync
# or
pip install -e .
```

### Port Already in Use

**Symptom**: `Address already in use: bind()`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

## Database Management

### Inspect RocksDB Data

```python
import rocksdb

db = rocksdb.DB("./data/donations.db", rocksdb.Options())

# List all keys
it = db.iterkeys()
it.seek_to_first()
for key in it:
    print(key.decode())
```

### Reset Database

```bash
# Stop server
# Remove database directory
rm -rf ./data/donations.db

# Restart server (will recreate with mock data)
uv run uvicorn app.main:app --reload
```

### Backup Database

```bash
cp -r ./data/donations.db ./data/donations.db.backup
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NETWORK` | `base-sepolia` | Base network (base-sepolia or base) |
| `CDP_API_KEY_ID` | - | Coinbase Developer Platform API Key ID |
| `CDP_API_KEY_SECRET` | - | CDP API Key Secret |
| `CDP_WALLET_SECRET` | - | CDP Wallet Secret |
| `ROCKSDB_PATH` | `./data/donations.db` | Path to RocksDB database |
| `ALLOWED_ORIGINS` | `http://localhost:3000,...` | CORS allowed origins (comma-separated) |
| `MIN_DONATION_USD` | `0.01` | Minimum donation amount in USD |
| `MAX_DONATION_USD` | `1000.0` | Maximum donation amount in USD |

## Logging

Application logs are written to stdout with the following format:

```
2025-11-10 23:00:00 - app.main - INFO - Starting Streamer Donation System
2025-11-10 23:00:01 - app.database - INFO - Database initialized at: ./data/donations.db
2025-11-10 23:00:02 - app.mock_data - INFO - Mock streamer data loaded
```

### Log Levels

- **INFO**: Startup, shutdown, successful operations
- **DEBUG**: Detailed execution flow (set `log_level="debug"` in uvicorn)
- **WARNING**: Validation failures, missing resources
- **ERROR**: Exception handling, system errors

### Enable Debug Logging

```bash
uvicorn app.main:app --reload --log-level debug
```

## Performance Tips

### RocksDB Tuning

Edit `app/database.py` for production use:

```python
opts = rocksdb.Options()
opts.create_if_missing = True
opts.max_open_files = 300000
opts.write_buffer_size = 67108864  # 64MB
opts.max_write_buffer_number = 3
opts.target_file_size_base = 67108864  # 64MB
opts.compression = rocksdb.CompressionType.lz4_compression
```

### Connection Pooling

For high traffic, consider adding connection pooling in `dependencies.py`.

## Next Steps

1. **Integrate x402 Protocol**: Add actual payment processing
2. **Add Frontend**: Build React/Vue.js donation interface
3. **Implement Authentication**: Secure API endpoints
4. **Add WebSocket**: Real-time donation notifications
5. **Deploy to Production**: Use Base Mainnet

## Support

- **Documentation**: See [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
- **Issues**: Report bugs via GitHub Issues
- **Discord**: Join Base Korea Developer community

## License

MIT License - See [LICENSE](../LICENSE) file for details
