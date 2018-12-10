import config_reader
import imagery

# Read the config
config = config_reader.get_config()

if "imageryURL" not in config:
    print("[ERROR] Could not find imageryURL in the config file!")

# Get the imagery URL and access key
imagery_url = config["imageryURL"]
access_key = ""

if "accessKey" in config:
    access_key = config["accessKey"]

# Create imagery downloader
imd = imagery.ImageryDownloader(imagery_url, access_key)
    
# Start Flask
import app
app.start_webapp(imd)