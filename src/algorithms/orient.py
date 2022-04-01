"""Functionallity to orient self from a map fragment."""
import numpy as np


def locate(matrix, fragment):
    """Locate map fragment within known map.
    Returns all potential locations of agent within matrix:
        - Multiple locations - ambiguous location, seek more data.
        - One location - located self.
        - No locations - no matching locations, agent is lost (check for mistakes in fragment?)

    Arguments:
        matrix: known map
        fragment: current known surroundings

    Output:
        locations: coordinate, orientation pairs for all pential locations.
    """

    matrix = (np,)

    # NOTE: if agent starts facing a rotation not tested, fragment will not match anywhere on map

    #  TODO: finish this function
    # for orientation in [0, 90, 180, 270]:
    #    rotated = np.rot90(matrix, k=(orientation / 90))
    #
    #
    #     for sub in fragment:

    # split fragments into sub-fragments
    # search for initial fragment, adding new fragments on previous success
    # rotate map to check if fragment is different orientation to map

    return locations


if __name__ == "__main__":
    """Test functionallity.

    Variables:
        matrix: a matrix representing the space the robot is in
        fragment: the fragment of the map the robot is currently in
        location: a list of nodes representing where the robot could be
    """
    matrix = [[1, 0, 1, 1], [1, 0, 1, 0], [1, 0, 1, 1], [1, 0, 0, 1], [1, 1, 1, 1]]
    fragment = [[-1, 0, 1], [-1, 0]]

    locations = locate()

    for coords, orientation in locations:
        x, y = coords
        print(f"{x}, {y}, {orientation} degrees.")
