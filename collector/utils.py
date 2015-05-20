import itertools


def flatten(list_of_list):
    """ Takes list_of_list as an input, returns flat list """
    return list(itertools.chain(*list_of_list))
