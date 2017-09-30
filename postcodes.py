postal_codes = defaultdict(int)

#regular expression for postal codes
postal_code_re = re.compile(r'^[5][3]\d{3}$')

def is_postal_code(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:postcode")

def count_postal_code(postal_codes, postal_code):
    """Count number of each unconventional postal code"""
    m = postal_code_re.search(postal_code)
    if not m:

        postal_codes[postal_code] += 1


def audit_zip():
    osm_file = open(SAMPLE_FILE, "r")
    for event, elem in ET.iterparse(osm_file):
        if is_postal_code(elem):
            count_postal_code(postal_codes, elem.attrib['v'])  
            
    osm_file.close()
    return postal_codes
