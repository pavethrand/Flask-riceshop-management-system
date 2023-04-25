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
            WHERE o.username = %s AND o.status = 'ORDERED';
        """
        self.cursor.execute(query, (username,))
        orders = self.cursor.fetchall()
        self.close()
        return orders
    
    #customer-> order cancel to cancel table
    def add_cancel_order_to_cancel_table(self,orderid,username):
        self.connect()
        doc = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = (username, orderid,doc)
        sql = 'INSERT INTO order_cancellation(username, order_id, doc) VALUES (%s, %s, %s)'
        self.cursor.execute(sql, values)
        self.conn.commit()
        inserted = self.cursor.rowcount
        self.close()
        return inserted
    
    #customer -> get order_quantity by order id
    def get_order_quantity_by_id(self,id):
        self.connect()
        query= "SELECT quantity FROM order_details where order_id= %s"
        values=(id,)
        self.cursor.execute(query, values)
        quantity = self.cursor.fetchone()
        self.close()
        return quantity
    
    #customer-> return add the product value to product table
    def update_product_quantity_on_cancel(self, id, add_quantity):
        self.connect()
        self.cursor.execute("UPDATE product_details SET quantity = quantity + %s WHERE product_id IN (SELECT product_id FROM order_details WHERE order_id = %s)", (add_quantity, id))
        self.conn.commit()
        self.close()
        return True
    
    #customer-> update status
    def update_order_details_to_cancel(self, id):
        try:
            self.connect()
            status = 'CANCELLED'
            sql = "UPDATE order_details SET status = %s WHERE order_id = %s"
            values = (status, id)
            self.cursor.execute(sql, values)
            self.conn.commit()
            updated = self.cursor.rowcount
            return updated
        except Exception as e:
            print("Error while updating order details:", e)
        finally:
            self.close()
            return updated
        
    #customer -> values for history
    def product_fetch_for_history(self, username):
        self.connect()
        query = """
            SELECT o.order_id, o.product_id, p.brand, p.category, p.availability,o.quantity, o.roo, o.doo, o.status
            FROM order_details o 
            INNER JOIN product_details p ON o.product_id = p.product_id
            WHERE o.username = %s;
        """
        self.cursor.execute(query, (username,))
        orders = self.cursor.fetchall()
        self.close()
        return orders

#customer completed....

    #admin-> view employee list
    def view_employees(self):
        self.connect()
        self.cursor.execute("SELECT * FROM employee")
        employees = self.cursor.fetchall()
        self.close()
        return employees
    
    #admin-> delete employee
    def delete_employee(self, username):
        self.connect()
        self.cursor.execute("DELETE FROM employee WHERE username=%s", (username,))
        self.conn.commit()
        self.close()
        return True
    
    #admin-> check employee username presence in database
    def check_employee_username(self,username):
        self.connect()
        query = "SELECT * FROM employee WHERE username = '%s'"
        self.cursor.execute(query % username)
        result = self.cursor.fetchall()
        self.close()
        return bool(result)
    
    #admin->add employee
    def add_employee_todb(self,username,fullname,password,mobile,address):
        self.connect()
        dor = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = (username, fullname, password, mobile, address, dor)
        sql = 'INSERT INTO employee (username, fullname, password, mobile, address, dor) VALUES ( %s, %s, %s, %s, %s, %s)'
        self.cursor.execute(sql, values)
        self.conn.commit()
        inserted = self.cursor.rowcount
        self.close()
        return inserted
    
    #admin -> get_employee_details_by_username
    def get_employee_details_by_username(self,username):
        self.connect()
        query= "SELECT username,fullname,password,mobile,address FROM employee where username = %s"
        values=(username,)
        self.cursor.execute(query, values)
        employee_details = self.cursor.fetchone()
        self.close()
        return employee_details
    
    #admin-> update employee
    def edit_employee_todb(self, username, fullname, password, mobile, address):
        self.connect()
        sql = "UPDATE employee SET fullname = %s, password = %s, mobile = %s, address = %s WHERE username = %s"
        values = (fullname, password, mobile, address, username)
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Error due to ", error)
            return False
        finally:
            self.close()
            return True
        
    #admin, employee -> show customers in add customer page
    def view_customers(self):
        self.connect()
        self.cursor.execute("SELECT * FROM customer")
        customer = self.cursor.fetchall()
        self.close()
        return customer
    
    #admin,employee -> delete customer
    def delete_customer(self, username):
        self.connect()
        self.cursor.execute("DELETE FROM customer WHERE username=%s", (username,))
        self.conn.commit()
        self.close()
        return True
    
    #admin,employee -> get_customer_details_by_username
    def get_customer_details_by_username(self,username):
        self.connect()
        query= "SELECT username,fullname,password,mobile,address FROM customer where username = %s"
        values=(username,)
        self.cursor.execute(query, values)
        customer_details = self.cursor.fetchone()
        self.close()
        return customer_details
    
    #admin,employee -> update customer
    def edit_customer_todb(self, username, fullname, password, mobile, address):
        self.connect()
        sql = "UPDATE customer SET fullname = %s, password = %s, mobile = %s, address = %s WHERE username = %s"
        values = (fullname, password, mobile, address, username)
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Error due to ", error)
            return False
        finally:
            self.close()
            return True

    #admin,employee -> get unverified customers
    def unverify_customers_list(self):
        self.connect()
        self.cursor.execute("SELECT * FROM customer where verified = 0")
        customer = self.cursor.fetchall()
        self.close()
        return customer
    
    #admin,employee -> view product details
    def view_products(self):
        self.connect()
        self.cursor.execute("SELECT * FROM product_details")
        product = self.cursor.fetchall()
        self.close()
        return product
    
    #admin,employee -> add product 
    def add_product_todb(self,brand,category,availability,quantity,rop,ros):
        self.connect()
        values = (brand,category,availability,quantity,rop,ros)
        sql = 'INSERT INTO product_details (brand,category,availability,quantity,rop,ros) VALUES ( %s, %s, %s, %s, %s, %s)'
        self.cursor.execute(sql, values)
        self.conn.commit()
        inserted = self.cursor.rowcount
        self.close()
        return inserted
    
    #admin,employee -> get_product_details_by_id
    def get_product_details_by_id(self,id):
        self.connect()
        query= "SELECT * FROM product_details where product_id = %s"
        values=(id,)
        self.cursor.execute(query, values)
        product__details = self.cursor.fetchone()
        self.close()
        return product__details
    
    #admin,employee -> edit product values in db
    def edit_product_todb(self,id,brand,category,availability,quantity,rop,ros):
        self.connect()
        sql = "UPDATE product_details SET brand = %s, category = %s, availability = %s, quantity = %s,rop = %s, ros = %s WHERE product_id = %s"
        values = (brand,category,availability,quantity,rop,ros,id)
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Error due to ", error)
            return False
        finally:
            self.close()
            return True

    #admin,employee -> view all suppliers
    def view_suppliers(self):
        self.connect()
        self.cursor.execute("SELECT * FROM supplier")
        supplier = self.cursor.fetchall()
        self.close()
        return supplier
    
    #admin,employee -> check supplier name already present in db or not
    def checksupplier_name(self, supplier):
        self.connect()
        query = "SELECT * FROM supplier WHERE supplier = '%s'"
        self.cursor.execute(query % supplier)
        result = self.cursor.fetchall()
        self.close()
        return bool(result)
    
    #admin,employee -> add supplier 
    def add_product_todb(self,supplier,mobile,address):
        self.connect()
        dor = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = (supplier,mobile,address,dor)
        sql = 'INSERT INTO supplier (supplier,mobile,address,dor) VALUES ( %s, %s, %s, %s)'
        self.cursor.execute(sql, values)
        self.conn.commit()
        inserted = self.cursor.rowcount
        self.close()
        return inserted
    
    #admin,employee -> get_supplier_details_by_supplier
    def get_supplier_details_by_supplier(self,supplier):
        self.connect()
        query= "SELECT * FROM supplier where supplier = %s"
        values=(supplier,)
        self.cursor.execute(query, values)
        supplier_details = self.cursor.fetchone()
        self.close()
        return supplier_details
    
    #admin,employee -> update supplier values
    def edit_supplier_todb(self,supplier,mobile,address):
        self.connect()
        sql = "UPDATE supplier SET mobile = %s, address = %s WHERE supplier = %s"
        values = (mobile,address,supplier)
        try:
            self.cursor.execute(sql, values)
            self.conn.commit()
            return True
        except mysql.connector.Error as error:
            print("Error due to ", error)
            return False
        finally:
            self.close()
            return True
        
    def make_purchase_for_shop(self,product_id,supplier,bag,quantity,rop):
        self.connect()
        dop = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        values = (product_id,supplier,bag,quantity,rop)
        sql = 'INSERT INTO purchase_details (product_id,supplier,bag,quantity,rop) VALUES ( %s, %s, %s, %s,%s)'
        self.cursor.execute(sql, values)
        self.conn.commit()
        inserted = self.cursor.rowcount
        self.close()
        return inserted
    
    def update_product_quantity_after_purchase(self, id, add_quantity):
        self.connect()
        self.cursor.execute("UPDATE product_details SET quantity = quantity + %s WHERE product_id = %s", (add_quantity, id))
        self.conn.commit()
        self.close()
        return True




    
    def view_billing(self):
        self.connect()
        self.cursor.execute("SELECT * FROM order_details")
        order = self.cursor.fetchall()
        self.close()
        return order
    
    
