# dbmini

`dbmini` is a lightweight Python library to quickly connect to **MySQL**, **SQLite**, and **MongoDB** databases.  
It is designed to be simple, flexible, and easy to integrate into any project.

---

## 🔹 Features

- Connect to **MySQL** databases.
- Connect to **SQLite** databases (local or in-memory).
- Connect to **MongoDB** databases (e.g., hosted on filess.io or local).
- Minimal configuration — credentials are passed as parameters.
- Interactive database operations can be done easily in Python scripts.

---

## 🔹 Installation

Install via PyPI:

```bash
pip install dbmini

---

## 🔹 Steps to use

To use MySQL, you can call the mysql function by passing the username, password, host, and port as parameters. For example:

from dbmini import mysql
conn, cur = mysql(user="user_name", password="user_password", host="localhost", port=port_number)

---


For SQLite, you can call the sqlite function by passing the path to the database file. 
For example:

from dbmini import sqlite
conn, cur = sqlite("your_db_path")

---

For MongoDB, you can call the mongo function by passing the MongoDB connection URL and the database name you want to connect to. 
For example:

from dbmini import mongo
client, db = mongo(mongo_url="filess.io_mongo_url", mongo_db="your_db_name")
