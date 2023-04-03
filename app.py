from flask import Flask,render_template,request

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logincus/',methods=['POST','GET'])
def logincus():
    if request.method == 'GET':
        return render_template('customer/login.html')
    return render_template('customer/dashboard.html')

@app.route('/loginemp/',methods=['POST','GET'])
def loginemp():
    if request.method == 'GET':
        return render_template('employee/login.html')
    return render_template('employee/dashboard.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)