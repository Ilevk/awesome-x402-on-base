# Awesome x402 on Base 🚀

> A curated collection of resources, tools, and knowledge about x402 protocol on Base chain, maintained by the Base Korea Developer Ambassador.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Base Chain](https://img.shields.io/badge/Chain-Base-blue.svg)](https://base.org)
[![x402 Protocol](https://img.shields.io/badge/Protocol-x402-green.svg)](https://www.x402.org)

## 📝 TL;DR

**What**: Korean documentation and guides for x402 payment protocol on Base chain
**Why**: Official x402 examples already use Base - we add comprehensive Korean tutorials
**How**: Git submodule links official code (`external/`) + Korean guides (`docs/korean/`)
**For**: Korean developers & global builders interested in Base-specific x402 implementations

**Quick Start**: [English Docs](https://docs.cdp.coinbase.com/x402/welcome) | [한글 가이드](./docs/korean/README.ko.md)

---

## 📖 About This Repository

This repository provides **Korean guides and documentation** for the x402 protocol on Base chain. Since the official x402 examples already use Base chain by default, we focus on creating comprehensive Korean tutorials and community resources.

**What's Inside:**
- 🔗 **Official Examples** (via Git submodule in `external/`) - Direct access to Coinbase's x402 examples
- 📝 **Korean Guides** (in `docs/korean/`) - Step-by-step Korean tutorials for each example
- 🔵 **Base-Specific Content** (in `examples/`) - Additional Base chain optimizations and use cases
- 🇰🇷 **Korean Community** - Resources for Korean developers

> **Note**: This repository complements the [official x402 repository](https://github.com/coinbase/x402) by providing Korean documentation and Base-focused content.

## 🔍 What is x402?

**x402** is an open-source payment protocol developed by Coinbase that revolutionizes internet-native payments by reviving the HTTP 402 status code that has been dormant for 26 years.

### Key Features

- ⚡ **Lightning Fast** - Payments processed in ~2 seconds
- 💰 **Ultra Low Cost** - Transaction fees < $0.0001, enabling micropayments as low as $0.001
- 🤖 **Machine-to-Machine** - Enable AI agents and IoT devices to autonomously pay for resources
- 🔗 **Chain Agnostic** - Supports Base, Solana, Polygon, Ethereum, and more
- 🌐 **HTTP Native** - Built on top of HTTP for seamless web integration

### How It Works

x402 leverages the HTTP 402 "Payment Required" status code to create a standardized payment layer for the internet. When a service requires payment, it returns a 402 response with payment instructions. Clients (including AI agents) can automatically process these payments using stablecoins like USDC, without requiring accounts, sessions, or complex authentication.

## 🎯 Why Base Chain?

**Base** is the optimal network for x402 protocol adoption:

- 🚀 **High Performance** - Fast finality and low latency
- 💵 **Minimal Fees** - Gas fees < $0.0001 for x402 transactions
- 🔐 **Ethereum Security** - L2 built on Ethereum with robust security
- 🌊 **Native Support** - x402 has first-class support for Base Sepolia and Base Mainnet
- 💎 **USDC Integration** - Native USDC as the default payment currency

Base provides the perfect infrastructure for x402's vision of enabling micropayments and machine-to-machine transactions at scale.

## 🌟 x402 Ecosystem

The x402 ecosystem is rapidly growing with support from major tech companies:

- **Coinbase** - Protocol creator and primary maintainer
- **Cloudflare** - Co-founder of x402 Foundation
- **Google** - Infrastructure integration
- **Visa** - Payment network partnership
- **AWS** - Cloud infrastructure support
- **Circle** - USDC stablecoin provider
- **Anthropic** - AI integration

### Recent Growth Metrics

- 📈 **163,600+** transactions in the last 7 days (+701.7%)
- 💰 **$140,200+** in transaction volume (+8,218.5%)
- 👥 **31,000+** unique buyers (+15,000%)

## 📁 Repository Structure

```
awesome-x402-on-base/
├── external/x402/          # 🔗 Git Submodule (Official x402 Repository)
│   └── examples/python/    # Official Python examples (read-only)
│
├── examples/               # 📝 Base-Specific Examples (This Repo)
│   └── base-specific/      # Base chain optimization examples
│
├── docs/korean/            # 🇰🇷 Korean Documentation
│   ├── quickstart/         # Quick start guides
│   ├── examples/           # Korean guides for official examples
│   └── base-chain/         # Base chain setup guides
│
└── resources/              # 📚 Additional Resources
    └── korean-community.md # Korean community links
```

**Clear Separation:**
- **`external/`** = Official x402 examples (via submodule, don't modify)
- **`examples/`** = Our Base-specific additions and advanced use cases
- **`docs/`** = Korean guides and tutorials for both

## 🚀 Quick Start

### For English Speakers
→ Start with [Official x402 Documentation](https://docs.cdp.coinbase.com/x402/welcome)

### 한국 개발자분들을 위해 🇰🇷
→ [한글 빠른 시작 가이드](./docs/korean/README.ko.md)에서 시작하세요

## 💡 Examples with Korean Guides

### Python Examples (Official Code + Korean Guides)

| Example | Official Code | Korean Guide |
|---------|---------------|--------------|
| **requests Client** | [→ Code](./external/x402/examples/python/clients/requests) | [→ 한글 가이드](./docs/korean/examples/python-requests-client.ko.md) |
| **httpx Client** | [→ Code](./external/x402/examples/python/clients/httpx) | [→ 한글 가이드](./docs/korean/examples/python-httpx-client.ko.md) |
| **FastAPI Server** | [→ Code](./external/x402/examples/python/servers) | [→ 한글 가이드](./docs/korean/examples/python-fastapi-server.ko.md) |
| **Discovery** | [→ Code](./external/x402/examples/python/discovery) | [→ 한글 가이드](./docs/korean/examples/python-discovery.ko.md) |

### Using the Submodule

First time setup:
```bash
# Clone this repository with submodules
git clone --recursive https://github.com/YOUR_USERNAME/awesome-x402-on-base.git

# Or if already cloned without --recursive
git submodule update --init --recursive
```

Access official examples:
```bash
cd external/x402/examples/python
# Follow the Korean guides in docs/korean/examples/
```

## 🗺️ Roadmap

### ✅ Phase 1: Foundation (Current)
- [x] Repository setup with Git submodule
- [x] Directory structure
- [ ] Korean README (README.ko.md)
- [ ] Python quickstart guide (Korean)
- [ ] Base Sepolia setup guide (Korean)

### 🔄 Phase 2: Korean Documentation
- [ ] requests client guide (Korean)
- [ ] httpx client guide (Korean)
- [ ] FastAPI server guide (Korean)
- [ ] Discovery example guide (Korean)
- [ ] USDC faucet guide (Korean)

### 🚀 Phase 3: Advanced Content
- [ ] AI agent integration tutorial
- [ ] API monetization guide
- [ ] Production deployment guide
- [ ] Gas optimization techniques

### 🌏 Phase 4: Community
- [ ] Korean Discord/Telegram
- [ ] Video tutorials (Korean)
- [ ] Workshop materials
- [ ] Hackathon starter kits

## 🤝 Contributing

Contributions are welcome! Whether you're building with x402, writing documentation, or sharing your experiences, we'd love to have your input.

### Ways to Contribute

- 🐛 Report bugs or issues
- 💡 Suggest new features or improvements
- 📝 Write tutorials or guides
- 🔧 Submit code examples or tools
- 🌐 Translate documentation
- 📢 Share your x402 projects

Please feel free to open an issue or submit a pull request.

## 📚 Resources

### Official x402 Resources
- 📖 [Official Documentation](https://docs.cdp.coinbase.com/x402/welcome)
- 💻 [x402 GitHub Repository](https://github.com/coinbase/x402)
- 📄 [x402 Whitepaper](https://www.x402.org/x402-whitepaper.pdf)
- 🌐 [x402 Website](https://www.x402.org)

### x402 SDK & Examples
- [Python SDK](https://github.com/coinbase/x402/tree/main/python/x402) - Official Python implementation
- [Python Examples](./external/x402/examples/python) - Client & server examples (via submodule)
- [TypeScript SDK](https://github.com/coinbase/x402/tree/main/typescript)
- [Go Implementation](https://github.com/coinbase/x402/tree/main/go)

### Base Chain Resources
- [Base Official Website](https://base.org)
- [Base Documentation](https://docs.base.org)
- [Base Sepolia Faucet](https://faucet.quicknode.com/base/sepolia)
- [Circle USDC Faucet](https://faucet.circle.com/)

### Announcements & Articles
- [Introducing x402 - Coinbase](https://www.coinbase.com/developer-platform/discover/launches/x402)
- [Launching the x402 Foundation - Cloudflare](https://blog.cloudflare.com/x402/)

### Korean Community (한국 커뮤니티)
- 🇰🇷 [한국어 가이드](./docs/korean/README.ko.md)
- 📱 Discord/Telegram (Coming Soon)
- 📝 [Korean Community Resources](./resources/korean-community.md)

## 📬 Connect

- **Base Korea Developer Community** - [Join us](./resources/korean-community.md)
- **Issues & Questions** - Open an issue in this repository
- **Discussions** - Share your thoughts in GitHub Discussions

## 📄 License

This repository is licensed under the [MIT License](LICENSE).

---

**Maintained with ❤️ by Base Korea Developer Ambassador**

*Building the future of internet-native payments, one commit at a time.*
