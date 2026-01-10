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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """봇 시작 명령어 처리"""
    welcome_message = (
        "텔레그램-노션 봇에 오신 것을 환영합니다!\n\n"
        "이 봇은 ! 로 시작하는 메시지를 노션 데이터베이스에 저장합니다.\n\n"
        "사용 가능한 명령어:\n"
        "/start - 환영 메시지 표시\n"
        "/help - 도움말 표시\n"
        "/list - 최근 저장된 메시지 목록 보기\n"
        "/status - 현재 설정 상태 확인\n\n"
        "사용법: ! 메시지 내용\n"
        "예시: ! 오늘 회의 내용 정리하기"
    )
    await update.message.reply_text(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """도움말 명령어 처리"""
    help_text = (
        "사용 방법:\n\n"
        "1. ! 로 시작하는 메시지만 노션에 저장됩니다.\n"
        "2. 메시지는 제목, 내용, 날짜와 함께 저장됩니다.\n"
        "3. 메시지 발신자 정보도 함께 기록됩니다.\n\n"
        "예시:\n"
        "! 오늘 할 일 정리\n"
        "! 프로젝트 아이디어: AI 챗봇 개발\n"
        "! 회의록: 2026년 1월 10일\n\n"
        "명령어:\n"
        "/start - 시작하기\n"
        "/help - 이 도움말 표시\n"
        "/list - 최근 저장된 메시지 10개 조회\n"
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
    """최근 저장된 메시지 목록 조회"""
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
            await update.message.reply_text("📭 저장된 메시지가 없습니다.\n\n! 메시지를 보내서 노션에 저장해보세요!")
            return

        # 메시지 목록 생성
        message_list = "📋 최근 저장된 메시지 (최대 10개):\n\n"

        for idx, page in enumerate(results['results'], 1):
            properties = page['properties']

            # 제목 추출
            title_property = properties.get('제목', {})
            title = ""
            if title_property.get('title'):
                title = title_property['title'][0]['text']['content']

            # 날짜 추출
            date_property = properties.get('날짜', {})
            date_str = ""
            if date_property.get('date') and date_property['date'].get('start'):
                date_iso = date_property['date']['start']
                # ISO 형식을 읽기 쉬운 형식으로 변환
                date_obj = datetime.fromisoformat(date_iso.replace('Z', '+00:00'))
                date_str = date_obj.strftime('%m/%d %H:%M')

            message_list += f"{idx}. {title}\n   📅 {date_str}\n\n"

        message_list += "💡 /help 명령어로 더 많은 기능을 확인하세요!"

        await update.message.reply_text(message_list)

    except Exception as e:
        logger.error(f"목록 조회 오류: {e}")
        await update.message.reply_text(f"❌ 목록 조회 중 오류가 발생했습니다:\n{str(e)}")


async def save_to_notion(message_data: dict):
    """노션 데이터베이스에 메시지 저장"""
    try:
        new_page = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "제목": {
                    "title": [
                        {
                            "text": {
                                "content": message_data['title']
                            }
                        }
                    ]
                },
                "내용": {
                    "rich_text": [
                        {
                            "text": {
                                "content": message_data['content']
                            }
                        }
                    ]
                },
                "발신자": {
                    "rich_text": [
                        {
                            "text": {
                                "content": message_data['sender']
                            }
                        }
                    ]
                },
                "날짜": {
                    "date": {
                        "start": message_data['date']
                    }
                }
            }
        }

        notion.pages.create(**new_page)
        return True
    except Exception as e:
        logger.error(f"노션 저장 오류: {e}")
        return False


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
        await update.message.reply_text("❌ ! 뒤에 저장할 내용을 입력해주세요.\n예: ! 오늘 할 일 정리")
        return

    # 메시지가 너무 길면 제목을 축약
    title = actual_message[:50] + "..." if len(actual_message) > 50 else actual_message

    message_data = {
        'title': title,
        'content': actual_message,
        'sender': f"{user.first_name} {user.last_name or ''}".strip() + f" (@{user.username})" if user.username else "",
        'date': datetime.now().isoformat()
    }

    # 노션에 저장
    success = await save_to_notion(message_data)

    if success:
        await update.message.reply_text("✅ 메시지가 노션에 저장되었습니다!")
    else:
        await update.message.reply_text("❌ 메시지 저장에 실패했습니다. 로그를 확인해주세요.")


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
