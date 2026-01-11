import os
from dotenv import load_dotenv
from notion_client import Client
from datetime import datetime

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
notion = Client(auth=NOTION_API_KEY)

try:
    # 먼저 데이터베이스 속성 가져오기
    db = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)

    # Title 타입 속성 찾기
    title_prop_name = None
    date_prop_name = None

    for prop_name, prop_data in db['properties'].items():
        if prop_data.get('type') == 'title':
            title_prop_name = prop_name
            print(f"Found title property: {repr(prop_name)}")
        if prop_data.get('type') == 'date':
            date_prop_name = prop_name
            print(f"Found date property: {repr(prop_name)}")

    # 테스트 데이터 저장
    print("\nAttempting to save test data...")

    new_page = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            title_prop_name: {
                "title": [
                    {
                        "text": {
                            "content": "텔레그램 봇 테스트"
                        }
                    }
                ]
            },
            date_prop_name: {
                "date": {
                    "start": datetime.now().isoformat()
                }
            }
        }
    }

    result = notion.pages.create(**new_page)
    print(f"✅ Success! Page created: {result['id']}")

except Exception as e:
    print(f"❌ Error: {str(e)}")
