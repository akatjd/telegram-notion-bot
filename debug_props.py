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

print(f"데이터베이스 ID: {NOTION_DATABASE_ID}")
print("=" * 80)

try:
    db = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)

    print("\n모든 속성 상세 정보:\n")

    for prop_name, prop_data in db['properties'].items():
        prop_type = prop_data.get('type', 'unknown')
        print(f"속성명: '{prop_name}'")
        print(f"타입: {prop_type}")

        # 디버그: 필드 감지 조건 체크
        if prop_type == 'select':
            print(f"  '종류' in prop_name: {'종류' in prop_name}")
            print(f"  '카테고리' in prop_name: {'카테고리' in prop_name}")
            print(f"  '지출' in prop_name: {'지출' in prop_name}")
            print(f"  '수입' in prop_name: {'수입' in prop_name}")

        # select 타입인 경우 옵션도 출력
        if prop_type == 'select':
            options = prop_data.get('select', {}).get('options', [])
            print(f"옵션: {[opt['name'] for opt in options]}")

        # formula 타입인 경우 수식 출력
        if prop_type == 'formula':
            formula = prop_data.get('formula', {})
            print(f"Formula 타입: {formula.get('type')}")
            print(f"Formula 표현식: {formula.get('expression', '없음')[:100]}")

        # relation 타입인 경우 연결된 DB 출력
        if prop_type == 'relation':
            relation = prop_data.get('relation', {})
            print(f"연결된 DB ID: {relation.get('database_id')}")
            print(f"Relation 타입: {relation.get('type')}")

        print("-" * 80)

except Exception as e:
    print(f"오류: {str(e)}")
