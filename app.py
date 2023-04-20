#import required libraries
from flask import Flask,render_template,request,url_for,redirect
import re

#import database file
from db import RiceDatabase

#import OTP class
from otp import OTPGenerator

#create app
app = Flask(__name__)

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
        return render_template('customer/login.html',error=False)
    user = request.form['username']
    password = request.form['password']
    res = db.check_login('customer',user,password)
    if res == True:
        res_unverified,mobile=db.verify_cus(user)
        if res_unverified:
            return redirect(url_for('verifyotp',number=mobile,user=user))
        return render_template('customer/dashboard.html',username = user)
    return render_template('customer/login.html',error=True)

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
        return redirect(url_for('verifyotp',number=str(mobile),user=username))
    print(values_upload)
    return render_template('customer/signup.html',message='Error in Signup.....',list=list)

#customer->OTP Validation
@app.route('/otp/<string:number>/<string:user>',methods=['GET','POST'])
def verifyotp(number,user):
    global generated_otp
    if request.method == 'GET':
        generated_otp=otp.generate_otp()
        return render_template('customer/otp.html',number=number,user=user)
    user_otp = request.form['otp1']
    user_otp = user_otp + request.form['otp2']
    user_otp = user_otp + request.form['otp3']
    user_otp = user_otp + request.form['otp4']
    if user_otp == generated_otp:
        generated_otp = None
        updated = db.verify_otp(user)
        if updated > 0:
            return render_template('/customer/otp_verified.html', value="success")
        return render_template('/customer/otp_verified.html', value="db_error")
    return render_template('/customer/otp_verified.html', value="otp_error")

#customer->make order
@app.route('/makeorderbycustomer/',methods=['GET','POST'])
def makeorderbycustomer():
    dropdown_values = db.view_products_category()
    if request.method == 'GET': 
        return render_template('customer/orderpage.html',category=dropdown_values,selected=None)
    selected_category = request.form.get('product')
    if selected_category == 'null':
        return render_template('customer/orderpage.html',category=dropdown_values,selected=None)
    selected = db.view_products_selected(selected_category)
    return render_template('customer/orderpage.html',category=dropdown_values,selected=selected)
    
#customer-> place order
#need to change after setting session
@app.route('/placeorder/<int:prt_id>')
def place_order(prt_id):
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