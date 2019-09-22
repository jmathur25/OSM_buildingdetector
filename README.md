# OpenStreetMap Building Detector

![](demo.gif)
A demo in Champaign, IL

OpenStreetMap Building Detector was made to simplify and improve the mapping process on OpenStreetMap (https://www.openstreetmap.org/). At the moment, most OSM mappers do their work _by hand_. We built a Mask-RCNN, the current state of the art deep learning approach to object detection, to quickly detect buildings and improve mapping efficiency. With our platform, one can map a suburb in 10 minutes where previously it may have taken days if not weeks.

# Quick Start
It is recommended that you create a project environment to manage all the dependencies of this project. Anaconda is a good option if you are new to programming in Python / using environments.
To create the environment, run:
```
conda create -n ENV_NAME python=3.7 pip
```
Installing Dependencies:

```
conda activate ENV_NAME
pip install -r requirements.txt
```
Optionally, to make jupyter notebooks that run on the environment:
```
pip install ipykernel
ipython kernel install --user --name=ENV_NAME
```
Then, clone this repository onto your machine.

Finally, download the weights for the Mask-RCNN from here: https://drive.google.com/drive/folders/1IRCnYRwKLZUFQCZ8Imiy1_DUR8iFvoSB?usp=sharing <br>
Put these inside the _weights_ folder.

Run the following command and then navigate to http://127.0.0.1:5000/home/:
```
python application.py
```

# Usage
Press the down arrows button to sync with OSM and see what is already mapped.

Press the "M" button to use the Mask-RCNN. If you don't, you will use a very simple algorithm that does so-so at detecting buildings. After clicking "M", start clicking away! Feedback should be <0.5s. Note: the model runs on your local CPU, so the first time you use the Mask-RCNN you will have to wait a solid ~6s as the weights get loaded into memory. Afterwards, it should work instantly.

Press "DB" to activate delete mode. Click inside a building on the map, it will delete it. You can use this to clear bad finds by the model.

Press the up arrow button to upload your changes to the OSM server directly! Note: OSM servers can be slow, so this may take even up to 30 seconds. Note 2: this repository is currently configured to push to the dev server (https://master.apis.dev.openstreetmap.org/). To push to the real server, go into _config.yml_ and swap the API URLs.

In the top right, you will see two things.

1. A search bar. It's not... very... professional... but if you type in the name of cities (or even some towns) with proper spelling and capitalization, it will take you there. Examples: Chicago, London, Pleasanton

2. What I call the "window to the backend." This will show the "semantic segmentation masks" for every building the model detects. This is fancy talk for an image that clearly highlights where the object in question is. In this case, it shows where the model thinks the buildings are in a raw form. I wrote several image processing algorithms on top of the result you see, because OSM would much rather plot a rectangle (which is 99% if buildings) than a billion points that represent a mask. The result of those computations is rendered on your map as nice, neat rectangles.

## Some other cool features

Press "cntrl-z" to undo your last building.

# Technical Overview

This section will give a high level overview of the evolution of the project and its technical components. <br>

This project originally used more simple techniques for mapping. Inside of _Archive_, which I would not recommend opening unless you are REALLY curious, are a bunch of the old algorithms that we have since removed. Two worth mentioning:

1. _detectors/SimpleDetect.py_. Turns the image into grayscale and sends a vector in the horizontal and vertical directions. Stops when the brightness changes a preset amount. This is a very simple algorithm that captures rectanglar, non-rotated buildings pretty well.

2. _Archive/floodFillActual.py_. This is based on Photoshop's "magic wand" algorithm for filling odd shapes with one color. We adapted this algorithm to take a "seed click" and fill in the building to the best of its ability. It worked decently well and could handle rotated buildings, but some drawbacks included that it still didn't improve user efficiency enough (4 clicks -> 1 click is good but could be better), and it wasn't robustn(user click had too much power as it was the seed pixel).

We actually kept #1, and it is the default algorithm when you load up the web app and click the map. This is because it is fast, and we want you to consciously choose to load and use the Mask-RCNN.

Now, as for the Mask-RCNN, I used Matterport's implementation of the Mask-RCNN (Facebook AI initially created this in 2017). See here: https://github.com/matterport/Mask_RCNN. I trained the model using data from https://www.aicrowd.com/challenges/mapping-challenge using Google's Deep Learning VM. On epoch 55, I had a validation mAP of 0.81, which would place on 13th on crowdAI's challenge. These are the weights that I shared on the google link. It does remarkably well (mAP = 0.81 can be thought of as the object detection equivalent to 81%), but you'll notice it screws up a decent amount still. Quite remakrable how good the human eye is, huh?

After making the algorithm, I had to do a lot to turn it into something usable. <br>

First, I needed a "rectanglify" function that turns a collection of points into a minimum bounding rectangle. This is an interesting geometric challenge, and I solved it in _detectors/algorithms/Polygonify.py_ using a technique called Convex Hull. <br>

Second, I noticed that the Mask-RCNN would often detect a big mask and a smaller mask inside that big mask. I went with the assumption that the smaller mask was more likely to be accurate, so I wrote a function called _small_merge_ to do this quickly (another image computation challenge). I tried to combine all of this into a reusable, versatile class structure in _Mask_RCNN_Detect.py_. This class can be used to detect a single image (independent of the Flask server), or embedded deep into the Flask server. You can explore this class with _demo_detect.ipynb_ and _use_mrccn_class.ipynb_.

In addition to the core algorithm, there was a lot of software engineering kind of work to turn this into a full-fledges web-app. <br>

First was the development of the Flask server. If you want to learn more about it, navigate to _application.py_. Flask sets up the server side functions in a pretty neat way.

Second was writing the frontend for this. You can find all the JavaScript that supports this app in _templates/DisplayMap.html_. I'll admit it's not the cleanest, but all of the functionality (everything from rendering the map to rendering/tracking polygons to the buttons to the window to the backend to cntrl-z) is in there. We primarly used POST requests to communicate information between the frontend and backend.

Third was writing scripts to work with the OSM server. This included fetching existing buildings and pushing newly mapped buildings. Thankfully, OSM provides a nice pip package that made my life much easier. _backend/OSMAPI_Interactor.py_ contains that functionality.

Fourth came fetching imagery. The map that you see on the front end is in some ways different from the image that is used in the backend. I need to separately query the image from Mapbox and pass that to the model. _imagery.py_ contains those scripts.

Fifth was handling geo data. I needed quick ways to convert between geo data (this is important for mapping the results and for pushing to OSM) with regular image data (for building detection). _geolocation.py_ came in handy a lot here. I also had to keep track of buildings that were mapped, because if a user chooses to delete a building it needs to be deleted from the backend. Thankfully, Mapbox has done a lot of math into splitting the world into tiles. So, I stored buildings by grouping them into their tile and using a hashmap to store that grouping. That means that if a user clicked on the map, I simply computed the tile and then iterated through all the buildings in that tile to see if the click was inside of the building.

That wraps up a high-level description of the technical components that went into this project. It is kinda awesome to see all these parts come together into one finished product.


# Contact
You can reach me at jatinm2@illinois.edu

# Contributing
Please see our [contributor's guide](https://github.com/jmather625/OSM_buildingdetector/blob/master/CONTRIBUTING.md)
