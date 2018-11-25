from flask import Flask, render_template, request
app = Flask(__name__)

@app.route('/') #base page that loads up on start/accessing the website
def login():  #this method is called when the page starts up
   return render_template('login.html') #displays the relevant page

@app.route('/NewAccount.html') #activates when create a new account is clicked
def newAccount():
   return render_template('/NewAccount.html') #links to the create a new account page

@app.route('/test',methods = ['POST', 'GET'])   #this page is a test page to show if the information is saved
def result():
   if request.method == 'POST': # if the user hits the submit button. post is called
      result = request.form
      return render_template("test.html",result = result) #this links to the result page and dispalys the proper information

if __name__ == '__main__': #causes the program to boot
   app.run(debug = True)