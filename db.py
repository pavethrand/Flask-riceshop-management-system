import mysql.connector

db = mysql.connector.connect()

class RiceDatabase:
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        self.conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='riceshop'
        )
        self.cursor = self.conn.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def check_login(self,tablename,username,password):
        self.connect()
        query = "SELECT * FROM {} WHERE username = %s AND password = %s".format(tablename)
        values = (username, password)
        self.cursor.execute(query, values)
        result = self.cursor.fetchall()
        self.close()
        return bool(result)
    
    def view_employees(self):
        self.connect()
        self.cursor.execute("SELECT * FROM employee")
        employees = self.cursor.fetchall()
        self.close()
        return employees
    
    def view_customers(self):
        self.connect()
        self.cursor.execute("SELECT * FROM customer")
        customer = self.cursor.fetchall()
        self.close()
        return customer
    
    def unverify_customers_list(self):
        self.connect()
        self.cursor.execute("SELECT * FROM customer where verified = 0")
        customer = self.cursor.fetchall()
        self.close()
        return customer
    
    def view_products(self):
        self.connect()
        self.cursor.execute("SELECT * FROM product_details")
        product = self.cursor.fetchall()
        self.close()
        return product
    
    def view_suppliers(self):
        self.connect()
        self.cursor.execute("SELECT * FROM supplier")
        supplier = self.cursor.fetchall()
        self.close()
        return supplier
    
    def view_billing(self):
        self.connect()
        self.cursor.execute("SELECT * FROM order_details")
        order = self.cursor.fetchall()
        self.close()
        return order
    
