d_expected = ["North ", "South ", "East ", "West "]

def audit_street_direction(street_directions, street_name):
    m = street_direction_re.search(street_name)
    if m:
        street_direction = m.group()
        if street_direction not in d_expected:
            street_directions[street_direction].add(street_name)
            
            
def audit_direction(osmfile):
    
    osm_file = open(osmfile, "r")
    street_directions = defaultdict(set)
    
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_direction(street_directions, tag.attrib['v'])
                    
    osm_file.close()
    
    return street_directions