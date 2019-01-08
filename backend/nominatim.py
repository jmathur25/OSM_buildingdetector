import requests

def query_location(query):
    """
    Send a query for reverse geocoding to Nominatim.
    @param query Query to search, such as "Illinois" or "Six Flags Great America"
    @return The JSON object containing Nominatim's results for that search term,
        or None if the request was unsuccessful.
    """
    nom_url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query,
        "format": "jsonv2",
        "accept-language": "en-US"
    }
    
    headers = {
        "User-Agent": "OSM Building Detector v1.0"
    }
    
    r = requests.get(nom_url, params=params, headers=headers)
    
    if r.status_code == requests.codes.ok:
        return r.json()
    else:
        None
    
