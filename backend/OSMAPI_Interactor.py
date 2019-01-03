# based on https://pypi.org/project/osmapi/ and http://osmapi.metaodi.ch/#header-classes
# not a built-in library
import osmapi


def sign_in(web_api, username, password):
    osm_api = osmapi.OsmApi(api=web_api, username=username, password=password)
    return osm_api


# tag must be as a dict, like {"Corner": "1"}
def node_create(osm_api, latitude, longitude, comment, tag = {}):
    node = osm_api.NodeCreate({"lat": latitude, "lon": longitude, "tag": tag})
    return node


# tag must be as a dict, like {"Way": "new way!"}
# default is empty tag
def way_create(osm_api, node_list, comment, tag = {}):
    osm_api.ChangesetCreate({u"comment": comment})

    node_id_list = []
    for node in node_list:
        node_id_list.append(node["id"])

    way = osm_api.WayCreate({"nd": node_id_list, "tag": tag})

    # close set of changes
    osm_api.ChangesetClose()
    return way


# Create a changeset with multiple ways (multiple buildings)
def way_create_multiple(osm_api, all_rects_dict, comment, tag={"building": "yes"}):
    # Create the changeset
    osm_api.ChangesetCreate({u"comment": comment})
    
    way_list = []
    
    # Create each way
    for rect in all_rects_dict.values():
        node_list = []
        
        for coordinates in rect:
            lat = coordinates[0]
            long = coordinates[1]
            node = node_create(osm_api, lat, long, "")
            node_list.append(node["id"])
        
        # If there are at least three nodes, create the area
        if len(node_list) >= 3:
            node_list.append(node_list[0])
            this_way = osm_api.WayCreate({"nd": node_list, "tag": tag})
            way_list.append(this_way)
    
    # Close the changeset
    osm_api.ChangesetClose()
    return way_list


def find_way(osm_api, way):
    # see data on the way you just made
    return osm_api.WayGet(str(way["id"]))


def see_map(osm_api, min_lon, min_lat, max_lon, max_lat):
    # FORMAT: min lon, min lat, max lon, max lat
    # returns a dictionary of the form [{'type': (one of node, way, changeset), 'data': dict}, ...]
    # print(api.Map(-94.532408, 45.127431, -94.531071, 45.128568))
    return api.Map(min_lon, min_lat, max_lon, max_lat)


def parse_map(map_info):
    # parses map, returns coordinates of buildings with each building an item of the return list
    node_list_ids = []
    render_buildings = []
    for info in map_info:
        if info['type'] == 'way':
            node_list_ids.append(info['data']['nd'])
    for node_list in node_list_ids:
        way_coordinates = []
        for info in map_info:
            if info['type'] == 'node':
                if info['data']['id'] in node_list:
                    way_coordinates.append((info['data']['lat'], info['data']['lon']))
        render_buildings.append(way_coordinates)
    return render_buildings


api = sign_in('https://api06.dev.openstreetmap.org', 'OSM_buildingdetector', 'fakepassword123')
map_info = see_map(api, -94.532408, 45.127431, -94.531071, 45.128568)
parse_map(map_info)
