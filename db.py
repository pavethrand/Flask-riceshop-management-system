import mysql.connector
import datetime

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
    
    def check_customer_username(self,username):
        self.connect()
        query = "SELECT * FROM customer WHERE username = '%s'"
        self.cursor.execute(query % username)
        result = self.cursor.fetchall()
        self.close()
        return bool(result)
    
    def customer_signup(self,username,fullname,password,mobile,address,verify):
        self.connect()
        dor = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = (username, fullname, password, mobile, address, dor, verify)
        sql = 'INSERT INTO customer (username, fullname, password, mobile, address, dor, verified) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        self.cursor.execute(sql, values)
        self.conn.commit()
        inserted = self.cursor.rowcount
        self.close()
        return inserted
    
    def verify_otp(self, username):
        self.connect()
        sql = 'UPDATE customer SET verified = 1 WHERE username = %s'
        values = (username,)
        self.cursor.execute(sql, values)
        self.conn.commit()
        updated = self.cursor.rowcount
        self.close()
        return updated
    
    def verify_cus(self,username):
        self.connect()
        tablename='customer'
        query = "SELECT mobile FROM {} WHERE username = %s AND verified = 0".format(tablename)
        values = (username,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        self.close()
        if result:
            mobile = result[0]
            return True, mobile
        return False, None
    
    def view_products_category(self):
        self.connect()
        self.cursor.execute("SELECT DISTINCT category FROM product_details")
        product = self.cursor.fetchall()
        self.close()
        return product
    
    def view_products_selected(self,category):
        self.connect()
        query= "SELECT * FROM product_details where category = %s"
        values=(category,)
        self.cursor.execute(query, values)
        product = self.cursor.fetchall()
        self.close()
        return product

