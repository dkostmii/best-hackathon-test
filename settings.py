import os
from dotenv import load_dotenv

load_dotenv()

DATABASE = {
    'NAME': os.environ.get('POSTGRES_DB') or 'postgres_local',
    'USER': os.environ.get("POSTGRES_USER") or 'postgres',
    'PASSWORD': os.environ.get("POSTGRES_PASSWORD") or 'postgres',
    'HOST': os.environ.get('PG_HOST') or 'db',
    'PORT': str(os.environ.get('PG_PORT', 5432)),
}

DB_URL = (
    f"postgresql://{DATABASE['USER']}"
    f":{DATABASE['PASSWORD']}"
    f"@{DATABASE['HOST']}"
    f":{DATABASE['PORT']}"
    f"/{DATABASE['NAME']}"
)
