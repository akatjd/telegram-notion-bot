import os
from dotenv import load_dotenv
from notion_client import Client
import json

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
notion = Client(auth=NOTION_API_KEY)

print("Transaction DB 속성 이름 확인")
print("=" * 80)

try:
    db = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)

    print("\n정확한 속성 이름들:")
    print("-" * 80)

    for prop_name, prop_data in db['properties'].items():
        prop_type = prop_data.get('type', 'unknown')
        # 속성 이름을 repr로 출력하여 정확한 값 확인
        print(f"속성 이름: {repr(prop_name)}")
        print(f"  타입: {prop_type}")
        print()

    # Title 타입 찾기
    print("\nTitle 타입 속성:")
    for prop_name, prop_data in db['properties'].items():
        if prop_data.get('type') == 'title':
            print(f"  -> {repr(prop_name)}")

    # Date 타입 찾기
    print("\nDate 타입 속성:")
    for prop_name, prop_data in db['properties'].items():
        if prop_data.get('type') == 'date':
            print(f"  -> {repr(prop_name)}")

except Exception as e:
    print(f"오류: {str(e)}")
