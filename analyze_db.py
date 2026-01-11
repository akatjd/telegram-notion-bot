import os
from dotenv import load_dotenv
from notion_client import Client
import json

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
notion = Client(auth=NOTION_API_KEY)

print("Transaction DB 속성 상세 분석")
print("=" * 80)

try:
    db = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)

    print(f"데이터베이스: {db['title'][0]['plain_text']}\n")

    for prop_name, prop_data in db['properties'].items():
        prop_type = prop_data.get('type', 'unknown')
        print(f"\n속성: {prop_name}")
        print(f"  타입: {prop_type}")

        # Select 타입인 경우 옵션 출력
        if prop_type == 'select' and 'select' in prop_data:
            if prop_data['select'].get('options'):
                print(f"  옵션:")
                for option in prop_data['select']['options']:
                    print(f"    - {option['name']}")

except Exception as e:
    print(f"오류: {str(e)}")
