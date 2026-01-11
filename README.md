# 💰 텔레그램 가계부 봇

텔레그램으로 간편하게 지출/수입을 기록하고 Notion 데이터베이스에 자동으로 저장하는 가계부 봇입니다.

## ✨ 주요 기능

- 💸 텔레그램에서 간단한 메시지로 지출/수입 기록
- 📊 월별 통계 조회 (총 지출/수입, 카테고리별 분석)
- 🗓️ 날짜별 거래 내역 자동 분류
- 📁 카테고리별 지출/수입 관리
- 🔄 Notion과 실시간 동기화

## 📋 사전 준비

### 1. 텔레그램 봇 생성

1. 텔레그램에서 [@BotFather](https://t.me/botfather) 검색
2. `/newbot` 명령어 입력
3. 봇 이름과 username 설정
4. 발급받은 **Bot Token** 저장

### 2. Notion 설정

#### 2.1 Notion Integration 생성

1. [Notion Integrations](https://www.notion.so/my-integrations) 페이지 접속
2. "+ New integration" 클릭
3. 통합 이름 설정 후 생성
4. **Internal Integration Token** 복사하여 저장

#### 2.2 Transaction Database (거래 내역) 생성

1. Notion에서 새 페이지 생성
2. `/database` 입력하여 Full page database 생성
3. 다음 속성(properties) 추가:
   - **내역** (Title) - 거래 내용
   - **날짜** (Date) - 거래 날짜
   - **종류** (Select) - 옵션: `지출`, `수입`
   - **지출 비용** (Number, 통화: KRW) - 지출 금액
   - **수입 비용** (Number, 통화: KRW) - 수입 금액
   - **지출 종류** (Select) - 지출 카테고리
     - `1-1. 월세`, `1-2. 보험`, `1-3. 교통비`, `1-4. 관리비`, `1-5. 통신비`, `1-6. 저축`
     - `2-1. 식비`, `2-2. 쇼핑`, `2-3. 여가`, `2-4. 여행`, `2-5. 기타`
   - **수입 종류** (Select) - 수입 카테고리: `급여`, `중고거래`, `기타`
   - **월** (Relation) - Monthly DB와 연결
   - **절대 비용** (Formula) - 수식: `if(prop("지출 비용"), prop("지출 비용"), prop("수입 비용"))`

4. 데이터베이스 우측 상단 `...` > `Add connections` > 생성한 Integration 선택
5. 데이터베이스 ID 복사:
   ```
   https://www.notion.so/workspace/[DATABASE_ID]?v=...
                                   ^^^^^^^^^^^^^^^^
   ```

#### 2.3 Monthly Database (월별) 생성

1. 새 Full page database 생성
2. 속성:
   - **이름** (Title) - 형식: `YYYY-MM` (예: `2026-01`)
3. 각 월 페이지를 미리 생성 (예: `2026-01`, `2026-02`, ...)
4. Integration 연결
5. 데이터베이스 ID 복사

## 🚀 설치 방법

### 1. 저장소 클론

```bash
git clone https://github.com/your-username/telegram-notion-bot.git
cd telegram-notion-bot
```

### 2. 가상환경 생성 및 활성화

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

`.env` 파일 생성:

```env
# Telegram Bot Token (BotFather에서 발급)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here

# Notion API Key (https://www.notion.so/my-integrations에서 발급)
NOTION_API_KEY=your_notion_api_key_here

# Notion Transaction Database ID (거래 내역 DB)
NOTION_DATABASE_ID=your_transaction_database_id_here

# Notion Monthly Database ID (월별 DB)
MONTHLY_DB_ID=your_monthly_database_id_here
```

## 💡 사용 방법

### 봇 실행

```bash
python bot.py
```

### 텔레그램에서 사용

#### 📝 거래 기록하기

형식: `! [내용] [금액] [종류] [카테고리] [날짜(선택)]`

**예시:**
```
! 커피 4500 지출 2-1.식비
! 택시 8900 지출 1-3.교통비 2026/01/10
! 점심 12000 지출 2-1.식비 1/11
! 월급 3000000 수입 급여
```

**날짜 형식:**
- 생략 → 오늘 날짜
- `1/11` → 올해 1월 11일
- `2026/01/11` → 2026년 1월 11일
- `2026-01-11` → ISO 형식

#### 🤖 명령어

- `/start` - 봇 시작 및 환영 메시지
- `/help` - 사용법 및 도움말
- `/list` - 최근 저장된 거래 10개 조회
- `/status` - Notion 연결 상태 확인
- `/월별통계 [YYYY-MM]` - 월별 지출/수입 통계 조회
  - 예: `/월별통계 2026-01`
  - 인자 생략 시 이번 달 통계 조회

#### 📊 월별 통계 예시

```
📊 2026-01 월별 통계
==============================

💰 총 수입: 3,000,000원
💸 총 지출: 1,250,000원
📈 순자산 변화: +1,750,000원
📝 거래 건수: 45건

💵 수입 내역:
  • 급여: 3,000,000원 (100.0%)

💳 지출 내역:
  • 2-1. 식비: 450,000원 (36.0%)
  • 1-1. 월세: 400,000원 (32.0%)
  • 2-2. 쇼핑: 200,000원 (16.0%)
  • 1-3. 교통비: 150,000원 (12.0%)
  • 2-5. 기타: 50,000원 (4.0%)
```

## 📁 프로젝트 구조

```
telegram-notion-bot/
├── bot.py                  # 메인 봇 코드
├── requirements.txt        # Python 패키지 목록
├── .env                   # 환경 변수 (git 제외)
├── .gitignore            # Git 제외 파일 목록
├── README.md             # 이 파일
└── test_*.py             # 테스트 스크립트들
```

## 🔧 문제 해결

### 봇이 시작되지 않을 때

1. `.env` 파일의 모든 토큰/ID가 올바른지 확인
2. 가상환경이 활성화되어 있는지 확인
3. 패키지 재설치: `pip install -r requirements.txt`

### 데이터가 저장되지 않을 때

1. Notion Database에 Integration이 연결되어 있는지 확인
2. Database 속성 이름과 타입이 정확한지 확인
3. `/status` 명령어로 연결 상태 확인
4. 봇 로그에서 오류 메시지 확인

### 월 필드가 비어있을 때

1. Monthly DB에 해당 월 페이지가 생성되어 있는지 확인 (예: `2026-01`)
2. Monthly DB에 Integration이 연결되어 있는지 확인
3. `MONTHLY_DB_ID`가 `.env`에 올바르게 설정되어 있는지 확인

### 카테고리가 저장되지 않을 때

- 카테고리 입력 시 공백 주의: `2-1.식비` 또는 `2-1. 식비` 모두 가능
- 봇이 자동으로 정규화하여 Notion 옵션과 매칭합니다

## 🛠️ 기술 스택

- **Python 3.8+**
- **python-telegram-bot** - Telegram Bot API
- **notion-client** - Notion API
- **python-dotenv** - 환경 변수 관리

## 📝 라이선스

MIT License

## 🤝 기여

이슈 리포트와 Pull Request를 환영합니다!

## 👨‍💻 개발자

[@akatjd](https://github.com/akatjd)
