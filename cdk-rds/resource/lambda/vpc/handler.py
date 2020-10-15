
import pymysql
import os


def main(event=None, content=None):
    conn = pymysql.connect(
        host=os.environ['host'],
        user=os.environ['username'],
        password=os.environ['password'],
    )
    return conn
