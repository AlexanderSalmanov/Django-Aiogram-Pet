# import sqlite3 as sq
# from pathlib import Path
#
# db_file_root_folder = Path(__file__).resolve().parent.parent
#
# def sql_start():
#     global base, cur
#     base = sq.connect(f'{db_file_root_folder}/db.sqlite3')
#     cur = base.cursor()
#     if base:
#         print('SQLite3 connection succeeded.')

import psycopg2

def connect_to_postgres():

    connection = psycopg2.connect(
        host='ec2-52-49-120-150.eu-west-1.compute.amazonaws.com',
        database='d9rl11060doqo7',
        user='wobyscjtgqnwjk',
        password='3bda89089492b05635ba885a65181d9b8c02742a140bf78e2af39541e9dc35d5'
    )

    cursor = connection.cursor()

    print('CONNECTED TO POSTGRES!')
