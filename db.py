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


    #verify customer,employee for login
    def check_login(self,tablename,username,password):
        self.connect()
        query = "SELECT * FROM {} WHERE username = %s AND password = %s".format(tablename)
        values = (username, password)
        self.cursor.execute(query, values)
        result = self.cursor.fetchall()
        self.close()
        return bool(result)
    
    #give the customer is verified or not
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
    
    #customer -> check the username is already present in db or not
    def check_customer_username(self,username):
        self.connect()
        query = "SELECT * FROM customer WHERE username = '%s'"
        self.cursor.execute(query % username)
        result = self.cursor.fetchall()
        self.close()
        return bool(result)
    
    #customer -> customer_signup
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
    
    #customer-> verified 
    def verify_otp(self, username):
        self.connect()
        sql = 'UPDATE customer SET verified = 1 WHERE username = %s'
        values = (username,)
        self.cursor.execute(sql, values)
        self.conn.commit()
        updated = self.cursor.rowcount
        self.close()
        return updated
    
    #customer -> see all product categories
    def view_products_category(self):
        self.connect()
        self.cursor.execute("SELECT DISTINCT category FROM product_details")
        product = self.cursor.fetchall()
        self.close()
        return product
    
    #customer -> see details of particular category
    def view_products_selected(self,category):
        self.connect()
        query= "SELECT product_id,brand,category,availability,quantity,ros FROM product_details where quantity != 0 and category = %s"
        values=(category,)
        self.cursor.execute(query, values)
        product = self.cursor.fetchall()
        self.close()
        return product
    
    #customer -> get particular product by product_id
    def get_product_details(self,id):
        self.connect()
        query= "SELECT product_id,brand,category,availability,quantity,ros FROM product_details where product_id= %s"
        values=(id,)
        self.cursor.execute(query, values)
        product_details = self.cursor.fetchone()
        self.close()
        return product_details
    
    #customer->order backend work
    def product_availability(self,id):
        self.connect()
        query= "SELECT quantity,ros FROM product_details where product_id= %s"
        values=(id,)
        self.cursor.execute(query, values)
        product_details = self.cursor.fetchone()
        self.close()
        return product_details
    
    #customer->add order to order table
    def add_order(self,username,productid,quantity,rate):
        self.connect()
        doo = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        status='ORDERED'
        values = (username, productid, quantity, rate, doo, status)
        sql = 'INSERT INTO order_details (username, product_id, quantity, roo,doo,status) VALUES (%s, %s, %s, %s, %s, %s)'
        self.cursor.execute(sql, values)
        self.conn.commit()
        inserted = self.cursor.rowcount
        self.close()
        return inserted
    
    #customer->reduce order in product table
    def reduce_product(self, id,quantity):
        self.connect()
        sql = 'UPDATE product_details SET quantity = %s WHERE product_id = %s'
        values = (quantity,id)
        self.cursor.execute(sql, values)
        self.conn.commit()
        updated = self.cursor.rowcount
        self.close()
        return updated
    
    #customer->fetch value for order cancel
    def product_fetch_for_cancel(self, username):
        self.connect()
        query = """
            SELECT o.order_id, o.product_id, o.quantity, p.brand, p.category, p.availability, o.roo, o.doo
            FROM order_details o
            INNER JOIN product_details p ON o.product_id = p.product_id
            WHERE o.username = %s
        """
        self.cursor.execute(query, (username,))
        orders = self.cursor.fetchall()
        self.close()
        return orders
    



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
