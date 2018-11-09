


""" from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/readIn', methods = ['POST'])
def hello_world():
     username = request.form['username']
     password = request.form['password']
     render_template('Login.html')
     return username, password



if __name__ == '__main__': #starting function, causes the website to launch
    app.run()
"""

from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/')
def Login():
     #username = request.form['username']
     #password = request.form['password']
     #render_template('Login.html')
     #print(username + " " + password)
     return render_template('Login.html')

@app.route('/NewAccount.html/')
def newAccount():
    return render_template('/NewAccount.html')

if __name__ == '__main__': #starting function, causes the website to launch
    app.run()
