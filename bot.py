import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from notion_client import Client

# 환경 변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 텔레그램 및 노션 설정
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# Notion 클라이언트 초기화
notion = Client(auth=NOTION_API_KEY)

# 데이터베이스 속성 이름 캐시
_db_properties = None

def get_db_properties():
    """데이터베이스 속성 이름 가져오기"""
    global _db_properties
    if _db_properties is None:
        try:
            db = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
            _db_properties = {'props': {}, 'categories': {}}

            for prop_name, prop_data in db['properties'].items():
                prop_type = prop_data.get('type')

                if prop_type == 'title':
                    _db_properties['props']['title'] = prop_name

                elif prop_type == 'date':
                    _db_properties['props']['date'] = prop_name

                elif prop_type == 'number':
                    # 수입 비용, 지출 비용 구분
                    if '수입' in prop_name and '비용' in prop_name:
                        _db_properties['props']['income_amount'] = prop_name
                    elif '지출' in prop_name and '비용' in prop_name:
                        _db_properties['props']['expense_amount'] = prop_name

                elif prop_type == 'select':
                    # 종류 (지출/수입)
                    if '종류' in prop_name and ('지출' not in prop_name or '수입' not in prop_name):
                        _db_properties['props']['type'] = prop_name
                        _db_properties['categories']['type'] = [opt['name'] for opt in prop_data.get('select', {}).get('options', [])]
                    # 지출 카테고리
                    elif '지출' in prop_name and '카테고리' in prop_name:
                        _db_properties['props']['expense_category'] = prop_name
                        _db_properties['categories']['expense_category'] = [opt['name'] for opt in prop_data.get('select', {}).get('options', [])]
                    # 수입 카테고리
                    elif '수입' in prop_name and '카테고리' in prop_name:
                        _db_properties['props']['income_category'] = prop_name
                        _db_properties['categories']['income_category'] = [opt['name'] for opt in prop_data.get('select', {}).get('options', [])]

        except Exception as e:
            logger.error(f"데이터베이스 속성 조회 오류: {e}")
            return None
    return _db_properties


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """봇 시작 명령어 처리"""
    welcome_message = (
        "💰 텔레그램-가계부 봇에 오신 것을 환영합니다!\n\n"
        "이 봇은 텔레그램 메시지를 노션 가계부에 저장합니다.\n\n"
        "사용 가능한 명령어:\n"
        "/start - 환영 메시지 표시\n"
        "/help - 도움말 표시\n"
        "/list - 최근 저장된 항목 목록 보기\n"
        "/status - 현재 설정 상태 확인\n\n"
        "사용법: ! [내용] [금액] [종류] [카테고리] [날짜(선택)]\n\n"
        "예시:\n"
        "! 커피 4500 지출 교통비\n"
        "! 점심 12000 지출 식비 1/9\n"
        "! 월급 3000000 수입 급여"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """도움말 명령어 처리"""
    help_text = (
        "💡 사용 방법:\n\n"
        "형식: ! [내용] [금액] [종류] [카테고리] [날짜(선택)]\n\n"
        "⚠️ 필수 항목:\n"
        "- 내용: 거래 내용\n"
        "- 금액: 숫자만 입력\n"
        "- 종류: 지출 또는 수입\n"
        "- 카테고리: 아래 옵션 중 선택\n\n"
        "📝 지출 카테고리:\n"
        "1-1.월세, 1-2.보험, 1-3.교통비\n"
        "1-4.관리비, 1-5.통신비, 1-6.저축\n"
        "2-1.식비, 2-2.쇼핑, 2-3.여가\n"
        "2-4.여행, 2-5.기타\n\n"
        "📝 수입 카테고리:\n"
        "급여, 추가거래, 기타\n\n"
        "💡 예시:\n"
        "! 커피 4500 지출 2-1.식비\n"
        "! 택시 8900 지출 1-3.교통비 2026/01/10\n"
        "! 월급 3000000 수입 급여\n\n"
        "📅 날짜 형식:\n"
        "- 오늘 (기본값)\n"
        "- 1/9, 2026/01/10\n"
        "- 2026-01-09\n\n"
        "⚙️ 명령어:\n"
        "/start - 시작하기\n"
        "/help - 이 도움말 표시\n"
        "/list - 최근 저장된 항목 10개 조회\n"
        "/status - 현재 상태 확인"
    )
    await update.message.reply_text(help_text)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """상태 확인 명령어 처리"""
    try:
        # Notion 데이터베이스 접근 테스트
        database = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
        status_text = (
            "✅ 연결 상태: 정상\n\n"
            f"노션 데이터베이스: {database.get('title', [{}])[0].get('plain_text', 'Untitled')}\n"
            "텔레그램 봇: 활성화됨"
        )
    except Exception as e:
        status_text = f"❌ 연결 오류:\n{str(e)}"

    await update.message.reply_text(status_text)


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """최근 저장된 항목 목록 조회"""
    try:
        # 노션 데이터베이스에서 최근 10개 항목 조회
        results = notion.databases.query(
            database_id=NOTION_DATABASE_ID,
            sorts=[
                {
                    "property": "날짜",
                    "direction": "descending"
                }
            ],
            page_size=10
        )

        if not results.get('results'):
            await update.message.reply_text("📭 저장된 항목이 없습니다.\n\n! 메시지를 보내서 노션에 저장해보세요!")
            return

        # 항목 목록 생성
        message_list = "📋 최근 저장된 항목 (최대 10개):\n\n"

        # 동적으로 속성 이름 가져오기
        db_props = get_db_properties()
        if not db_props or 'props' not in db_props:
            await update.message.reply_text("❌ 데이터베이스 속성을 가져올 수 없습니다.")
            return

        props = db_props['props']

        for idx, page in enumerate(results['results'], 1):
            properties = page['properties']

            # 내용 추출 (title 타입)
            title_property = properties.get(props.get('title'), {})
            title = ""
            if title_property.get('title'):
                title = title_property['title'][0]['text']['content']

            # 금액 추출
            amount = ""
            if 'amount' in props:
                amount_property = properties.get(props['amount'], {})
                if amount_property.get('number') is not None:
                    amount = f" {int(amount_property['number']):,}원"

            # 카테고리 추출
            category = ""
            if 'category' in props:
                cat_property = properties.get(props['category'], {})
                if cat_property.get('select'):
                    category = f" [{cat_property['select']['name']}]"

            # 날짜 추출
            date_property = properties.get(props.get('date'), {})
            date_str = ""
            if date_property.get('date') and date_property['date'].get('start'):
                date_iso = date_property['date']['start']
                # ISO 형식을 읽기 쉬운 형식으로 변환
                date_obj = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
                date_str = date_obj.strftime('%m/%d')

            message_list += f"{idx}. {title}{amount}{category}\n   📅 {date_str}\n\n"

        message_list += "💡 /help 명령어로 더 많은 기능을 확인하세요!"

        await update.message.reply_text(message_list)

    except Exception as e:
        logger.error(f"목록 조회 오류: {e}")
        await update.message.reply_text(f"❌ 목록 조회 중 오류가 발생했습니다:\n{str(e)}")


def parse_date(date_str):
    """날짜 문자열을 ISO 형식으로 변환"""
    if not date_str or date_str == "오늘":
        return datetime.now().isoformat()

    try:
        # 2026/01/10 형식
        if '/' in date_str:
            parts = date_str.split('/')
            if len(parts) == 3:
                # 2026/01/10 형식
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                return datetime(year, month, day).isoformat()
            elif len(parts) == 2:
                # 1/9, 01/09 형식
                month, day = int(parts[0]), int(parts[1])
                year = datetime.now().year
                return datetime(year, month, day).isoformat()

        # 2026-01-09 형식
        if '-' in date_str:
            return datetime.fromisoformat(date_str).isoformat()

    except:
        pass

    # 파싱 실패시 오늘 날짜 반환
    return datetime.now().isoformat()


async def save_to_notion(message_data: dict):
    """노션 Transaction DB에 메시지 저장"""
    try:
        # 동적으로 속성 이름 가져오기
        db_props = get_db_properties()
        if not db_props or 'props' not in db_props:
            logger.error("데이터베이스 속성을 가져올 수 없습니다")
            return False, "데이터베이스 속성을 가져올 수 없습니다"

        props = db_props['props']

        # 기본 속성 구성
        properties = {
            props['title']: {
                "title": [{"text": {"content": message_data['title']}}]
            },
            props['date']: {
                "date": {"start": message_data['date']}
            }
        }

        # 종류 추가 (필수)
        if 'type' in message_data and 'type' in props:
            properties[props['type']] = {
                "select": {"name": message_data['type']}
            }

        # 금액 및 카테고리 추가 (지출/수입에 따라 다름)
        if message_data['type'] == '지출':
            # 지출 비용
            if 'amount' in message_data and 'expense_amount' in props:
                properties[props['expense_amount']] = {
                    "number": message_data['amount']
                }

            # 지출 카테고리
            if 'category' in message_data and 'expense_category' in props:
                properties[props['expense_category']] = {
                    "select": {"name": message_data['category']}
                }

        elif message_data['type'] == '수입':
            # 수입 비용
            if 'amount' in message_data and 'income_amount' in props:
                properties[props['income_amount']] = {
                    "number": message_data['amount']
                }

            # 수입 카테고리
            if 'category' in message_data and 'income_category' in props:
                properties[props['income_category']] = {
                    "select": {"name": message_data['category']}
                }

        new_page = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": properties
        }

        notion.pages.create(**new_page)
        return True, "저장 성공"
    except Exception as e:
        error_msg = str(e)
        logger.error(f"노션 저장 오류: {error_msg}")
        return False, error_msg


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """일반 메시지 처리"""
    user = update.effective_user
    message = update.message.text

    # ! 로 시작하는 메시지만 처리
    if not message.startswith('!'):
        return

    # ! 를 제거한 실제 메시지 내용
    actual_message = message[1:].strip()

    # 메시지가 비어있으면 무시
    if not actual_message:
        await update.message.reply_text(
            "❌ ! 뒤에 저장할 내용을 입력해주세요.\n"
            "형식: ! [내용] [금액] [종류] [카테고리] [날짜(선택)]\n"
            "예: ! 커피 4500 지출 교통비"
        )
        return

    # 메시지 파싱: ! 내용 금액 종류 카테고리 [날짜]
    parts = actual_message.split()

    # 최소 4개 항목 필요 (내용, 금액, 종류, 카테고리)
    if len(parts) < 4:
        await update.message.reply_text(
            "❌ 필수 항목이 부족합니다.\n\n"
            "형식: ! [내용] [금액] [종류] [카테고리] [날짜(선택)]\n\n"
            "필수 항목:\n"
            "1. 내용\n"
            "2. 금액 (숫자)\n"
            "3. 종류 (지출 또는 수입)\n"
            "4. 카테고리\n\n"
            "예시: ! 커피 4500 지출 교통비"
        )
        return

    # 1. 내용 파싱
    title = parts[0]

    # 2. 금액 파싱 (필수)
    try:
        amount = int(parts[1].replace(',', '').replace('원', ''))
    except ValueError:
        await update.message.reply_text(
            f"❌ 금액이 올바르지 않습니다: '{parts[1]}'\n\n"
            "금액은 숫자만 입력해주세요.\n"
            "예: 4500, 12000, 3000000"
        )
        return

    # 3. 종류 파싱 (필수: 지출 또는 수입)
    trans_type = parts[2]
    if trans_type not in ["지출", "수입"]:
        await update.message.reply_text(
            f"❌ 종류가 올바르지 않습니다: '{trans_type}'\n\n"
            "종류는 '지출' 또는 '수입'만 가능합니다.\n"
            "예: ! 커피 4500 지출 교통비"
        )
        return

    # 4. 카테고리 파싱 (필수)
    category = parts[3]

    # 5. 날짜 파싱 (선택)
    date_str = None
    if len(parts) >= 5:
        date_str = parts[4]

    # 데이터 구성
    message_data = {
        'title': title,
        'amount': amount,
        'type': trans_type,
        'category': category,
        'date': parse_date(date_str)
    }

    # 노션에 저장
    success, msg = await save_to_notion(message_data)

    if success:
        summary = f"✅ 저장되었습니다!\n\n"
        summary += f"내용: {title}\n"
        summary += f"금액: {amount:,}원\n"
        summary += f"종류: {trans_type}\n"
        summary += f"카테고리: {category}\n"

        # 날짜 표시
        date_obj = datetime.fromisoformat(message_data['date'])
        summary += f"날짜: {date_obj.strftime('%Y년 %m월 %d일')}"

        await update.message.reply_text(summary)
    else:
        await update.message.reply_text(f"❌ 저장에 실패했습니다.\n오류: {msg}")


def main():
    """봇 실행"""
    if not all([TELEGRAM_TOKEN, NOTION_API_KEY, NOTION_DATABASE_ID]):
        logger.error("환경 변수가 설정되지 않았습니다. .env 파일을 확인해주세요.")
        return

    # Application 생성
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # 명령어 핸들러 등록
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("list", list_command))
    application.add_handler(CommandHandler("status", status_command))

    # 메시지 핸들러 등록
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # 봇 시작
    logger.info("봇이 시작되었습니다...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
