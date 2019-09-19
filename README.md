# OpenStreetMap Building Detector

![](osm_demo_initial.gif)

OpenStreetMap Building Detector is a Python desktop/web app that uses aerial imagery to help the user map buildings quickly to OpenStreetMap (OSM).

Where there are not as many OSM mappers adding details to their area, adding items to the map can become an enormous task. Most OSM mappers do their work _by hand_—clicking each corner of every building—with aerial imagery in the background to guide them. Buildings are a very necessary component to maps, and with buildings in place, OSM mappers can add POIs with greater ease.

In rural areas (and even suburban areas) the buildings, especially houses, aren’t there.


# Quick Start
It is recommended you create a project environment first. <br>
Environment:
```
conda create -n ENV_NAME python=3.7 pip
```
Dependencies:

```
pip install -r requirements.txt
```
Optionally, to make jupyter notebooks that run on the environment:
```
pip install ipykernel
ipython kernel install --user --name=ENV_NAME
```
Then, clone the repository onto your machine.

Finally, download the weights for the Mask-RCNN from here: https://drive.google.com/drive/folders/1IRCnYRwKLZUFQCZ8Imiy1_DUR8iFvoSB?usp=sharing <br>
Put these inside the _weights_ folder.

Run the following command and then navigate to http://127.0.0.1:5000/home/:
```
python application.py
```


# Usage
Simply clone the repo and run _start.py_ to start the Flask server. Navigate to localhost:5000 in a web browser to begin mapping.

Press the "Sync" button to sync with the currently mapped buildings on the OSM server - this must be done in order to add buildings.

Click on a building on the map. This will generate a rectangle around the clicked point to represent the outline of the building.

Sometimes the rectangle detected is slightly inaccurate. When this happens, press "Ctrl z" on your keyboard to undo the last added rectangle. Click at a slightly different point on the same building to generate another rectangle.

Press the "Submit" button to upload all of the building outlines on your map to the OpenStreetMap server.

Press the "Merge" button or press "m" to toggle Merge Mode. When Merge Mode is turned on, new buidling outlines that are generated will try to merge with nearby building outlines. This should be used to outline buildings with a lot of noise in the image, or buidlings with roofs that contain different colors/gradients.

Press the "C" button to toggle between Simple and Complex mode. Simple mode is best used for standard-oriented rectangular buildings, complex mode should be used for any rotated buildings or irregular geometry.
# Contributing
Please see our [contributor's guide](https://github.com/jmather625/OSM_buildingdetector/blob/master/CONTRIBUTING.md)
