import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="smart_campus"
)

cursor = db.cursor()