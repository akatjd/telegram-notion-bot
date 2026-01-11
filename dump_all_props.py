import os
from dotenv import load_dotenv
from notion_client import Client
import json
import sys

# UTF-8 출력 설정
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
notion = Client(auth=NOTION_API_KEY)

try:
    db = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)

    print("전체 속성 JSON:")
    print(json.dumps(db['properties'], indent=2, ensure_ascii=False))

except Exception as e:
    print(f"오류: {str(e)}")
