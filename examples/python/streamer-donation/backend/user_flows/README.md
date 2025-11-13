# User Flows

This directory contains practical user flow examples for the Streamer Donation System.

## 📝 Example List

### 1. `donation_flow_example.py` - Complete Donation Flow

Demonstrates a full scenario of searching for your favorite streamer and donating via x402.

**Scenario:**
1. Search by streamer name
2. Check available donation tiers
3. Access x402-protected donation page
4. Select donation amount and message
5. Submit donation
6. Verify donation
7. View streamer statistics

---

## 🚀 How to Run

### Prerequisites

1. **Backend Server Running**
   ```bash
   cd /path/to/backend
   uv run uvicorn app.main:app --reload
   ```

2. **Environment Variables Setup**

   Configure the following via `.env` file or environment variables:
   ```bash
   # API Server URL
   API_BASE_URL=http://localhost:8000

   # Donor Wallet Private Key (for testnet)
   PRIVATE_KEY=0xac0974bec39a17e36f4ac7d1d5f1e3fe...

   # Network (base-sepolia or base)
   NETWORK=base-sepolia
   ```

   ⚠️ **Security Notice:**
   - Only use testnet Private Keys
   - Never use mainnet Private Keys
   - Ensure `.env` is included in `.gitignore`

### Execution

```bash
# Navigate to examples directory
cd user_flows

# Run the example
python donation_flow_example.py
```

---

## 📋 Example Output

```
================================================================================
🎮 Streamer Donation Flow Example - x402 on Base
================================================================================
Donor Address: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
Network: base-sepolia
API URL: http://localhost:8000
================================================================================

Step 1: Search for your favorite streamer
--------------------------------------------------------------------------------
Enter streamer name to search (or press Enter for 'Logan'): Logan
🔍 Searching for streamer: 'Logan'...
   Found 2 total streamers
✅ Found streamer: Logan (a1b2c3d4-e5f6-7890-abcd-ef1234567890)

Step 2: View available donation tiers
--------------------------------------------------------------------------------
💰 Available donation tiers for Logan:
------------------------------------------------------------
1. $1.00 USD
   💬 Message: Thank you! 💙
   ⏱️  Duration: 3.0s

2. $5.00 USD
   💬 Message: Amazing! 🎉
   ⏱️  Duration: 5.0s

3. $10.00 USD
   💬 Message: Legendary support! 🚀
   ⏱️  Duration: 10.0s

Step 3: Select donation amount
--------------------------------------------------------------------------------
Available amounts: $1.00, $5.00, $10.00
Enter donation amount (or press Enter for $1.00): 5

Step 4: Add a custom message (optional)
--------------------------------------------------------------------------------
Enter your message (or press Enter to skip): Keep up the great content!

Step 5: Access x402-protected donation page
--------------------------------------------------------------------------------
🔐 Accessing x402-protected donation page...
   Endpoint: GET /donate/a1b2c3d4-e5f6-7890-abcd-ef1234567890
   💳 Server requires payment (402 Payment Required)

   ⚠️  Note: Full x402 payment flow requires:
      - x402 client library integration
      - Payment signature generation
      - X-PAYMENT header with proof

   📝 For this example, we'll skip x402 payment
      and proceed directly to donation submission.

Step 6: Submit donation
--------------------------------------------------------------------------------
💸 Making donation of $5.00...
✅ Donation successful!
   Donation ID: d9e8f7g6-h5i4-3210-jklm-nopqrstuvwxy
   Popup Message: Amazing! 🎉
   Duration: 5.0s

Step 7: Verify donation was recorded
--------------------------------------------------------------------------------
🔍 Verifying donation...
✅ Donation verified!
   Amount: $5.00
   Message: Keep up the great content!
   TX Hash: 0xabcdef1234567890...
   Timestamp: 2025-01-12 10:30:45

Step 8: View updated streamer statistics
--------------------------------------------------------------------------------
📊 Fetching streamer donation statistics...
✅ Statistics retrieved!
   Total Amount: $15.00
   Total Donations: 3
   Unique Donors: 2

================================================================================
✨ Donation flow completed successfully!
================================================================================
📝 Summary:
   Streamer: Logan
   Amount: $5.00
   Message: Keep up the great content!
   Donation ID: d9e8f7g6-h5i4-3210-jklm-nopqrstuvwxy
   Popup: Amazing! 🎉

🎉 Thank you for supporting your favorite streamer!
================================================================================
```

---

## 🧪 Test Scenarios

### Scenario 1: Minimum Donation
```bash
# Streamer: Logan
# Amount: $1.00 (minimum tier)
# Message: "Thanks!"
```

### Scenario 2: Mid-tier Donation
```bash
# Streamer: Logan
# Amount: $5.00 (mid tier)
# Message: "Great stream!"
```

### Scenario 3: Maximum Donation
```bash
# Streamer: Logan
# Amount: $10.00 (maximum tier)
# Message: "You're amazing! Keep it up! 🚀"
```

### Scenario 4: Streamer Not Found
```bash
# Streamer: "NonExistentStreamer"
# Expected result: "No streamer found matching 'NonExistentStreamer'"
```

---

## 🔍 Troubleshooting

### 1. `PRIVATE_KEY not set` Error

**Problem:** PRIVATE_KEY is not configured in environment variables.

**Solution:**
```bash
# Add to .env file
echo "PRIVATE_KEY=0xYourPrivateKeyHere" >> .env

# Or set directly
export PRIVATE_KEY=0xYourPrivateKeyHere
```

### 2. `Connection refused` Error

**Problem:** Backend server is not running.

**Solution:**
```bash
# Start backend server
cd /path/to/backend
uv run uvicorn app.main:app --reload
```

### 3. `Streamer not found` Error

**Problem:** No streamers exist in the database.

**Solution:**
```bash
# Mock data loads automatically on server restart
# Or create a new streamer via POST /api/streamer endpoint
```

### 4. `Invalid donation amount` Error

**Problem:** The entered amount doesn't match streamer's donation tiers.

**Solution:**
- Enter exact tier amounts (e.g., 1.0, 5.0, 10.0)
- Check the streamer's available_tier_amounts

---

## 📚 Additional Learning Resources

- **API Documentation:** http://localhost:8000/docs
- **PRD Document:** `../PRD.ko.md`
- **Architecture:** `../ARCHITECTURE.md`
- **Deployment Guide:** `../DEPLOYMENT.md`

---

## 🤝 Contributing

Want to add new examples?

1. Create a new `.py` file in `user_flows/` directory
2. Add clear docstrings and comments
3. Add example description to this README
4. Submit a Pull Request

---

## 📄 License

MIT License - Free to use, modify, and distribute.
