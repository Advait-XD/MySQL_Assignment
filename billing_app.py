import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTableWidget, QTableWidgetItem, QTabWidget, 
                             QMessageBox, QFormLayout)
from PySide6.QtCore import Qt
import mysql.connector

class BillingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billing System")
        self.setGeometry(100, 100, 800, 600)
        
        # Database connection
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "@dvait123",
            "database": "billing_db"
        }
        
        # Create tabs
        self.setup_ui()
        
        # Load data
        self.load_customers()
    
    def setup_ui(self):
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create tabs
        self.customer_tab = QWidget()
        self.billing_tab = QWidget()
        
        # Add tabs to widget
        self.tabs.addTab(self.customer_tab, "Customers")
        self.tabs.addTab(self.billing_tab, "Billing")
        
        # Setup customer tab
        self.setup_customer_tab()
        
        # Setup billing tab
        self.setup_billing_tab()
        
        # Set central widget
        self.setCentralWidget(self.tabs)
    
    def setup_customer_tab(self):
        layout = QVBoxLayout()
        
        # Form for adding customers
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        
        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Email:", self.email_input)
        
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Customer")
        self.add_btn.clicked.connect(self.add_customer)
        
        self.update_btn = QPushButton("Update Customer")
        self.update_btn.clicked.connect(self.update_customer)
        
        self.delete_btn = QPushButton("Delete Customer")
        self.delete_btn.clicked.connect(self.delete_customer)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)
        
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)
        layout.addWidget(btn_widget)
        
        # Table for displaying customers
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Email"])
        self.customer_table.horizontalHeader().setStretchLastSection(True)
        self.customer_table.verticalHeader().setVisible(False)
        self.customer_table.clicked.connect(self.select_customer)
        
        layout.addWidget(self.customer_table)
        
        self.customer_tab.setLayout(layout)
    
    def setup_billing_tab(self):
        layout = QVBoxLayout()
        
        # Form for creating bills
        form_layout = QFormLayout()
        
        self.customer_id_input = QLineEdit()
        self.amount_input = QLineEdit()
        self.description_input = QLineEdit()
        
        form_layout.addRow("Customer ID:", self.customer_id_input)
        form_layout.addRow("Amount:", self.amount_input)
        form_layout.addRow("Description:", self.description_input)
        
        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.create_bill_btn = QPushButton("Create Bill")
        self.create_bill_btn.clicked.connect(self.create_bill)
        
        btn_layout.addWidget(self.create_bill_btn)
        
        btn_widget = QWidget()
        btn_widget.setLayout(btn_layout)
        layout.addWidget(btn_widget)
        
        # Table for displaying bills
        self.bill_table = QTableWidget()
        self.bill_table.setColumnCount(5)
        self.bill_table.setHorizontalHeaderLabels(["ID", "Customer ID", "Amount", "Description", "Date"])
        self.bill_table.horizontalHeader().setStretchLastSection(True)
        self.bill_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.bill_table)
        
        self.billing_tab.setLayout(layout)
        
        # Load bills
        self.load_bills()
    
    def db_connect(self):
        try:
            conn = mysql.connector.connect(**self.db_config)
            return conn
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Could not connect to database: {err}")
            return None
    
    def load_customers(self):
        try:
            conn = self.db_connect()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM customers")
                customers = cursor.fetchall()
                
                self.customer_table.setRowCount(0)
                
                for row_num, customer in enumerate(customers):
                    self.customer_table.insertRow(row_num)
                    for col_num, data in enumerate(customer):
                        self.customer_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
                
                cursor.close()
                conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Could not fetch customers: {err}")
    
    def load_bills(self):
        try:
            conn = self.db_connect()
            if conn:
                cursor = conn.cursor()
                # Check if bills table exists
                cursor.execute("SHOW TABLES LIKE 'bills'")
                if not cursor.fetchone():
                    cursor.execute("""
                        CREATE TABLE bills (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            customer_id INT,
                            amount DECIMAL(10, 2),
                            description TEXT,
                            bill_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (customer_id) REFERENCES customers(id)
                        )
                    """)
                    conn.commit()
                
                cursor.execute("SELECT * FROM bills")
                bills = cursor.fetchall()
                
                self.bill_table.setRowCount(0)
                
                for row_num, bill in enumerate(bills):
                    self.bill_table.insertRow(row_num)
                    for col_num, data in enumerate(bill):
                        self.bill_table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
                
                cursor.close()
                conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Could not fetch bills: {err}")
    
    def add_customer(self):
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        
        if not name or not phone:
            QMessageBox.warning(self, "Input Error", "Name and phone are required!")
            return
        
        try:
            conn = self.db_connect()
            if conn:
                cursor = conn.cursor()
                query = "INSERT INTO customers (name, phone, email) VALUES (%s, %s, %s)"
                values = (name, phone, email)
                cursor.execute(query, values)
                conn.commit()
                
                QMessageBox.information(self, "Success", "Customer added successfully!")
                
                # Clear inputs
                self.name_input.clear()
                self.phone_input.clear()
                self.email_input.clear()
                
                # Refresh table
                self.load_customers()
                
                cursor.close()
                conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Could not add customer: {err}")
    
    def select_customer(self):
        row = self.customer_table.currentRow()
        if row > -1:
            self.customer_id = self.customer_table.item(row, 0).text()
            self.name_input.setText(self.customer_table.item(row, 1).text())
            self.phone_input.setText(self.customer_table.item(row, 2).text())
            self.email_input.setText(self.customer_table.item(row, 3).text())
    
    def update_customer(self):
        if not hasattr(self, "customer_id"):
            QMessageBox.warning(self, "Selection Error", "Please select a customer first!")
            return
        
        name = self.name_input.text()
        phone = self.phone_input.text()
        email = self.email_input.text()
        
        if not name or not phone:
            QMessageBox.warning(self, "Input Error", "Name and phone are required!")
            return
        
        try:
            conn = self.db_connect()
            if conn:
                cursor = conn.cursor()
                query = "UPDATE customers SET name = %s, phone = %s, email = %s WHERE id = %s"
                values = (name, phone, email, self.customer_id)
                cursor.execute(query, values)
                conn.commit()
                
                QMessageBox.information(self, "Success", "Customer updated successfully!")
                
                # Clear inputs
                self.name_input.clear()
                self.phone_input.clear()
                self.email_input.clear()
                
                # Refresh table
                self.load_customers()
                
                cursor.close()
                conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Could not update customer: {err}")
    
    def delete_customer(self):
        if not hasattr(self, "customer_id"):
            QMessageBox.warning(self, "Selection Error", "Please select a customer first!")
            return
        
        confirm = QMessageBox.question(self, "Confirm Delete", 
                                      "Are you sure you want to delete this customer?",
                                      QMessageBox.Yes | QMessageBox.No)
        
        if confirm == QMessageBox.Yes:
            try:
                conn = self.db_connect()
                if conn:
                    cursor = conn.cursor()
                    query = "DELETE FROM customers WHERE id = %s"
                    values = (self.customer_id,)
                    cursor.execute(query, values)
                    conn.commit()
                    
                    QMessageBox.information(self, "Success", "Customer deleted successfully!")
                    
                    # Clear inputs
                    self.name_input.clear()
                    self.phone_input.clear()
                    self.email_input.clear()
                    
                    # Refresh table
                    self.load_customers()
                    
                    cursor.close()
                    conn.close()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Database Error", f"Could not delete customer: {err}")
    
    def create_bill(self):
        customer_id = self.customer_id_input.text()
        amount = self.amount_input.text()
        description = self.description_input.text()
        
        if not customer_id or not amount:
            QMessageBox.warning(self, "Input Error", "Customer ID and amount are required!")
            return
        
        try:
            conn = self.db_connect()
            if conn:
                cursor = conn.cursor()
                query = "INSERT INTO bills (customer_id, amount, description) VALUES (%s, %s, %s)"
                values = (customer_id, amount, description)
                cursor.execute(query, values)
                conn.commit()
                
                QMessageBox.information(self, "Success", "Bill created successfully!")
                
                # Clear inputs
                self.customer_id_input.clear()
                self.amount_input.clear()
                self.description_input.clear()
                
                # Refresh table
                self.load_bills()
                
                cursor.close()
                conn.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Could not create bill: {err}")

def main():
    app = QApplication(sys.argv)
    window = BillingApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()