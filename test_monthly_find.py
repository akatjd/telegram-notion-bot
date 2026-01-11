import os
from dotenv import load_dotenv
from notion_client import Client
import sys

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
MONTHLY_DB_ID = os.getenv('MONTHLY_DB_ID')
notion = Client(auth=NOTION_API_KEY)

def find_monthly_page(year_month_str):
    """
    Monthly DB에서 특정 월(YYYY-MM 형식) 페이지를 찾기
    """
    try:
        print(f"'{year_month_str}' 페이지 찾는 중...")

        # Monthly DB 조회
        results = notion.databases.query(database_id=MONTHLY_DB_ID)
        print(f"총 {len(results['results'])}개 페이지 발견")

        for page in results['results']:
            # title 속성 찾기
            for prop_name, prop_data in page['properties'].items():
                if prop_data.get('type') == 'title':
                    title_list = prop_data.get('title', [])
                    if title_list:
                        title = title_list[0].get('plain_text', '')
                        print(f"  페이지: '{title}' (ID: {page['id']})")
                        if title == year_month_str:
                            print(f"  ✅ 매칭 성공!")
                            return page['id']
                    break

        print(f"❌ '{year_month_str}' 페이지를 찾지 못했습니다")
        return None

    except Exception as e:
        print(f"오류: {e}")
        import traceback
        traceback.print_exc()
        return None


# 테스트
print("=== 2026-01 페이지 찾기 테스트 ===\n")
page_id = find_monthly_page("2026-01")

if page_id:
    print(f"\n성공! 페이지 ID: {page_id}")
else:
    print("\n실패!")
