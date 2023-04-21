#import required libraries
from flask import Flask,render_template,request,url_for,redirect,session
import re

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
        if 'unverified' in session:
            session.pop('unverified', None)
        return render_template('customer/login.html',error=False)
    user = request.form['username']
    password = request.form['password']
    res = db.check_login('customer',user,password)
    if res == True:
        res_unverified,mobile=db.verify_cus(user)
        if res_unverified:
            return redirect(url_for('verifyotp',number=mobile,user=user))
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
    mobile = request.form['mobile']
    address = request.form['address']
    list = [username,fullname,password,confirm_password,mobile,address]
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
    elif bool(re.match('^[0-9]{10}$',mobile)) == False:
        list[4]=''
        return render_template('customer/signup.html',message='Enter Correct Mobile Number',list=list)
    values_upload = db.customer_signup(username,fullname,password,mobile,address,verify=0)
    if values_upload > 0:
        #set session to signup
        session['unverified'] = username
        return redirect(url_for('verifyotp',number=str(mobile),user=session['unverified']))
    return render_template('customer/signup.html',message='Error in Signup.....',list=list)

#customer->OTP Validation
@app.route('/otp/<string:number>/<string:user>',methods=['GET','POST'])
def verifyotp(number,user):
    global generated_otp
    if request.method == 'GET':
        if session.get('unverified') == user:
            generated_otp=otp.generate_otp()
            return render_template('customer/otp.html',number=number,user=user)
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

#customer -> logout
#add admin,employee at last
@app.route('/logout/',methods=['GET','POST'])
def logoutall():
    if 'customer' in session:
        session.pop('customer', None)
        return redirect(url_for('logincus',error=False))
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
    print(total_product)
    check_availability = db.product_availability(product_id)
    if check_availability[0] < int(total_product):
        return "<html><body><script>alert('Entered value is greater than available quantity')</script></body></html>"
    order_add=db.add_order(session['customer'],product_id,int(total_product),(float(total_product) * float(check_availability[1])))
    if order_add:
        reduce_product = db.reduce_product(product_id,check_availability[0]-int(total_product))
        if reduce_product:
            return render_template('customer/orderdone.html',value='success')
    return render_template('customer/orderdone.html',value='error')

@app.route('/cordercancel/',methods=['GET','POST'])
def cordercancel():
    if 'customer' not in session:
        return redirect(url_for('logoutall'))
    placed_orders=db.product_fetch_for_cancel(session['customer'])
    return render_template('customer/ordercancel.html',orders=placed_orders)

@app.route('/cordercancel/<int:orderid>/',methods=['GET','POST'])
def ordercancelling(orderid):
    if 'customer' not in session:
        return redirect(url_for('logoutall'))
    return "done"





@app.route('/loginemp/',methods=['POST','GET'])
def loginemp():
    if request.method == 'GET':
        return render_template('employee/login.html',error=False)

    user = request.form['username']
    password = request.form['password']
    if user == 'admin' and password == 'admin':
        return render_template('admin/dashboard.html')
    res = db.check_login('employee',user,password)
    if res == True:
        return render_template('employee/dashboard.html',username = user)
    return render_template('employee/login.html',error=True)

@app.route('/editemployee/',methods=['POST','GET'])
def editemp():
    employees = db.view_employees()
    return render_template('admin/editemployee.html',employees=employees)

@app.route('/editcustomer/',methods=['POST','GET'])
def editcus():
    customers = db.view_customers()
    return render_template('employee/editcustomer.html',customers=customers)

@app.route('/verifycustomer/',methods=['POST','GET'])
def vercus():
    vcustomers = db.unverify_customers_list()
    return render_template('employee/verifycus.html',customers=vcustomers)

@app.route('/addproduct/')
def addproduct():
    products = db.view_products()
    return render_template('employee/addproduct.html',products = products)

@app.route('/addsupplier/')
def addsupplier():
    suppliers = db.view_suppliers()
    return render_template('employee/addsupplier.html',suppliers = suppliers)

@app.route('/purchase/',methods=['POST','GET'])
def purchase():
    suppliers=db.view_suppliers()
    products = db.view_products()
    return render_template('employee/purchase.html',suppliers = suppliers,products=products,page=1)

@app.route('/purchase/2',methods=['POST','GET'])
def purchase2():
    suppliers=db.view_suppliers()
    products = db.view_products()
    return render_template('employee/purchase.html',suppliers = suppliers,products=products,page=2)

@app.route('/purchase/3',methods=['POST','GET'])
def purchase3():
    suppliers=db.view_suppliers()
    products = db.view_products()
    return render_template('employee/purchase.html',suppliers = suppliers,products=products,page=3)

@app.route('/billing/')
def billing():
    billing = db.view_billing()
    return render_template('employee/billing.html',orders=billing)

@app.route('/salesemp/')
def salebyemployee():
    products= db.view_products()
    customers= db.view_customers()
    return render_template('employee/sales_customer.html',products=products,customers=customers)

@app.route('/salesemp2/',methods=['GET','POST'])
def salebyemployee2():
    products= db.view_products()
    customers= db.view_customers()
    return render_template('employee/sales_customer2.html',products=products,customers=customers)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)