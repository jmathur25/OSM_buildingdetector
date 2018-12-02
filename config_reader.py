
import yaml

def get_config():
    """Load the configuration file and return the dictionary containing
    the configuration."""
    
    with open("config.yml", "r") as conf_file:
        try:
            return yaml.load(conf_file)
        except yaml.YAMLError as exception:
            print(exception)
    
    # Parse error
    return {}
