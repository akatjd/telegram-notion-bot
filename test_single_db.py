import os
from dotenv import load_dotenv
from notion_client import Client

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
notion = Client(auth=NOTION_API_KEY)

print(f"테스트 중인 데이터베이스 ID: {NOTION_DATABASE_ID}")
print("=" * 80)

try:
    db = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)
    title = ""
    if db.get('title'):
        title = db['title'][0]['plain_text'] if db['title'] else "Untitled"

    print(f"성공! 데이터베이스에 접근할 수 있습니다!")
    print(f"제목: {title}")
    print(f"\n속성(Properties):")
    for prop_name, prop_data in db['properties'].items():
        prop_type = prop_data.get('type', 'unknown')
        print(f"  - {prop_name}: {prop_type}")

except Exception as e:
    print(f"실패: {str(e)}")
