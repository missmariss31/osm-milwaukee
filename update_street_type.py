mapping = { "St": "Street",
            "St.": "Street",
            "Ave": "Avenue",
            "Ave.": "Avenue",
            "PL": "Place",
            "Rd": "Road",
            "Rd.": "Road",
            "Cir.": "Circle",
            "Providence": "Providence Avenue",
            "Wells": "Wells Street"
           }
           
                
def update_type(name, mapping):
    """Replace abbreviated street type with full version using mapping"""
    name = name
    split_name = name.split(' ')
    
    for i in split_name:
        if i in mapping.keys():
            name = name.replace(i,mapping[i])

    return name

def change_name(st_types):
    """iterate through street types and use helper function update_name to update data"""
    for st_type, ways in st_types.iteritems():
            for name in ways:
                better_name = update_type(name, mapping)
                print name, "=>", better_name

