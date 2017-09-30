#Find problem characters/audit data
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys):
    """Element keys with all lowercase letters: add to 'lower'
    Element keys with lowercase letters and colon: add to 'lower_colon'
    Element keys with problem characters: add to 'problemchars'
    """
    if element.tag == "tag":
        
        if lower.search(element.attrib['k']):
            keys['lower'] += 1
        
        elif lower_colon.search(element.attrib['k']):
            keys['lower_colon'] += 1
        elif problemchars.search(element.attrib['k']):
            print element.attrib['k']
            keys['problemchars'] += 1
        
        else:
            keys['other'] += 1
        
    return keys

def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys)

    return keys