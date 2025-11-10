# 스트리머 후원 시스템 (Streamer Donation System)

> Base 블록체인과 x402 프로토콜을 활용한 스트리머 직접 후원 플랫폼

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)

[English](./README.md) | **한국어**

---

## 📋 프로젝트 소개

스트리머 후원 시스템은 YouTube, Twitch 등의 스트리머가 **중간 플랫폼 수수료 없이** 암호화폐로 직접 후원을 받을 수 있는 웹 플랫폼입니다.

### 핵심 특징

- ⚡ **빠른 결제**: x402 프로토콜로 ~2초 내 결제 처리
- 💰 **저렴한 수수료**: Base 블록체인 사용으로 거래 수수료 < $0.0001
- 🎯 **커스터마이징**: 스트리머가 후원 금액 티어 및 메시지 설정 가능
- 💬 **메시지 기능**: 시청자가 후원과 함께 응원 메시지 전송
- 🔒 **안전한 결제**: Web3 지갑 기반 비수탁형(non-custodial) 결제

### 사용 기술

- **백엔드**: FastAPI (Python 3.10+)
- **블록체인**: Base (Ethereum L2)
- **결제 프로토콜**: x402
- **데이터베이스**: RocksDB
- **프론트엔드**: Vanilla JavaScript + Viem

---

## 🚀 빠른 시작

### 사전 요구사항

- **Python 3.10 이상**
- **uv** (Python 패키지 관리자) - [설치 가이드](https://github.com/astral-sh/uv)
- **Base Sepolia 테스트넷 지갑** 및 테스트 토큰
- **CDP (Coinbase Developer Platform) 계정** - [가입하기](https://portal.cdp.coinbase.com/)

### 1. 레포지토리 클론

```bash
git clone --recursive https://github.com/YOUR_USERNAME/awesome-x402-on-base.git
cd awesome-x402-on-base/examples/base-specific/streamer-donation
```

### 2. 환경 설정

```bash
cd backend
cp .env.example .env
```

`.env` 파일을 편집하여 CDP 인증 정보를 입력하세요:

```bash
# .env
CDP_API_KEY_ID=your-api-key-id
CDP_API_KEY_SECRET=your-api-key-secret
CDP_WALLET_SECRET=your-wallet-secret
NETWORK=base-sepolia
```

### 3. 의존성 설치

```bash
uv sync
```

### 4. 서버 실행

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

서버가 `http://localhost:8000`에서 실행됩니다.

### 5. 브라우저에서 접속

- **랜딩 페이지**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs
- **후원 페이지 예시**: http://localhost:8000/donate/{streamer_id}

---

## 📖 사용 가이드

### 스트리머 설정 (Phase 1 - 모킹)

Phase 1에서는 스트리머 데이터가 `app/mock_data.py`에 하드코딩되어 있습니다.

```python
# app/mock_data.py
MOCK_STREAMERS = {
    "logan": Streamer(
        id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
        name="Logan",
        wallet_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        platforms=["youtube", "twitch"],
        donation_tiers=[
            DonationTier(amount_usd=1.0, popup_message="감사합니다! 💙"),
            DonationTier(amount_usd=5.0, popup_message="대박! 🎉"),
            DonationTier(amount_usd=10.0, popup_message="레전드! 🌟"),
        ],
        thank_you_message="방송 시청해주셔서 감사합니다!"
    ),
}
```

### 후원 플로우

1. **스트리머**: 후원 링크 생성 및 방송 설명란/채팅에 공유
   ```
   https://localhost:8000/donate/a1b2c3d4-e5f6-7890-abcd-ef1234567890
   ```

2. **시청자**: 링크 클릭 → 후원 페이지 접속

3. **시청자**: 후원 금액 티어 선택 및 메시지 입력

4. **시청자**: Web3 지갑 연결 (MetaMask, Coinbase Wallet 등)

5. **시청자**: x402 프로토콜로 결제 처리

6. **시청자**: 감사 페이지에서 완료 확인

---

## 🏗️ 프로젝트 구조

```
streamer-donation/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 진입점
│   │   ├── models.py            # Pydantic 데이터 모델
│   │   ├── database.py          # RocksDB 래퍼
│   │   ├── config.py            # 환경 설정
│   │   ├── mock_data.py         # 모킹 스트리머 데이터
│   │   └── routes/
│   │       ├── streamers.py     # 스트리머 API
│   │       └── donations.py     # 후원 API
│   ├── static/                  # CSS, JS, 이미지
│   ├── templates/               # HTML 템플릿
│   ├── tests/                   # 테스트 코드
│   ├── pyproject.toml           # 의존성 정의
│   └── .env.example             # 환경 변수 템플릿
├── docs/                        # 추가 문서
├── PRD.ko.md                    # 제품 요구사항 명세서
└── README.ko.md                 # 이 파일
```

---

## 🔌 API 엔드포인트

### 스트리머 정보 조회

```http
GET /api/streamer/{streamer_id}
```

**응답 예시**:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Logan",
  "wallet_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
  "platforms": ["youtube", "twitch"],
  "donation_tiers": [
    {
      "amount_usd": 1.0,
      "popup_message": "감사합니다! 💙",
      "duration_ms": 3000
    }
  ]
}
```

### 후원 페이지 (x402 보호)

```http
GET /donate/{streamer_id}
```

x402 프로토콜로 보호된 엔드포인트입니다. 결제 없이 접근 시 `402 Payment Required` 응답을 받습니다.

### 후원 메시지 제출

```http
POST /api/donate/{streamer_id}/message
Content-Type: application/json

{
  "amount_usd": 5.0,
  "donor_address": "0x1234...",
  "message": "재밌는 방송!",
  "tx_hash": "0xabcdef..."
}
```

상세한 API 명세는 [API.md](./docs/API.md)를 참고하세요.

---

## 🧪 테스트

### 전체 테스트 실행

```bash
uv run pytest
```

### 커버리지 포함 실행

```bash
uv run pytest --cov=app --cov-report=html
```

### 특정 테스트 실행

```bash
uv run pytest tests/test_api.py -v
```

---

## 🔒 보안

### 구현된 보안 조치

- ✅ **지갑 주소 검증**: Web3.is_address() 사용
- ✅ **금액 제한**: $0.01 - $1000 범위
- ✅ **XSS 방지**: bleach 라이브러리로 HTML 태그 제거
- ✅ **CORS 설정**: 허용 도메인 리스트 관리

### 주의사항

⚠️ **Private Key 보안**:
- `.env` 파일을 절대 Git에 커밋하지 마세요
- 개발용과 프로덕션용 지갑을 분리하세요
- 테스트는 Base Sepolia 네트워크에서만 진행하세요

---

## 📚 문서

- [PRD (Product Requirements Document)](./PRD.ko.md) - 제품 요구사항 명세서
- [API 명세](./docs/API.md) - 상세 API 문서
- [시스템 아키텍처](./docs/ARCHITECTURE.md) - 전체 시스템 구조
- [배포 가이드](./docs/DEPLOYMENT.md) - 프로덕션 배포 방법

---

## 🗺️ 로드맵

### Phase 1: MVP (현재)
- [x] 프로젝트 구조 및 설정
- [x] RocksDB 통합
- [ ] x402 미들웨어 통합
- [ ] 후원 페이지 UI
- [ ] Web3 지갑 연결
- [ ] 감사 페이지

### Phase 2: AI Agent 통합
- [ ] Google A2A 프로토콜 연구
- [ ] 자연어 후원 명령 처리
- [ ] 실시간 알림 (WebSocket)
- [ ] 클립 업로드/저장

---

## 🤝 기여

이 프로젝트는 오픈소스이며 커뮤니티 기여를 환영합니다!

### 기여 방법

1. 이 레포지토리를 Fork하세요
2. Feature 브랜치를 생성하세요 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 Push하세요 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성하세요

### 코드 스타일

- **Python**: Black (line length 100) + Ruff
- **주석/Docstring**: 영어
- **커밋 메시지**: [Conventional Commits](https://www.conventionalcommits.org/) 형식

---

## 📞 문의 및 지원

- **GitHub Issues**: [Issues 페이지](https://github.com/YOUR_USERNAME/awesome-x402-on-base/issues)
- **Discord**: Base Korea 커뮤니티
- **작성자**: Logan (Base Korea Developer Ambassador)

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](../../LICENSE) 파일을 참고하세요.

---

## 🙏 감사의 말

- [Coinbase](https://www.coinbase.com/) - Base 블록체인 및 CDP Platform 제공
- [x402 프로토콜](https://github.com/coinbase/x402) - 혁신적인 마이크로페이먼트 프로토콜
- Base Korea 커뮤니티 - 피드백 및 테스트

---

**Built with ❤️ for the Base ecosystem**
