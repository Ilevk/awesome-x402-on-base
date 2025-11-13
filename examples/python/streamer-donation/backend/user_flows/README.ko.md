# 사용자 플로우 예제

이 디렉토리에는 스트리머 후원 시스템의 실제 사용자 플로우 예제가 포함되어 있습니다.

## 📝 예제 목록

### 1. `donation_flow_example.py` - 완전한 후원 플로우

좋아하는 스트리머를 검색하고 x402 프로토콜을 통해 후원하는 전체 시나리오를 보여줍니다.

**시나리오:**
1. 스트리머 이름으로 검색
2. 사용 가능한 후원 티어 확인
3. x402 보호된 후원 페이지 접근
4. 후원 금액 및 메시지 선택
5. 후원 제출
6. 후원 검증
7. 스트리머 통계 확인

---

## 🚀 실행 방법

### 사전 요구사항

1. **백엔드 서버 실행**
   ```bash
   cd /path/to/backend
   uv run uvicorn app.main:app --reload
   ```

2. **환경 변수 설정**

   `.env` 파일 또는 환경 변수로 다음을 설정하세요:
   ```bash
   # API 서버 URL
   API_BASE_URL=http://localhost:8000

   # 후원자 지갑 Private Key (테스트넷용)
   PRIVATE_KEY=0xac0974bec39a17e36f4ac7d1d5f1e3fe...

   # 네트워크 (base-sepolia 또는 base)
   NETWORK=base-sepolia
   ```

   ⚠️ **보안 주의사항:**
   - 테스트넷 Private Key만 사용하세요
   - 절대 메인넷 Private Key를 사용하지 마세요
   - `.env` 파일이 `.gitignore`에 포함되어 있는지 확인하세요

### 실행

```bash
# user_flows 디렉토리로 이동
cd user_flows

# 예제 실행
python donation_flow_example.py
```

---

## 📋 실행 예시

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

## 🧪 테스트 시나리오

### 시나리오 1: 최소 금액 후원
```bash
# 스트리머: Logan
# 금액: $1.00 (최소 티어)
# 메시지: "Thanks!"
```

### 시나리오 2: 중간 금액 후원
```bash
# 스트리머: Logan
# 금액: $5.00 (중간 티어)
# 메시지: "Great stream!"
```

### 시나리오 3: 최대 금액 후원
```bash
# 스트리머: Logan
# 금액: $10.00 (최대 티어)
# 메시지: "You're amazing! Keep it up! 🚀"
```

### 시나리오 4: 스트리머를 찾을 수 없는 경우
```bash
# 스트리머: "NonExistentStreamer"
# 예상 결과: "No streamer found matching 'NonExistentStreamer'"
```

---

## 🔍 문제 해결

### 1. `PRIVATE_KEY not set` 오류

**문제:** 환경 변수에 PRIVATE_KEY가 설정되지 않았습니다.

**해결방법:**
```bash
# .env 파일에 추가
echo "PRIVATE_KEY=0xYourPrivateKeyHere" >> .env

# 또는 직접 설정
export PRIVATE_KEY=0xYourPrivateKeyHere
```

### 2. `Connection refused` 오류

**문제:** 백엔드 서버가 실행되지 않았습니다.

**해결방법:**
```bash
# 백엔드 서버 실행
cd /path/to/backend
uv run uvicorn app.main:app --reload
```

### 3. `Streamer not found` 오류

**문제:** 데이터베이스에 스트리머가 없습니다.

**해결방법:**
```bash
# 서버 재시작 시 mock data가 자동으로 로드됩니다
# 또는 POST /api/streamer 엔드포인트로 새 스트리머 생성
```

### 4. `Invalid donation amount` 오류

**문제:** 입력한 금액이 스트리머의 후원 티어와 일치하지 않습니다.

**해결방법:**
- 정확히 티어 금액을 입력하세요 (예: 1.0, 5.0, 10.0)
- 스트리머의 available_tier_amounts를 확인하세요

---

## 📚 추가 학습 자료

- **API 문서:** http://localhost:8000/docs
- **PRD 문서:** `../PRD.ko.md`
- **아키텍처:** `../ARCHITECTURE.md`
- **배포 가이드:** `../DEPLOYMENT.md`

---

## 🤝 기여

새로운 사용자 플로우를 추가하고 싶으신가요?

1. `user_flows/` 디렉토리에 새 `.py` 파일 생성
2. 명확한 docstring과 주석 추가
3. 이 README에 예제 설명 추가
4. Pull Request 제출

---

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.
