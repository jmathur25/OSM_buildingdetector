# OpenStreetMap Building Detector

OpenStreetMap Building Detector is a Python desktop/web app that uses aerial imagery to help the user map buildings quickly to OpenStreetMap (OSM).

Where there are not as many OSM mappers adding details to their area, adding items to the map can become an enormous task. Most OSM mappers do their work _by hand_—clicking each corner of every building—with aerial imagery in the background to guide them. Buildings are a very necessary component to maps, and with buildings in place, OSM mappers can add POIs with greater ease.

In rural areas (and even suburban areas) the buildings, especially houses, aren’t there.

# Requirements
OpenStreetMap Building Detector requires some extra packages to run. Install the following packages before running the start.py script.

OSM API for interacting with the online database:
```pip install osmapi```

For the local database:
```pip install dataset```

OpenCV for building detection:
```pip install opencv-python```

# Usage
Simply clone the repo and run _start.py_ to start the Flask server. Navigate to localhost:5000 in a web browser to begin mapping.

Click on a building on the map. This will generate a rectangle around the clicked point to represent the outline of the building.

Sometimes the rectangle detected is slightly inaccurate. When this happens, press "Ctrl z" on your keyboard to undo the last added rectangle. Click at a slightly different point on the same building to generate another rectangle.

Press the "Submit" button to upload all of the building outlines on your map to the OpenStreetMap server.

Press the "Merge" button or press "m" to toggle Merge Mode. When Merge Mode is turned on, new buidling outlines that are generated will try to merge with nearby building outlines. This should be used to outline buildings with a lot of noise in the image, or buidlings with roofs that contain different colors/gradients.
