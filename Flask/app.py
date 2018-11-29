import sys
sys.path.append('../')
import backend

from flask import Flask, render_template, request, flash, redirect, url_for
app = Flask(__name__)


def result_to_dict(result):
    info = {}
    for k, v in result.items():
        info[k.lower()] = v
    return info


@app.route('/', methods=['POST', 'GET']) #base page that loads up on start/accessing the website
def login():  #this method is called when the page starts up
    error = None
    if request.method == 'POST':
        result = request.form
        info = result_to_dict(result)
        status = backend.user_sign_in(info)
        if status:
            flash('You successfully made a new account')
            return redirect(url_for("home"))
        else:
            error = "Account does not exist"

    return render_template('Login.html', error=error)


@app.route('/home')
def home():
    return render_template('Skeleton.html')


@app.route('/NewAccount/', methods=['POST', 'GET']) #activates when create a new account is clicked
def newAccount():
    error = None
    if request.method == 'POST':  # if the user hits the submit button. post is called
        result = request.form
        info = result_to_dict(result)
        status = backend.create_user(info)
        if status:  # true condition
            flash('You successfully made a new account')
            return redirect(url_for('home'))
        else:  # false condition
            error = "account already exists"

        return redirect(url_for('login'))

    return render_template('/NewAccount.html', error=error) #links to the create a new account page


if __name__ == '__main__': #causes the program to boot
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = True
    app.run()
