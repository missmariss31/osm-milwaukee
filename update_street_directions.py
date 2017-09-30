d_mapping = {"N.": "North",
             "N": "North",
             "S.": "South",
             "S": "South",
             "E.": "East",
             "E": "East",
             "W.": "West",
             "W": "West",
             "SOUTH": "South"}

def update_direction(name, d_mapping):
    """Replace abbreviated street directions with full version using d_mapping"""
    name = name
    split_name = name.split(' ')
    
    for i in split_name:
        if i in d_mapping.keys():
            name = name.replace(i,d_mapping[i])

    return name

def change_direction(st_directions):
    """iterate through street directions and use helper function update_direction to update data"""
    for st_direction, ways in st_directions.iteritems():
            for name in ways:
                better_name = update_direction(name, d_mapping)
                print name, "=>", better_name