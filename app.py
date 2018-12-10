import backend
import imagery
import os
import BuildingDetectionFromClick as bdfc
import geolocation
import PIL.ImageOps
import cv2
import numpy
import json

from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, send_file

app = Flask(__name__)

imd = None


def result_to_dict(result):
    info = {}
    for k, v in result.items():
        info[k.lower()] = v
    return info


@app.route('/', methods=['POST', 'GET'])  # base page that loads up on start/accessing the website
def login():  # this method is called when the page starts up
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


@app.route('/home/')
def home():
    # x = send_from_directory("../templates/", "DisplayMap.html", as_attachment=True)
    # print(x)
    # return send_from_directory('./../templates/', 'DisplayMap.html')
    return render_template('DisplayMap.html')


@app.route('/home/mapclick', methods=['POST'])
def mapclick():
    if request.method == 'POST':
        result = request.form
        info = result_to_dict(result)

        lat = float(info['lat'])
        long = float(info['long'])
        zoom = int(info['zoom'])

        # find xtile, ytile
        xtile, ytile = geolocation.deg_to_tile(lat, long, zoom)

        # find x, y
        x, y = geolocation.deg_to_tilexy(lat, long, zoom)

        # Get those tiles
        backend_image = imd.get_tiles_around(xtile, ytile, zoom)
        backend_image.show()
        backend_image = PIL.ImageOps.grayscale(backend_image)
        backend_image.show()

        # create a rectangle from click
        # rect_data includes a tuple -> (list of rectangle references to add/draw, list of rectangle ids to remove)
        rect_data = bdfc.get_rectangle_from_image_lat_long(numpy.array(backend_image), lat, long, zoom)
        print(rect_data)
        
        rect_to_add = rect_data[0][0]
        rect_points = rect_to_add.get_points()  # a list of [lat, long]  # TODO check if the rectangle lat/long internal conversions are correct
        rect_id = rect_to_add.get_id()
        
        print("")
        print("Adding Rectangle id #{}; lat/long points are:\n{}".format(rect_id, rect_points))
        # TODO draw polygon stuff
        rectangles_id_to_remove = rect_data[1]
        for rect_id in rectangles_id_to_remove:
            print("Removing Rectangle id #{}:".format(rect_id))
            # TODO remove polygon of id rect_id
            print(rect_id)

        json_post = {"rectsToAdd": [{"id": rect_id,
                                    "points": rect_points}],
                     "rectsToDelete": [{"ids": rectangles_id_to_remove}]
                            }

        return json.dumps(json_post)


@app.route('/NewAccount/', methods=['GET', 'POST'])  # activates when create a new account is clicked
def new_account():
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

    return render_template('/NewAccount.html', error=error)  # links to the create a new account page


@app.route('/home/imagery/<zoom>/<x>/<y>.png', methods=['GET'])
def imagery_request(zoom, x, y):
    fname = imd.get_tile_filename(x, y, zoom)
    if not os.path.isfile(fname):
        imd.download_tile(x, y, zoom)
    return send_file(fname, mimetype="image/png")


def start_webapp(imagery_downloader):
    """Starts the Flask server."""
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    global imd
    imd = imagery_downloader

    app.debug = True
    app.run()
