# based on https://pypi.org/project/osmapi/ and http://osmapi.metaodi.ch/#header-classes
# not a built-in library in Pycharm
import osmapi
import math
import operator


class OSM_Interactor:
    # a little bit of research suggested this number might be a good one
    AREA_THRESHOLD = 0.000001
    # a little bit of research suggested this number might be a good one
    SUM_THRESHOLD = 0.1

    def __init__(self, web_api, username, password):
        osm_api = osmapi.OsmApi(api=web_api, username=username, password=password)
        self.osm_api = osm_api
        # variable to keep track of buildings synced
        self.ways_added = {}

    # ideally not used as signing is taking care of during __init__
    # could be used in a feature where the user can change the access token while mapping
    def sign_in(self, web_api, username, password):
        osm_api = osmapi.OsmApi(api=web_api, username=username, password=password)
        self.osm_api = osm_api
        return osm_api

    # tag must be as a dict, like {"Corner": "1"}
    def node_create(self, latitude, longitude, comment, tag={}):
        node = self.osm_api.NodeCreate({"lat": latitude, "lon": longitude, "tag": tag})
        return node

    # tag must be as a dict, like {"Way": "new way!"}
    # default is empty tag
    def way_create(self, node_list, comment, tag={}):
        self.osm_api.ChangesetCreate({u"comment": comment})
        node_id_list = []
        for node in node_list:
            node_id_list.append(node["id"])
        way = self.osm_api.WayCreate({"nd": node_id_list, "tag": tag})
        # close set of changes
        self.osm_api.ChangesetClose()
        return way

    # Create a changeset with multiple ways (multiple buildings)
    def way_create_multiple(self, all_rects_dict, comment, tag={"building": "yes"}):
        # Create the changeset
        self.osm_api.ChangesetCreate({u"comment": comment})
        way_list = []
        # Create each way
        for rect in all_rects_dict.values():
            node_list = []

            for coordinates in rect:
                lat = coordinates[0]
                long = coordinates[1]
                node = self.node_create(lat, long, "")
                node_list.append(node["id"])

            # If there are at least three nodes, create the area
            if len(node_list) >= 3:
                node_list.append(node_list[0])
                this_way = self.osm_api.WayCreate({"nd": node_list, "tag": tag})
                way_list.append(this_way)

        # Close the changeset
        self.osm_api.ChangesetClose()
        return way_list

    def find_way(self, way_id):
        # see data on the way given way id
        return self.osm_api.WayGet(way_id)

    def find_node(self, node_id):
        # see data on the way given way id
        return self.osm_api.NodeGet(node_id)

    def sync_map(self, min_lon, min_lat, max_lon, max_lat):

        """
        FIRST FUNCTION LOOKS AT MAP AND RETURNS A DICTIONARY OF INFO ON NODES AND WAYS
        SECOND FUNCTION LOOKS AT INFO AND PARSES TO GET A 2D LIST OF BUILDINGS TO SYNC
        """

        def see_map(self, min_lon, min_lat, max_lon, max_lat):
            # FORMAT: min lon, min lat, max lon, max lat
            # returns a dictionary of the form [{'type': (one of node, way, changeset), 'data': dict}, ...]
            # print(api.Map(-94.532408, 45.127431, -94.531071, 45.128568))
            return self.osm_api.Map(min_lon, min_lat, max_lon, max_lat)

        def parse_map(self, map_info):
            # parses map, returns coordinates of buildings with each building an item of the return list
            # stores a tuple in each index, where the first item is the list of node ids and the second is the way id
            node_list_ids = []
            # ultimately passed to frontend, as a 2D list with each index being a list containing 4 (lat, long) coordinates
            render_buildings = []

            # reduces runtime by remembering elements of map_info that are nodes in initial parsing
            map_node_info = []
            for info in map_info:
                if info['type'] == 'way':
                    if info['data']['id'] not in self.ways_added:
                        node_list_ids.append((info['data']['nd'], info['data']['id']))
                else:
                    if info['type'] == 'node':
                        map_node_info.append(info)
            for node_list, way_id in node_list_ids:
                # OpenStreetMap has this incredibly weird thing where info['data']['id'] only seems to have 4 unique nodes
                # if there are any more spots, they are just repeats. Checkout changeset # 140834 online and use find_way
                # on way 4305299393 to see the difference. As far as I can tell, all node_lists over length 4 have length 5,
                # with the last node being the first one repeated
                # temporary solution caps way_coordinates at 4
                way_coordinates = [0, 0, 0, 0]
                for info in map_node_info:
                    if info['type'] == 'node':
                        if info['data']['id'] in node_list:
                            index = node_list.index(info['data']['id']) % 4
                            way_coordinates[index] = (info['data']['lat'], info['data']['lon'])
                            if 0 not in way_coordinates:
                                break
                # the method above should make sure way is already sorted
                if not OSM_Interactor.check_area(way_coordinates, sort=False):
                    lats = [p[0] for p in way_coordinates]
                    longs = [p[1] for p in way_coordinates]
                    # makes ways_added keep track of the center of the building
                    center_lat = sum(lats) / len(way_coordinates)
                    center_long = sum(longs) / len(way_coordinates)
                    self.ways_added[way_id] = (center_lat + center_long, way_coordinates)
                    render_buildings.append(way_coordinates)
            return render_buildings

        return parse_map(self, see_map(self, min_lon, min_lat, max_lon, max_lat))

    # True if the area is too big
    # uses area
    @staticmethod
    def check_area(points, sort=False):
        if sort:
            points = sort_points(points)
        if area_from_points(points) > OSM_Interactor.AREA_THRESHOLD:
            return True
        return False

    # allows server to clear ways_added if necessary
    def clear_ways_memory(self):
        self.ways_added = {}

    def get_ways_memory(self):
        return self.ways_added

    def sort_ways_memory(self):
        return sorted(self.ways_added.items(), key=operator.itemgetter(1))


    def ways_binary_search(self, coordinate):
        recursion_memory = {}
        index_matches = []
        def binary_recursion(current, old, search_val, sorted_ways):
            if current in recursion_memory:
                return 'done'
            if current >= len(sorted_ways):
                current = len(sorted_ways) - 1
            if current <= -1:
                current = 0
            recursion_memory[current] = 1
            diff = sorted_ways[current][1][0] - search_val
            if abs(diff) <= OSM_Interactor.SUM_THRESHOLD:
                index_matches.append(current)
            if diff > 0:
                new = current - math.ceil(abs(current - old) / 2)
            else:
                new = current + math.ceil(abs(current - old) / 2)
            old = current
            binary_recursion(new, old, search_val, sorted_ways)

        # this function uses sort_ways_memory and binary_recursion to find a small list of ways that are close to the poiint
        sorted_ways = self.sort_ways_memory()
        root_index = len(sorted_ways) // 2
        search_val = sum(coordinate)
        binary_recursion(root_index, 0, search_val, sorted_ways)
        possible_matches = [sorted_ways[i][1][1] for i in range(min(index_matches), max(index_matches) + 1)]
        return possible_matches


# Uses shoelace to find the area given SORTED lat, long coordinates of ANY polygon
# points in the form [(lat1, long1), (lat2, long2), ...]
# duplicate code right now, BuildingDetectionFromClick should move to backend and this will be accessible
def area_from_points(points):
    n = len(points)  # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += points[i][0] * points[j][1]
        area -= points[j][0] * points[i][1]
    area = abs(area) / 2.0
    return area


def sort_points(corners):
    # calculate centroid of the polygon
    n = len(corners) # of corners
    cx = float(sum(x for x, y in corners)) / n
    cy = float(sum(y for x, y in corners)) / n
    # create a new list of corners which includes angles
    cornersWithAngles = []
    for x, y in corners:
        dx = x - cx
        dy = y - cy
        an = (math.atan2(dy, dx) + 2.0 * math.pi) % (2.0 * math.pi)
        cornersWithAngles.append((dx, dy, an))
    # sort it using the angles
    cornersWithAngles.sort(key=lambda tup: tup[2])
    return cornersWithAngles
