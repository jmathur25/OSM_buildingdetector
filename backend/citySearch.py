import pandas as pd
# from perspective of app.py, where this function is called
# the dataframe is read at startup
df = pd.read_csv('data/cityLocation.csv')

def search_city(city_name):
    try:
        new = df[df['city_ascii'] == city_name]
        return float(new['lat']), float(new['lng'])
    except:
        return None

# print(search_city('Chicago'))

