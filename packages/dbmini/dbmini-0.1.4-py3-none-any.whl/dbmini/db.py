import mysql.connector as mysql_connector
import sqlite3
from pymongo import MongoClient
import pymysql


def mysql(user, password, host, port):
    try:
        conn = pymysql.connect(
            host=host,
            port=int(port),
            user=user,
            password=password
        )
        print("✅ MySQL connection established.")
        cur = conn.cursor()
        return conn, cur
    except pymysql.Error as err:
        print(f"❌ MySQL connection error: {err}")
        raise err
    
def sqlite(db_path):
    try:
        conn = sqlite3.connect(db_path)
        print("✅ SQLite connection established.")
        cur = conn.cursor()
        return conn, cur
    except sqlite3.Error as err:
        print(f"❌ SQLite connection error: {err}")
        raise err


def mongo(mongo_url,mongo_db):
    try:
        client = MongoClient(mongo_url)
        db = client[mongo_db]
        print("✅ MongoDB (filess.io) connection established.")
        return client, db
    except Exception as err:
        print(f"❌ MongoDB connection error: {err}")
        raise err


