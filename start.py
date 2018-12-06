import config_reader

# Read the config
config = config_reader.get_config()

if "imageryURL" not in config:
    print("[ERROR] Could not find imageryURL in the config file!")

# Get the imagery URL and access key
imagery_url = config["imageryURL"]
access_key = ""

if "accessKey" in config:
    access_key = config["accessKey"]
    
# Start Flask
#import app