
import yaml

def get_config():
    """Load the configuration file and return the dictionary containing
    the configuration."""
    
    try:
        with open("config.yml", "r") as conf_file:
            return yaml.load(conf_file)
    except:
        print("[ERROR] Could not parse the configuration file config.yml!")
    
    # Parse error
    return {}
