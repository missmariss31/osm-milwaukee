phone_re = re.compile(r'\+1[\s-]\d{3}[\s-]\d{3}[\s-]\d{4}$')

def is_phone_number(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "contact:phone")

def find_phone_numbers(phone_number):
    """Find phone numbers that need fixing"""
    m = phone_re.search(phone_number)
    if not m:
        return phone_number


def audit_phone():
    with open(SAMPLE_FILE, "r") as osm_file:
        num_list = []
        for event, elem in ET.iterparse(osm_file):
            if is_phone_number(elem):
                contact_num = find_phone_numbers(elem.attrib['v'])
                if contact_num != None:
                    num_list.append(contact_num)
        return num_list
     