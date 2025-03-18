import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@dvait123",
    database="billing_db"
)

cursor = db.cursor()

cursor.execute("SELECT * FROM customers")
customers = cursor.fetchall()

for customer in customers:
    print(customer)

db.close()
