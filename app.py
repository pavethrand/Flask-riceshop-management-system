#import required libraries
from flask import Flask,render_template,request,url_for,redirect

#import database file
from db import RiceDatabase

#create app
app = Flask(__name__)

#create db connection
db = RiceDatabase()
db.connect()

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
        return render_template('customer/dashboard.html',username = user)
    return render_template('customer/login.html',error=True)

#employee login
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

#customersignup
@app.route('/signup/',methods=['POST','GET'])
def cussignup():
    return render_template('customer/signup.html')


#otp verification customer
@app.route('/otp/',methods=['GET','POST'])
def verityotp():
    return render_template('customer/otp.html')

#admin -> edit employee
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

@app.route('/ordercus/',methods=['GET','POST'])
def ordercus():
    products= db.view_products()
    return render_template('customer/makeorder.html',products=products)

@app.route('/ordercus2/',methods=['GET','POST'])
def ordercus2():
    products= db.view_products()
    return render_template('customer/makeorder2.html',products=products)

@app.route('/ordercancel/',methods=['GET','POST'])
def ordercancel():
    products= db.view_products()
    return render_template('customer/order_cancel.html',products=products)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)