# Streamer Donation System

> Direct donation platform for streamers powered by Base blockchain and x402 protocol

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

**English** | [한국어](./README.ko.md)

---

## 📋 Overview

The Streamer Donation System is a web platform that enables YouTube, Twitch, and other streamers to receive cryptocurrency donations **directly without intermediary platform fees**.

### Key Features

- ⚡ **Fast Payments**: ~2 second payment processing with x402 protocol
- 💰 **Low Fees**: Transaction fees < $0.0001 using Base blockchain
- 🎯 **Customizable**: Streamers can configure donation tiers and messages
- 💬 **Messaging**: Viewers can send support messages with donations
- 🔒 **Secure**: Non-custodial payments via Web3 wallets

### Technology Stack

- **Backend**: FastAPI (Python 3.10+)
- **Blockchain**: Base (Ethereum L2)
- **Payment Protocol**: x402
- **Database**: RocksDB
- **Frontend**: Vanilla JavaScript + Viem

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+**
- **uv** (Python package manager) - [Installation guide](https://github.com/astral-sh/uv)
- **Base Sepolia testnet wallet** with test tokens
- **CDP (Coinbase Developer Platform) account** - [Sign up](https://portal.cdp.coinbase.com/)

### 1. Clone Repository

```bash
git clone --recursive https://github.com/YOUR_USERNAME/awesome-x402-on-base.git
cd awesome-x402-on-base/examples/python/streamer-donation
```

### 2. Environment Setup

```bash
cd backend
cp .env.example .env
```

Edit `.env` file with your CDP credentials:

```bash
# .env
CDP_API_KEY_ID=your-api-key-id
CDP_API_KEY_SECRET=your-api-key-secret
CDP_WALLET_SECRET=your-wallet-secret
NETWORK=base-sepolia
```

### 3. Install Dependencies

```bash
uv sync
```

### 4. Run Server

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be running at `http://localhost:8000`.

### 5. Access in Browser

- **Landing Page**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Donation Page Example**: http://localhost:8000/donate/{streamer_id}

---

## 📖 Usage Guide

### Streamer Setup (Phase 1 - Mocked)

In Phase 1, streamer data is hardcoded in `app/mock_data.py`.

```python
# app/mock_data.py
MOCK_STREAMERS = {
    "logan": Streamer(
        id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        name="Logan",
        wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        platforms=["youtube", "twitch"],
        donation_tiers=[
            DonationTier(amount_usd=1.0, popup_message="Thank you! 💙"),
            DonationTier(amount_usd=5.0, popup_message="Amazing! 🎉"),
            DonationTier(amount_usd=10.0, popup_message="Legend! 🌟"),
        ],
        thank_you_message="Thanks for watching my stream!"
    ),
}
```

### Donation Flow

1. **Streamer**: Generate donation link and share in stream description/chat
   ```
   https://localhost:8000/donate/a1b2c3d4-e5f6-7890-abcd-ef1234567890
   ```

2. **Viewer**: Click link → Access donation page

3. **Viewer**: Select donation tier and enter message

4. **Viewer**: Connect Web3 wallet (MetaMask, Coinbase Wallet, etc.)

5. **Viewer**: Process payment via x402 protocol

6. **Viewer**: Confirm completion on thank you page

---

## 🏗️ Project Structure

```
streamer-donation/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── models.py            # Pydantic data models
│   │   ├── database.py          # RocksDB wrapper
│   │   ├── config.py            # Environment configuration
│   │   ├── mock_data.py         # Mocked streamer data
│   │   └── routes/
│   │       ├── streamers.py     # Streamer API
│   │       └── donations.py     # Donation API
│   ├── static/                  # CSS, JS, images
│   ├── templates/               # HTML templates
│   ├── tests/                   # Test code
│   ├── pyproject.toml           # Dependencies
│   └── .env.example             # Environment variables template
├── docs/                        # Additional documentation
├── PRD.md                       # Product Requirements Document
└── README.md                    # This file
```

---

## 🔌 API Endpoints

### Get Streamer Information

```http
GET /api/streamer/{streamer_id}
```

**Response Example**:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Logan",
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "platforms": ["youtube", "twitch"],
  "donation_tiers": [
    {
      "amount_usd": 1.0,
      "popup_message": "Thank you! 💙",
      "duration_ms": 3000
    }
  ]
}
```

### Donation Page (x402 Protected)

```http
GET /donate/{streamer_id}
```

This endpoint is protected by x402 protocol. Accessing without payment returns `402 Payment Required`.

### Submit Donation Message

```http
POST /api/donate/{streamer_id}/message
Content-Type: application/json

{
  "amount_usd": 5.0,
  "donor_address": "0x1234...",
  "message": "Great stream!",
  "tx_hash": "0xabcdef..."
}
```

See [API.md](./docs/API.md) for detailed API specifications.

---

## 🧪 Testing

### Run All Tests

```bash
uv run pytest
```

### Run with Coverage

```bash
uv run pytest --cov=app --cov-report=html
```

### Run Specific Test

```bash
uv run pytest tests/test_api.py -v
```

---

## 🔒 Security

### Implemented Security Measures

- ✅ **Wallet Address Validation**: Using Web3.is_address()
- ✅ **Amount Limits**: $0.01 - $1000 range
- ✅ **XSS Prevention**: HTML tag removal with bleach library
- ✅ **CORS Configuration**: Managed allowed domains list

### Important Notes

⚠️ **Private Key Security**:
- Never commit `.env` file to Git
- Separate development and production wallets
- Test only on Base Sepolia network

---

## 📚 Documentation

- [PRD (Product Requirements Document)](./PRD.md) - Product specifications
- [API Specification](./docs/API.md) - Detailed API documentation
- [System Architecture](./docs/ARCHITECTURE.md) - Overall system structure
- [Deployment Guide](./docs/DEPLOYMENT.md) - Production deployment

---

## 🗺️ Roadmap

### Phase 1: MVP (Current)
- [x] Project structure and configuration
- [x] RocksDB integration
- [ ] x402 middleware integration
- [ ] Donation page UI
- [ ] Web3 wallet connection
- [ ] Thank you page

### Phase 2: AI Agent Integration
- [ ] Google A2A protocol research
- [ ] Natural language donation commands
- [ ] Real-time notifications (WebSocket)
- [ ] Clip upload/storage

---

## 🤝 Contributing

This project is open source and welcomes community contributions!

### How to Contribute

1. Fork this repository
2. Create a Feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

### Code Style

- **Python**: Black (line length 100) + Ruff
- **Comments/Docstrings**: English
- **Commit Messages**: [Conventional Commits](https://www.conventionalcommits.org/) format

---

## 📞 Contact & Support

- **GitHub Issues**: [Issues page](https://github.com/YOUR_USERNAME/awesome-x402-on-base/issues)
- **Discord**: Base Korea Community
- **Author**: Logan (Base Korea Developer Ambassador)

---

## 📄 License

This project is distributed under the MIT License. See [LICENSE](../../LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Coinbase](https://www.coinbase.com/) - For Base blockchain and CDP Platform
- [x402 Protocol](https://github.com/coinbase/x402) - For innovative micropayment protocol
- Base Korea Community - For feedback and testing

---

**Built with ❤️ for the Base ecosystem**
