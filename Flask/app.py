from flask import Flask, render_template, request, redirect

app = Flask(__name__)


@app.route('/readIn', methods = ['POST'])
def hello_world():
     result = request.form['address'] #reads in result from textbox
     render_template('Skeleton.html')
     return result



if __name__ == '__main__': #starting function, causes the website to launch
    app.run()
