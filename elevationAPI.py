from googlemaps import convert

def elevation(client, locations):
    """
    Provides elevation data for locations provided on the surface of the
    earth, including depth locations on the ocean floor (which return negative
    values)

    :param locations: List of latitude/longitude values from which you wish
        to calculate elevation data.
    :type locations: a single location, or a list of locations, where a
        location is a string, dict, list, or tuple

    :rtype: list of elevation data responses
    """
    params = {"locations": convert.shortest_path(locations)}
    return client._request("/maps/api/elevation/json", params).get("results", [])


def elevation_along_path(client, path, samples):
    """
    Provides elevation data sampled along a path on the surface of the earth.

    :param path: An encoded polyline string, or a list of latitude/longitude
        values from which you wish to calculate elevation data.
    :type path: string, dict, list, or tuple

    :param samples: The number of sample points along a path for which to
        return elevation data.
    :type samples: int

    :rtype: list of elevation data responses
    """

    if type(path) is str:
        path = "enc:%s" % path
    else:
        path = convert.shortest_path(path)

    params = {
        "path": path,
        "samples": samples
    }

    return client._request("/maps/api/elevation/json", params).get("results", [])