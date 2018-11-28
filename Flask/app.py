import sys
sys.path.append('../')
import backend

# need the following syntax to call classes from another file
# x = backend.Users.User("Jatin", "jmather", "jatinm2@illinois.edu", "fakepassword", 18, "Champaign, IL")
# print(x)

# need the following syntax to call functions from another file
# backend.init_backend() <- from backend.py
# since there is no function overlap there should be no problem

# to call functions
# backend.create_user(info)
# to see the changes
backend.show_database()
# to clear the database
# backend.clear_database()

from flask import Flask, render_template, request, flash

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
        error = ""
        result = request.form
        # changes result into a dict, currently is an immutable multi dict
        info = {}
        for k, v in result.items():
            info[k.lower()] = v
        # passes to backend
        """
        string1 = result["username"]
        string2 = result["password"]
        info["string1"] = string2   
        """
        #that should add to the list, where it has the username and password on file
        # verification can be done by calling the username key and comparing the inputted password to the actual
        # if it hasn't been done already
        status = backend.create_user(info)
        if status: # true condition
            error = "account created"
            flash(error) # new stuff I added
            #return render_template("test.html",result = result) <-- have it redirect to the actual service once connected
            #  #this links to the result page and dispalys the proper information
        else: # false condition
            error = "account already exists"
            flash(error) # new stuff I added
            #return render_template("test.html", result=result) <-- no longer in use
            # this links to the result page and dispalys the proper informatio


if __name__ == '__main__': #causes the program to boot
   app.run(debug=True)
