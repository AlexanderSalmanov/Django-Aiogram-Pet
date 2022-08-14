import os
import dotenv
from pathlib import Path

ENV_DIR = os.path.join(Path(__file__).resolve().parent.parent, '.env')
dotenv.read_dotenv(ENV_DIR)

from pyairtable import Table

api_key = os.environ.get('AIRTABLE_API_KEY')
base_id = os.environ.get('AIRTABLE_BASE_ID')

table = Table(api_key, base_id, 'Users')



def airtable_record_filler(table, tg_id, tg_username, tg_fullname, username, email, password):
    data = {
        'tg_id': tg_id,
        'tg_username': tg_username,
        'tg_fullname': tg_fullname,
        'username': username,
        'email': email,
        'password': password
    }


    record = table.create(data)
    print("AIRTABLE RECORD ADDED")
