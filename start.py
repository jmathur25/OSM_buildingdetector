import config_reader
import imagery

# Read the config
config = config_reader.get_config()
    
# Start Flask
import app
app.start_webapp(config)