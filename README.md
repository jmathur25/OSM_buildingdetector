# OpenStreetMap Building Detector

OpenStreetMap Building Detector is a Python desktop/web app that uses aerial imagery to help the user map buildings quickly to OpenStreetMap (OSM).

Where there are not as many OSM mappers adding details to their area, adding items to the map can become an enormous task. Most OSM mappers do their work _by hand_—clicking each corner of every building—with aerial imagery in the background to guide them. Buildings are a very necessary component to maps, and with buildings in place, OSM mappers can add POIs with greater ease.

In rural areas (and even suburban areas) the buildings, especially houses, aren’t there.

# Requirements
OSM API for interacting with the online database:
```pip install osmapi

For the local database:
```pip install dataset

# Usage
Simply clone the repo and run _start.py_ to start the Flask server. Navigate to localhost:5000 in a web browser to begin mapping.