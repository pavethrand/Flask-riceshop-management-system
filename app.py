from flask import Flask,render_template,request,url_for
from db import RiceDatabase

app = Flask(__name__)

db = RiceDatabase()
db.connect()

@app.route('/')
def home():
    return render_template('index.html')

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

@app.route('/loginemp/',methods=['POST','GET'])
def loginemp():
    if request.method == 'GET':
        return render_template('employee/login.html')
    return render_template('employee/dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)