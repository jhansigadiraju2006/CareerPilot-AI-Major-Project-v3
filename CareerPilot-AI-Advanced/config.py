import os
from pathlib import Path
BASE_DIR=Path(__file__).resolve().parent
DB_PATH=BASE_DIR/'data'/'careerpilot.db'
KNOWLEDGE_DIR=BASE_DIR/'data'/'knowledge'
SECRET_KEY=os.getenv('CAREERPILOT_SECRET','careerpilot-local-demo-secret')
MODEL=os.getenv('CAREERPILOT_MODEL','llama3.2:3b')
