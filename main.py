"""The program that creates the map using the folium library"""
import argparse
import re
from functools import lru_cache
import folium
from geopy import distance
from geopy.geocoders import Nominatim, ArcGIS


arcgis = ArcGIS(timeout=10)
nominatim = Nominatim(timeout=10, user_agent="justme")
geocoders = [arcgis, nominatim]


def main():
    """
    The main function that lanunches all the functions and creating the map.
    """
    year, latitude, longtitude, path = input_info()
    info_list = file_info(path, year)
    data = calculating_distances(latitude, longtitude, converting_places(info_list))
    creating_map(latitude, longtitude, data, year)


def input_info():
    """
    The function for user's inputs in terminal.
    """
    parser = argparse.ArgumentParser()

    # positional

    parser.add_argument("year", type=int, help="The year of the film")
    parser.add_argument("latitude", type=int, help="The latitude of the location")
    parser.add_argument("longtitude", type=int, help="The longtitude of the location")
    parser.add_argument("path", type=str, help="The path to the file")

    argums = parser.parse_args()

    return argums.year, argums.latitude, argums.longtitude, argums.path


def file_info(path: str, year: int):
    """
    The function reads the file, searches and saves only the needed years
    and returns the list that consist of title and place of film.
    Args:
        path (str): path to the file
        year (int): the year of the film

    Returns:
        [list]: consist of: [[title, place], [ , ]]
    Example:
    >>> type(file_info("locations.list", 1999))
    <class 'list'>
    """
    info_list = []
    with open(path, "r", encoding="UTF-8") as file:
        for line in file.readlines():
            process_data = []
            if "(" + str(year) + ")" in line:
                title = line[:line.index("(")].strip()
                process_data.append(title)
                sec_part = line[line.index(")") + 1:]
                place = re.sub(r'\([^()]*\)', "", sec_part).strip()
                process_data.append(place)
                info_list.append(process_data)
    return info_list


def converting_places(info: list):
    """
    The function launches the function that finds the city and
    the coordinates of film by address.
    >>> converting_places([['Serious Business', 'Chicago, Illinois, USA']])
    [(41.884250000000065, -87.63244999999995, 'Chicago, Illinois')]
    """
    data = []
    for item in info:
        data.append(getting_the_coords(item[1]))
    return data


@lru_cache(maxsize=None)
def getting_the_coords(address: str):
    """
    The function with geocode module finds and returns
    the coords and the city of film.
    >>> getting_the_coords('Chicago, Illinois')
    (41.884250000000065, -87.63244999999995, 'Chicago, Illinois')
    """
    i = 0
    try:
        location = geocoders[i].geocode(address)
        if location is not None:
            return location.latitude, location.longitude, location.address
        i += 1
        location = geocoders[i].geocode(address)
        if location is not None:
            return location.latitude, location.longitude, location.address
    except AttributeError:
        return None


def calculating_distances(lat: int, lon: int, data: list):
    """
    The function launches the other function that finds the distances between coordinates.
    Moreover, creates the dictionary, where keys are distances and returns it.
    >>> calculating_distances(20, 20, [(41.88425, -87.63245, 'Chicago, Illinois')])
    {9919.096357004097: (41.88425, -87.63245, 'Chicago, Illinois')}
    """
    dist_dict = dict()
    for item in data:
        dist_dict[distance_betw_points((lat, lon), (item[0], item[1]))] = item
    return dist_dict


def distance_betw_points(pair1: tuple, pair2: tuple):
    """
    The function finds and returns the distance in km(from coords).
    >>> distance_betw_points((5, 5), (10, 10))
    781.1062793857897
    """
    return distance.distance(pair1, pair2).km


def creating_map(lat: int, lon: int, data: dict, year: int):
    """
    The function create the html map with some layers and
    you can customize what you want.
    Args:
        lat (int): the inputed latitude
        lon (int): the inputed longtitude
        data (dict): the dictionary with distances and coords
        year (int): the year of the film
    """
    user_map = folium.Map(location=[lat, lon], zoom_start=5)

    html = """<h4>Movie information:</h4>
    Year: {},<br>
    Latitude: {},<br>
    Longtitude: {},<br>
    The place: {}
    """

    dist_sort = sorted(data)
    closest = folium.FeatureGroup(name="Closest movies")
    farest = folium.FeatureGroup(name="Farest movies")

    for num in range(10):
        iframe = folium.IFrame(html=html.format(year, data[dist_sort[num]][0],
        data[dist_sort[num]][1], data[dist_sort[num]][2]), width=300, height=100)

        closest.add_child(folium.Marker(location=[data[dist_sort[num]][0],
        data[dist_sort[num]][1]], popup=folium.Popup(iframe),
        icon=folium.Icon(color="blue")))
        user_map.add_child(closest)

    for num in range(10):
        dist_sort = sorted(dist_sort, reverse=True)
        iframe = folium.IFrame(html=html.format(year, data[dist_sort[num]][0],
        data[dist_sort[num]][1], data[dist_sort[num]][2]), width=300, height=100)

        farest.add_child(folium.Marker(location=[data[dist_sort[num]][0],
        data[dist_sort[num]][1]], popup=folium.Popup(iframe),
        icon=folium.Icon(color="red")))
        user_map.add_child(farest)
        dist_sort = sorted(dist_sort, reverse=True)

    user_map.add_child(folium.LayerControl())
    user_map.save("map.html")

if __name__ == "__main__":
    main()
