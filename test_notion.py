import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
notion = Client(auth=NOTION_API_KEY)

print("노션 연결 테스트...")
print(f"API Key: {NOTION_API_KEY[:20]}...")

# 검색으로 데이터베이스 찾기
try:
    results = notion.search(filter={"property": "object", "value": "database"})

    print(f"\n접근 가능한 데이터베이스 목록:")
    print("=" * 80)

    for db in results.get('results', []):
        db_id = db['id']
        title = ""
        if db.get('title'):
            title = db['title'][0]['plain_text'] if db['title'] else "Untitled"

        print(f"제목: {title}")
        print(f"ID: {db_id}")
        print(f"URL: https://www.notion.so/{db_id.replace('-', '')}")
        print("-" * 80)

except Exception as e:
    print(f"오류 발생: {e}")
