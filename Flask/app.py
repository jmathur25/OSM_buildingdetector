from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/')
def Login():
     #username = request.form['username']
     #password = request.form['password']
     #render_template('Login.html')
     #print(username + " " + password)
     return render_template('Login.html')
Testusername = ""
Testpassword = ""
@app.route('/login', methods=['POST'])
def LoginPost():
    username = request.form['username']
    password = request.form['password']
    #Testpassword = password
    #Testusername = username
    print(username)
    print(password)
    return username, password

@app.route('/NewAccount.html/')
def newAccount():
    return render_template('/NewAccount.html')

@app.route('/signup', methods=['POST'])
def newAccountPost():
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    name = request.form['name']
    age = request.form['age']
    address = request.form['address']
    return username, password, email, name, age, address

@app.route('/Retrieval.html/')
def retrival():
    username, password = LoginPost()
    print(username, password)
    return render_template('/Retrieval.html', username=username, password=password)

if __name__ == '__main__': #starting function, causes the website to launch
    app.run()
