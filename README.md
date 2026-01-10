# 텔레그램-노션 연동 봇

텔레그램으로 보낸 메시지를 자동으로 노션 데이터베이스에 저장하는 봇입니다.

## 주요 기능

- 텔레그램 메시지를 노션 데이터베이스에 자동 저장
- 메시지 제목, 내용, 발신자, 날짜 정보 기록
- 간단한 명령어로 봇 상태 확인

## 사전 준비

### 1. 텔레그램 봇 생성

1. 텔레그램에서 [@BotFather](https://t.me/botfather) 검색
2. `/newbot` 명령어 입력
3. 봇 이름과 username 설정
4. 발급받은 **Bot Token** 저장

### 2. 노션 통합 설정

1. [Notion Integrations](https://www.notion.so/my-integrations) 페이지 접속
2. "+ New integration" 클릭
3. 통합 이름 설정 후 생성
4. **Internal Integration Token** 복사하여 저장

### 3. 노션 데이터베이스 생성

1. 노션에서 새 페이지 생성
2. `/database` 입력하여 데이터베이스 생성
3. 다음 속성(properties) 추가:
   - **제목** (Title) - 기본 제목 속성
   - **내용** (Text)
   - **발신자** (Text)
   - **날짜** (Date)

4. 데이터베이스 우측 상단 `...` > `Add connections` > 생성한 통합 선택
5. 데이터베이스 URL에서 ID 복사:
   ```
   https://www.notion.so/[workspace]/[DATABASE_ID]?v=...
                                    ^^^^^^^^^^^^^^^^
                                    이 부분이 Database ID
   ```

## 설치 방법

### 1. 저장소 클론 또는 파일 다운로드

```bash
cd telegram-notion-bot
```

### 2. 가상환경 생성 및 활성화

```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (macOS/Linux)
source venv/bin/activate

# 가상환경 활성화 (Windows)
venv\Scripts\activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정

```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일 편집
nano .env
```

`.env` 파일에 아래 정보 입력:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
NOTION_API_KEY=your_notion_api_key_here
NOTION_DATABASE_ID=your_notion_database_id_here
```

## 사용 방법

### 봇 실행

```bash
python bot.py
```

### 텔레그램에서 봇 사용

1. 텔레그램에서 생성한 봇 검색
2. `/start` 명령어로 시작
3. 메시지를 보내면 자동으로 노션에 저장됩니다

### 사용 가능한 명령어

- `/start` - 봇 시작 및 환영 메시지
- `/help` - 도움말 표시
- `/status` - 노션 연결 상태 확인

## 프로젝트 구조

```
telegram-notion-bot/
├── bot.py              # 메인 봇 코드
├── requirements.txt    # 필요한 패키지 목록
├── .env               # 환경 변수 (git에 커밋되지 않음)
├── .env.example       # 환경 변수 예시
├── .gitignore         # Git 제외 파일 목록
└── README.md          # 이 파일
```

## 문제 해결

### 봇이 시작되지 않을 때

1. `.env` 파일의 토큰과 ID가 올바른지 확인
2. 가상환경이 활성화되어 있는지 확인
3. 모든 패키지가 설치되었는지 확인: `pip install -r requirements.txt`

### 노션에 저장되지 않을 때

1. 노션 데이터베이스에 통합(Integration)이 연결되어 있는지 확인
2. 데이터베이스 속성 이름이 정확한지 확인 (제목, 내용, 발신자, 날짜)
3. `/status` 명령어로 연결 상태 확인

### 데이터베이스 속성 이름 변경

`bot.py` 파일의 `save_to_notion` 함수에서 속성 이름을 수정할 수 있습니다:

```python
"properties": {
    "제목": {  # 여기를 노션 데이터베이스의 속성 이름과 일치시키세요
        "title": [...]
    },
    "내용": {  # 마찬가지로 수정
        "rich_text": [...]
    },
    ...
}
```

## 확장 아이디어

- 사진, 파일 등 미디어 저장 기능 추가
- 특정 키워드가 포함된 메시지만 저장
- 여러 노션 데이터베이스에 카테고리별로 저장
- 노션에서 텔레그램으로 알림 보내기

## 라이선스

MIT License

## 기여

이슈나 Pull Request를 환영합니다!
