import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="@dvait123",
    database="billing_db"
)

cursor = db.cursor()

# Insert a sample customer
query = "INSERT INTO customers (name, phone, email) VALUES (%s, %s, %s)"
values = ("John Doe", "1234567890", "johndoe@example.com")
cursor.execute(query, values)

db.commit()  # Save changes
print("Customer inserted successfully!")

db.close()
