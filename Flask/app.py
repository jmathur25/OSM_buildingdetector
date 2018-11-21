from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/')
def login():
   return render_template('login.html')

@app.route('/NewAccount.html')
def newAccount():
   return render_template('/NewAccount.html')

@app.route('/test',methods = ['POST', 'GET'])
def result():
   if request.method == 'POST':
      result = request.form
      return render_template("test.html",result = result)

if __name__ == '__main__':
   app.run(debug = True)