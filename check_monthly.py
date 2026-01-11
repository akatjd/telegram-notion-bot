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
TRANSACTION_DB_ID = os.getenv('NOTION_DATABASE_ID')
MONTHLY_DB_ID = os.getenv('MONTHLY_DB_ID')
notion = Client(auth=NOTION_API_KEY)

print("=== Transaction DB 확인 ===")
try:
    db = notion.databases.retrieve(database_id=TRANSACTION_DB_ID)
    print("\n모든 속성:")
    for prop_name, prop_data in db['properties'].items():
        prop_type = prop_data.get('type')
        print(f"  - '{prop_name}': {prop_type}")
        if prop_type == 'relation':
            relation = prop_data.get('relation', {})
            print(f"    -> 연결된 DB: {relation.get('database_id')}")
except Exception as e:
    print(f"오류: {e}")

print("\n=== Monthly DB 확인 ===")
try:
    monthly_db = notion.databases.retrieve(database_id=MONTHLY_DB_ID)
    print(f"Monthly DB 제목: {monthly_db.get('title', [{}])[0].get('plain_text', 'N/A')}")

    # Monthly DB의 페이지들 조회
    print("\nMonthly DB의 페이지들:")
    results = notion.databases.query(database_id=MONTHLY_DB_ID)
    for page in results['results'][:10]:  # 최근 10개만
        # title 속성 찾기
        for prop_name, prop_data in page['properties'].items():
            if prop_data.get('type') == 'title':
                title_list = prop_data.get('title', [])
                if title_list:
                    title = title_list[0].get('plain_text', '')
                    print(f"  - {title} (ID: {page['id']})")
                break
except Exception as e:
    print(f"오류: {e}")
