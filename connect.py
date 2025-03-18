import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@dvait123",
    database="billing_db"
)

# Check the connection
if db.is_connected():
    print("Connected to MySQL successfully!")

db.close()
