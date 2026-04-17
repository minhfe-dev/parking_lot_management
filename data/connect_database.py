import mysql.connector

db = mysql.connector.connect(
    user='root',
    password='12345678',
    host='localhost'
)

cur = db.cursor()
cur.execute("CREATE DATABASE QLBGX")