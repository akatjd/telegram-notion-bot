import os
from dotenv import load_dotenv
from notion_client import Client
import json

load_dotenv()

NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')
notion = Client(auth=NOTION_API_KEY)

try:
    db = notion.databases.retrieve(database_id=NOTION_DATABASE_ID)

    print("Property names in JSON format:")
    print("=" * 80)

    properties = {}
    for prop_name, prop_data in db['properties'].items():
        properties[prop_name] = prop_data.get('type')

    print(json.dumps(properties, ensure_ascii=False, indent=2))

    print("\n" + "=" * 80)
    print("Title property name:")
    for prop_name, prop_data in db['properties'].items():
        if prop_data.get('type') == 'title':
            print(json.dumps(prop_name, ensure_ascii=False))

    print("\nDate property name:")
    for prop_name, prop_data in db['properties'].items():
        if prop_data.get('type') == 'date':
            print(json.dumps(prop_name, ensure_ascii=False))

except Exception as e:
    print(f"Error: {str(e)}")
