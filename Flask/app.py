from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/readIn', methods = ['POST'])
def hello_world():
     result = request.form['search'] #reads in result from textbox
     return render_template('Skeleton.html')
"""
change return value to send result of the input box to openCV
"""


if __name__ == '__main__': #starting function, causes the website to launch
    app.run()
