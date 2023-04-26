#import required libraries
from flask import Flask,render_template,request,url_for,redirect,session,make_response,send_file
import re
import pdfkit
#from sendsms import Fast2SMS

#sms initialize
# sms_api_key = 'API_KEY'
# sms_client = Fast2SMS(sms_api_key)

#import database file
from db import RiceDatabase

#import OTP class
from otp import OTPGenerator

#create app
app = Flask(__name__)
app.secret_key = 'obito_uchiha'

#create db connection
db = RiceDatabase()
db.connect()

#initialize the class and otp veriable
otp = OTPGenerator()
generated_otp=None

config_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
config = pdfkit.configuration(wkhtmltopdf=config_path)

#index page
@app.route('/')
def home():
    return render_template('index.html')

#customer login
@app.route('/logincus/',methods=['POST','GET'])
def logincus():
    if request.method == 'GET':
        #destroy session -> if set
        if 'customer' in session:
            session.pop('customer', None)
        return render_template('customer/login.html',error=False)
    user = request.form['username']
    password = request.form['password']
    res = db.check_login('customer',user,password)
    if res == True:
        res_unverified,mail=db.verify_cus(user)
        if res_unverified:
            return redirect(url_for('verifyotp',mail=mail,user=user))
        #set session to login customer
        session['customer'] = user
        return redirect(url_for('cus_dashboard'))
    return render_template('customer/login.html',error=True)

#customer->dashboard
@app.route('/cdashboard/',methods=['GET','POST'])
def cus_dashboard():
    if 'customer' not in session:
        return redirect(url_for('logoutall'))
    return render_template('customer/dashboard.html',username = session['customer'])

#customer->signup page
@app.route('/signup/',methods=['POST','GET'])
def cussignup():
    list = []
    if request.method == 'GET':
        return render_template('customer/signup.html',message='',list=list)
    username = request.form['username']
    fullname = request.form['fullname']
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    mail = request.form['email']
    address = request.form['address']
    list = [username,fullname,password,confirm_password,mail,address]
    if db.check_customer_username(username):
        list[0]=''
        return render_template('customer/signup.html',message='username already exists',list=list)
    elif len(username) < 8:
        list[0]=''
        return render_template('customer/signup.html',message='username should be greater than or equal to 8 characters',list=list)
    elif len(username) > 15: 
        list[0]=''
        return render_template('customer/signup.html',message='username should be less than or equal to 15 characters',list=list)
    elif len(fullname) < 5:
        list[1]=''
        return render_template('customer/signup.html',message='Fullname should be greater than or equal to 5 characters',list=list)
    elif len(fullname) > 40: 
        list[1]=''
        return render_template('customer/signup.html',message='Fullname should be less than or equal to 40 characters',list=list)
    elif bool(re.match('^[a-zA-Z]+$',fullname)) == False:
        list[1]=''
        return render_template('customer/signup.html',message='Fullname should contain Alphabets only',list=list)
    elif bool(re.match('^[a-z0-9]+$',username)) == False:
        list[0]=''
        return render_template('customer/signup.html',message='Username should contain Alphabets and numbers only',list=list)
    elif bool(re.match('^(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,20}$',password)) == False:
        list[2]=''
        return render_template('customer/signup.html',message='Password should contain 8-20 characters and atleast one special characters and one number',list=list)
    elif password != confirm_password:
        list[3]=''
        return render_template('customer/signup.html',message='Password and Confirm Password must be same',list=list) 
    elif not re.match(r'^[\w-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]+$', mail):
        list[4] = ''
        return render_template('customer/signup.html', message='Enter a valid email address', list=list)
    values_upload = db.customer_signup(username,fullname,password,mail,address,verify=0)
    if values_upload > 0:
        #set session to signup
        session['unverified'] = username
        return redirect(url_for('verifyotp',mail=mail,user=session['unverified']))
    return render_template('customer/signup.html',message='Error in Signup.....',list=list)

#customer->OTP Validation
@app.route('/otp/<string:mail>/<string:user>',methods=['GET','POST'])
def verifyotp(mail,user):
    global generated_otp
    if request.method == 'GET':
        if session.get('unverified') == user:
            generated_otp=otp.generate_otp()
            return render_template('customer/otp.html',mail=mail,user=user)
        return redirect(url_for('logincus',error=False))
    
    if session.get('unverified') == user:
        user_otp = request.form['otp1']
        user_otp = user_otp + request.form['otp2']
        user_otp = user_otp + request.form['otp3']
        user_otp = user_otp + request.form['otp4']
        session.pop('unverified', None)
        if user_otp == generated_otp:
            generated_otp = None
            updated = db.verify_otp(user)
            if updated > 0:
                return render_template('/customer/otp_verified.html', value="success")
            return render_template('/customer/otp_verified.html', value="db_error")
        return render_template('/customer/otp_verified.html', value="otp_error")
    return redirect(url_for('logincus',error=False))

#customer,employee,admin -> logout
@app.route('/logout/',methods=['GET','POST'])
def logoutall():
    if 'customer' in session:
        session.pop('customer', None)
        return redirect(url_for('logincus',error=False))
    if 'employee' in session:
        session.pop('employee', None)
        return redirect(url_for('loginemp',error=False))
    if 'admin' in session:
        session.pop('admin', None)
        return redirect(url_for('loginemp',error=False))
    return redirect(url_for('home'))

#customer->make order
@app.route('/makeorderbycustomer/',methods=['GET','POST'])
def makeorderbycustomer():
    if 'customer' not in session:
        return redirect(url_for('logoutall'))    
    dropdown_values = db.view_products_category()
    if request.method == 'GET': 
        return render_template('customer/orderpage.html',category=dropdown_values,selected=None)
    selected_category = request.form.get('product')
    if selected_category == 'null':
        return render_template('customer/orderpage.html',category=dropdown_values,selected=None)
    selected = db.view_products_selected(selected_category)
    return render_template('customer/orderpage.html',category=dropdown_values,selected=selected)

#customer->orderconfirm page
@app.route('/placeorder/<int:prt_id>/<string:user>')
def place_order(prt_id,user):
    if 'customer' not in session or user != session['customer']:
        return redirect(url_for('logoutall'))
    product_detail = db.get_product_details(prt_id)
    return render_template('customer/orderpage2.html',product=product_detail)

#customer -> placing order in backend
@app.route('/order_done/',methods=['GET','POST'])
def order_done():
    if 'customer' not in session:
        return redirect(url_for('logoutall'))
    product_id = request.form.get('product_id')
    total_product = request.form.get('total_product')
    check_availability = db.product_availability(product_id)
    if check_availability[0] < int(total_product):
        return "<html><body><script>alert('Entered value is greater than available quantity')</script></body></html>"
    order_add=db.add_order(session['customer'],product_id,int(total_product),(float(total_product) * float(check_availability[1])))
    if order_add:
        reduce_product = db.reduce_product(product_id,check_availability[0]-int(total_product))
        if reduce_product:
            return render_template('customer/orderdone.html',value='success')
    return render_template('customer/orderdone.html',value='error')

#customer->order_cancel page
@app.route('/cordercancel/',methods=['GET','POST'])
def cordercancel():
    if 'customer' not in session:
        return redirect(url_for('logoutall'))
    placed_orders=db.product_fetch_for_cancel(session['customer'])
    return render_template('customer/ordercancel.html',orders=placed_orders)

#customer-> order cancell process
@app.route('/cordercancel/<int:orderid>/',methods=['GET','POST'])
def ordercancelling(orderid):
    if 'customer' not in session:
        return redirect(url_for('logoutall'))
    db.add_cancel_order_to_cancel_table(orderid,session['customer'])
    get_quantity = db.get_order_quantity_by_id(orderid)
    db.update_product_quantity_on_cancel(orderid,get_quantity[0])
    update = db.update_order_details_to_cancel(orderid)
    return redirect('/cordercancel/')

@app.route('/corderhistory/')
def corderhistory():
    if 'customer' not in session:
        return redirect(url_for('logoutall'))
    order_history = db.product_fetch_for_history(session['customer'])
    return render_template('customer/orderhistory.html',order_history=order_history)

# customer login backend completed

# now admin,employee works.......

# admin,employee -> login page
@app.route('/loginemp/',methods=['POST','GET'])
def loginemp():
    if 'customer' in session or 'admin' in session or 'employee' in session:
        return redirect(url_for('logoutall'))
    if request.method == 'GET':
        return render_template('employee/login.html',error=False)

    user = request.form['username']
    password = request.form['password']
    if user == 'admin' and password == 'admin':
        session['admin'] = user
        return redirect('/edashboard/')
    res = db.check_login('employee',user,password)
    if res == True:
        session['employee'] = user
        return redirect('/edashboard/')
    return render_template('employee/login.html',error=True)

#admin,employee -> dashboard
@app.route('/edashboard/')
def edashboard():
    if 'employee' in session:
        return render_template('employee/dashboard.html',user=session['employee'])
    elif 'admin' in session:
        return render_template('employee/dashboard.html',user=session['admin'])
    return redirect(url_for('logoutall'))

#admin -> add,edit,delete employee
@app.route('/editemployee/',methods=['POST','GET'])
def editemp():
    if 'admin' in session:
        employees = db.view_employees()
        if request.method == 'GET':
            return render_template('employee/addemployee.html',employees=employees,error=None)
        if request.method == 'POST':
             username = request.form.get('username')
             fullname = request.form.get('fullname')
             password = request.form.get('password')
             mobile = request.form.get('mobile')
             address = request.form.get('address')
             if not (8 <= len(username) <= 15):
                return render_template('employee/addemployee.html',employees=employees,error="Username should be between 8 to 15 characters")
             if not (5 <= len(fullname) <= 40):
                return render_template('employee/addemployee.html',employees=employees,error="Enter Valid Full Name(5-40 characters)")
             if not (8 <= len(password) <= 20):
                return render_template('employee/addemployee.html',employees=employees,error="invalid password length (8-20 characters)")
             if not (len(mobile) == 10 and mobile.isdigit()):
                return render_template('employee/addemployee.html',employees=employees,error="Error due to invalid mobile number (10 numbers only)")
             if len(address) == 0:
                return render_template('employee/addemployee.html',employees=employees,error="Enter address please....")
             if db.check_employee_username(username):
                 return render_template('employee/addemployee.html',employees=employees,error="username already exists")
             add_employee = db.add_employee_todb(username,fullname,password,mobile,address)
             if add_employee:
                 return redirect('/editemployee/')
             return render_template('employee/addemployee.html',employees=employees,error="Error in updating in db")
    return redirect(url_for('logoutall'))

#admin -> edit employee page
@app.route('/editemployee/<string:username>',methods=['POST','GET'])
def editemployee_page(username):
    if 'admin' in session:
        employees = db.view_employees()
        if request.method == 'GET':
            edit_value = db.get_employee_details_by_username(username)
            return render_template('employee/editemployee.html',employees=employees,error=None,edit_value=edit_value)
        if request.method == 'POST':
            fullname = request.form.get('fullname')
            password = request.form.get('password')
            mobile = request.form.get('mobile')
            address = request.form.get('address')
            if not (5 <= len(fullname) <= 40):
               return render_template('employee/addemployee.html',employees=employees,error="Enter Valid Full Name(5-40 characters)")
            if not (8 <= len(password) <= 20):
               return render_template('employee/addemployee.html',employees=employees,error="invalid password length (8-20 characters)")
            if not (len(mobile) == 10 and mobile.isdigit()):
               return render_template('employee/addemployee.html',employees=employees,error="Error due to invalid mobile number (10 numbers only)")
            if len(address) == 0:
               return render_template('employee/addemployee.html',employees=employees,error="Enter address please....")
            edit_employee = db.edit_employee_todb(username,fullname,password,mobile,address)
            if edit_employee:
                return redirect('/editemployee/')
            return render_template('employee/addemployee.html',employees=employees,error="Error in updating in db")
    return redirect(url_for('logoutall'))

#admin-> delete employee code
@app.route('/adeleteemployee/<string:username>')
def adeleteemployee(username):
    if 'admin' in session:
        db.delete_employee(username) 
        return redirect('/editemployee/')
    return redirect(url_for('logoutall'))

#admin,employee -> add,edit,delete customer
@app.route('/editcustomer/',methods=['POST','GET'])
def editcus():
    if 'employee' in session or 'admin' in session:
        customers = db.view_customers()
        if request.method == 'GET':
            return render_template('employee/addcustomer.html',customers=customers,error=None)
        if request.method == 'POST':
             username = request.form.get('username')
             fullname = request.form.get('fullname')
             password = request.form.get('password')
             mail = request.form.get('email')
             address = request.form.get('address')
             if not (8 <= len(username) <= 15):
                return render_template('employee/addcustomer.html',customers=customers,error="Username should be between 8 to 15 characters")
             if not (5 <= len(fullname) <= 40):
                return render_template('employee/addcustomer.html',customers=customers,error="Enter Valid Full Name(5-40 characters)")
             if not (8 <= len(password) <= 20):
                return render_template('employee/addcustomer.html',customers=customers,error="invalid password length (8-20 characters)")
             if not re.match(r'^[\w-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]+$', mail):
                return render_template('employee/addcustomer.html',customers=customers,error="Error due to invalid mail address")
             if len(address) == 0:
                return render_template('employee/addcustomer.html',customers=customers,error="Enter address please....")
             if db.check_customer_username(username):
                 return render_template('employee/addcustomer.html',customers=customers,error="username already exists")
             add_customer = db.customer_signup(username,fullname,password,mail,address,verify=1)
             if add_customer:
                 return redirect('/editcustomer/')
             return render_template('employee/addemployee.html',customers=customers,error="Error in updating in db")
    return redirect(url_for('logoutall'))

#admin,employee -> delete customer
# @app.route('/adeletecustomer/<string:username>')
# def adeletecustomer(username):
#     if 'admin' in session or 'employee' in session:
#         db.delete_customer(username) 
#         return redirect('/editcustomer/')
#     return redirect(url_for('logoutall'))

#admin,employee -> edit customer page
@app.route('/editcustomer/<string:username>',methods=['POST','GET'])
def editcustomer_page(username):
    if 'admin' in session or 'employee' in session:
        customers = db.view_customers()
        if request.method == 'GET':
            edit_value = db.get_customer_details_by_username(username)
            return render_template('employee/editcustomer.html',customers=customers,edit_value=edit_value,error=None)
        if request.method == 'POST':
            fullname = request.form.get('fullname')
            password = request.form.get('password')
            mail = request.form.get('email')
            address = request.form.get('address')
            if not (5 <= len(fullname) <= 40):
               return render_template('employee/addcustomer.html',customers=customers,error="Enter Valid Full Name(5-40 characters)")
            if not (8 <= len(password) <= 20):
               return render_template('employee/addcustomer.html',customers=customers,error="invalid password length (8-20 characters)")
            if not re.match(r'^[\w-]+@[a-zA-Z0-9]+\.[a-zA-Z0-9.]+$', mail):
                return render_template('employee/addcustomer.html',customers=customers,error="Error due to invalid mail address")
            if len(address) == 0:
               return render_template('employee/addcustomer.html',customers=customers,error="Enter address please....")
            edit_customer = db.edit_customer_todb(username,fullname,password,mail,address)
            if edit_customer:
                return redirect('/editcustomer/')
            return render_template('employee/addemployee.html',customers=customers,error="Error in updating in db")
    return redirect(url_for('logoutall'))

#admin,employee -> show unverified customers
@app.route('/verifycustomer/',methods=['POST','GET'])
def vercus():
    if 'admin' in session or 'employee' in session:
        vcustomers = db.unverify_customers_list()
        return render_template('employee/verifycus.html',customers=vcustomers)
    return redirect(url_for('logoutall'))

#admin,employee -> verify the unverified customers
@app.route('/verifycustomer/<string:username>',methods=['POST','GET'])
def vercus_by_username(username):
    if 'admin' in session or 'employee' in session:
        vcustomers = db.verify_otp(username)
        if vcustomers:
            return redirect('/verifycustomer/')
        return "<html><body><script>alert('Unble to verify customer')"
    return redirect(url_for('logoutall'))

#admin,employee -> delete unverified customer
@app.route('/deletecustomer/<string:username>')
def deletecustomer(username):
    if 'admin' in session or 'employee' in session:
        db.delete_customer(username) 
        return redirect('/verifycustomer/')
    return redirect(url_for('logoutall'))

#admin,employee -> add,edit products
@app.route('/addproduct/',methods=['GET','POST'])
def addproduct():
    if 'admin' in session or 'employee' in session:
        products = db.view_products()
        if request.method == 'GET':
            return render_template('employee/addproduct.html',products = products,error=None)
        brand = request.form.get('brand')
        category = request.form.get('category')
        availability = request.form.get('availability')
        quantity = request.form.get('quantity')
        rate_purchase = request.form.get('rate_purchase')
        rate_sales = request.form.get('rate_sales')
        if not all([brand, category, availability, quantity, rate_purchase, rate_sales]):
            return render_template('employee/addproduct.html',products = products,error='Please fill out all fields.')
        if not availability.isdigit() or not quantity.isdigit():
            return render_template('employee/addproduct.html',products = products,error='Availability and Quantity must be numbers.')
        add_product = db.add_product_todb(brand,category,availability,quantity,rate_purchase,rate_sales)
        if add_product:
            return redirect('/addproduct/')
        return "<html><head><script>alert('error in adding product')</script></head></html>"
    return redirect(url_for('logoutall'))

#admin,employee -> edit products page
@app.route('/addproduct/<string:productid>',methods=['GET','POST'])
def editproduct(productid):
    if 'admin' in session or 'employee' in session:
        products = db.view_products()
        if request.method == 'GET':
            edit_value = db.get_product_details_by_id(productid)
            return render_template('employee/editproduct.html',products = products,edit_value=edit_value,error=None) 
        brand = request.form.get('brand')
        category = request.form.get('category')
        availability = request.form.get('availability')
        quantity = request.form.get('quantity')
        rate_purchase = request.form.get('rate_purchase')
        rate_sales = request.form.get('rate_sales')
        if not all([brand, category, availability, quantity, rate_purchase, rate_sales]):
            return render_template('employee/addproduct.html',products = products,error='Please fill out all fields.')
        if not availability.isdigit() or not quantity.isdigit():
            return render_template('employee/addproduct.html',products = products,error='Availability and Quantity must be numbers.')
        edit_product = db.edit_product_todb(productid,brand,category,availability,quantity,rate_purchase,rate_sales)
        if edit_product:
            return redirect('/addproduct/')
        return "<html><head><script>alert('error in Editing product')</script></head></html>"
    return redirect(url_for('logoutall'))

#admin,employee -> add,edit supplier
@app.route('/addsupplier/',methods=['GET','POST'])
def addsupplier():
    if 'admin' in session or 'employee' in session:
        suppliers = db.view_suppliers()
        if request.method=='GET':
            return render_template('employee/addsupplier.html',suppliers = suppliers,error=None)
        supplier = request.form['supplier']
        mobile = request.form['mobile']
        address = request.form['address']
        # Check for empty fields
        if not supplier or not mobile or not address:
            return render_template('employee/addsupplier.html', suppliers=suppliers, error='Please fill in all fields.')
        # Check if mobile number is valid
        if not re.match(r'^[0-9]{10}$', mobile):
            return render_template('employee/addsupplier.html', suppliers=suppliers, error='Please enter a valid 10-digit mobile number.')
        if db.checksupplier_name(supplier):
            return render_template('employee/addsupplier.html', suppliers=suppliers, error='Supplier name already exists')
        add_supplier= db.add_product_todb(supplier,mobile,address)
        if add_supplier:
            return redirect('/addsupplier/')
        return render_template('employee/addsupplier.html',suppliers = suppliers,error="Error in adding database")
    return redirect(url_for('logoutall'))

#admin,employee -> add,edit supplier
@app.route('/addsupplier/<string:supplier>',methods=['GET','POST'])
def editsupplier(supplier):
    if 'admin' in session or 'employee' in session:
        suppliers = db.view_suppliers()
        edit_value = db.get_supplier_details_by_supplier(supplier)
        if request.method=='GET':
            return render_template('employee/editsupplier.html',suppliers = suppliers,edit_value=edit_value,error=None)
        mobile = request.form['mobile']
        address = request.form['address']
        # Check for empty fields
        if not supplier or not mobile or not address:
            return render_template('employee/addsupplier.html', suppliers=suppliers, error='Please fill in all fields.')
        # Check if mobile number is valid
        if not re.match(r'^[0-9]{10}$', mobile):
            return render_template('employee/addsupplier.html', suppliers=suppliers, error='Please enter a valid 10-digit mobile number.')
        update_supplier = db.edit_supplier_todb(supplier,mobile,address)
        if update_supplier:
            return redirect('/addsupplier/')
        return render_template('employee/addsupplier.html', suppliers=suppliers, error='Error in updating db....')
    return redirect(url_for('logoutall'))

#admin, employee -> purchase product for the shop
@app.route('/purchase/',methods=['POST','GET'])
def purchase():
    if 'admin' in session or 'employee' in session:
        suppliers=db.view_suppliers()
        products = db.view_products()
        if request.method == 'GET':
            return render_template('employee/addpurchase.html',suppliers = suppliers,products=products)
        product = request.form['product']
        supplier = request.form['supplier']
        if supplier == '' or product == '':
            return "please select any one option"
        return redirect(url_for('purchase2',product_id=int(product),supplier=supplier))
    return redirect(url_for('logoutall'))

#admin, employee -> purchase done
@app.route('/purchase/<int:product_id>/<string:supplier>',methods=['POST','GET'])
def purchase2(product_id,supplier):
    if 'admin' in session or 'employee' in session:
        product = db.get_product_details_by_id(product_id)
        if request.method =='GET':
            return render_template('employee/purchaseconfirm.html',supplier = supplier,product=product)
        total_product = request.form['total_product']
        if total_product == None:
            return render_template('/employee/purchase_verified.html',value='error')
        make_purchase = db.make_purchase_for_shop(product_id,supplier,product[3],total_product,(float(total_product)*float(product[5])))
        add_quantity = db.update_product_quantity_after_purchase(product_id,total_product)
        if make_purchase and add_quantity:
            return render_template('/employee/purchase_verified.html',value='success')
        return render_template('/employee/purchase_verified.html',value='error')
    return redirect(url_for('logoutall'))

#admin, employee -> add,sales for customer
@app.route('/salesemp/',methods=['POST','GET'])
def salebyemployee():
    if 'admin' in session or 'employee' in session:
        products= db.view_products()
        customers= db.view_customers()
        if request.method =='GET':
            return render_template('employee/addsales.html',products=products,customers=customers)
        product = request.form['product']
        customer = request.form['customer']
        if customer == '' or product == '':
            return "please select any one option"
        return redirect(url_for('salebyemployee2',product_id=int(product),username=customer))
    return redirect(url_for('logoutall'))

#admin, employee -> add,sales for customer page - 2
@app.route('/salesemp/<int:product_id>/<string:username>',methods=['POST','GET'])
def salebyemployee2(product_id,username):
    if 'admin' in session or 'employee' in session:
        product = db.get_product_details_by_id(product_id)
        if request.method =='GET':
            return render_template('employee/salesconfirm.html',customer = username,product=product)
        total_product = request.form['total_product']
        if total_product == None:
            return render_template('/employee/purchase_verified.html',value='error')
        check_availability = db.product_availability(product_id)
        if check_availability[0] < int(total_product):
            return "<html><body><script>alert('Entered value is greater than available quantity')</script></body></html>"
        order_add=db.add_order(username,product_id,int(total_product),(float(total_product) * float(check_availability[1])))
        if order_add:
            reduce_product = db.reduce_product(product_id,check_availability[0]-int(total_product))
            if reduce_product:
                return render_template('employee/purchase_verified.html',value='success')
        return render_template('employee/purchase_verified.html',value='error')
    return redirect(url_for('logoutall'))

#admin,employee -> billing page
@app.route('/billing/')
def billing():
    if 'admin' in session or 'employee' in session:
        billing = db.view_billing()
        return render_template('employee/billing.html',orders=billing)
    return redirect(url_for('logoutall'))

def download_pdf(product_brand,product_category,order_id,bill_id,mode_of_payment,total_amount,customer_name,quantity,bag):  
    rendered = render_template('employee/bill_generated.html',product_brand=product_brand,product_category=product_category,order_id=order_id,bill_id=bill_id,mode_of_payment=mode_of_payment,total_amount=total_amount,customer_name=customer_name,quantity=quantity,bag=bag)
    pdf = pdfkit.from_string(rendered,False,configuration=config)
    response = make_response(pdf)
    response.headers['content-Type'] = 'application/pdf'
    response.headers['content-Disposition'] = 'inline; filename= hello.pdf'
    return response

#admin,employee -> billing page - payment mode
@app.route('/billing/<int:order_id>/',methods=['GET','POST'])
def paymentmode(order_id):
    if 'admin' in session or 'employee' in session:
        if request.method =='GET':
            return render_template('employee/paymentmode.html',id=order_id)
        mode = request.form.get("mode")
        ros = db.get_rate_from_order(order_id)
        if db.update_mode_paid(order_id):
            generated = db.generate_bill_db(order_id,mode,ros[0])
            product_id = db.get_product_id_by_order_id(order_id) # 0=product_id 1 = username 2=quantity
            product_details = db.get_product_details_by_id_for_bill(product_id[0]) #0-brand 1-category 2-availability
            bill_details = db.get_bill_details_by_order_id(order_id) #0-bill id 1-mode 2-amount
            product_brand=product_details[0]
            product_category=product_details[1]
            bill_id = bill_details[0]
            mode_of_payment=bill_details[1]
            total_amount=bill_details[2]
            customer_name=product_id[1]
            quantity=product_id[2]
            bag=product_details[2]
            rendered = render_template('employee/bill_generated.html',product_brand=product_brand,product_category=product_category,order_id=order_id,bill_id=bill_id,mode_of_payment=mode_of_payment,total_amount=total_amount,customer_name=customer_name,quantity=quantity,bag=bag)
            pdf = pdfkit.from_string(rendered,False,configuration=config)
            response = make_response(pdf)
            response.headers['content-Type'] = 'application/pdf'
            response.headers['content-Disposition'] = 'inline; filename= hello.pdf'
            return response
    return redirect(url_for('logoutall'))

#admin,employee -> cancelorder
@app.route('/ecancelorder/<int:orderid>/<string:username>',methods=['GET','POST'])
def eordercancelling(orderid,username):
    if 'admin' in session or 'employee' in session:
        db.add_cancel_order_to_cancel_table(orderid,username)
        get_quantity = db.get_order_quantity_by_id(orderid)
        db.update_product_quantity_on_cancel(orderid,get_quantity[0])
        update = db.update_order_details_to_cancel(orderid)
        return redirect('/billing/')
    return redirect(url_for('logoutall'))

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)