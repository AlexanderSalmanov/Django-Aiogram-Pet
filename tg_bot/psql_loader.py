import psycopg2

import dotenv
from pathlib import Path

ENV_DIR = os.path.join(Path(__file__).resolve().parent.parent, '.env')
dotenv.read_dotenv(ENV_DIR)


def connect_to_postgres():

    connection = psycopg2.connect(
        host= os.environ.get('PSQL_DB_HOST'),
        database=os.environ.get('PSQL_DB_NAME'),
        user=os.environ.get('PSQL_USER'),
        password=os.environ.get('PSQL_PASSWORD')
    )

    cursor = connection.cursor()

    print('CONNECTED TO POSTGRES!')
