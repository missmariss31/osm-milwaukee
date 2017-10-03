
<b WRANGLE OPEN STREET MAP DATA >

#  WRANGLE OPENSTREETMAP DATA 
_____________________________________________________________________

## MILWAUKEE, WI, UNITED STATES

OpenStreetMap link to Milwaukee Map http://www.openstreetmap.org/relation/251075


<img src="bigphotoformilwaukee.jpg" align='left'>
### Milwaukee<br>
<b>City in Wisconsin</b><br>
*Google Search Info<br>
Milwaukee is a city in the U.S. state of Wisconsin on Lake Michigan's western shore. It's known for its breweries, many of which offer tours chronicling its role in the beer industry. Overlooking the Menomonee River, the Harley-Davidson Museum displays classic motorcycles, including one of Elvis Presley’s. Nearby is the Milwaukee Public Museum, with its large-scale European Village and a recreation of old Milwaukee.<br>

Population: 595,047 (2016)<br>
Zip code: 532XX<br>
Area code: Area code 414<br>

I chose Milwaukee because I grew up just north of the city.  I remember going to concerts, basketball games, and eating at some great restaurants downtown.  

In preparing to audit, clean, and explore the dataset, I gathered information from Udacity's Data Wrangling course.  I also gathered information from https://regexone.com/ when using regular expressions.  Most of the code seen in the street name/direction/postcode audits has been modified from Udacity's Data Wrangling quizzes, as well as code used when auditing problem characters and when validating and writing to CSV.

## Explore Sample Dataset
______________________________________________


```python
#import modules
#write/explore sample dataset

import xml.etree.ElementTree as ET
import re
import pprint

OSM_FILE = "Milwaukee_dataset.bz2.osm"
SAMPLE_FILE = "milw_sample.osm"

#run code to write SAMPLE_FILE

#%run sample.py
```

To familiarize myself with the elements in the dataset, I referenced [http://wiki.openstreetmap.org/wiki/Elements](OpenStreetMap Wiki)


```python
def count_tags(filename):
    """Count top level tags"""
    tag_count = {}
    osm_file = open(filename, "r")
    for each, elem in ET.iterparse(osm_file):
        if elem.tag in tag_count:
            tag_count[elem.tag] += 1
        else:
            tag_count[elem.tag] = 1
    return tag_count
```


```python
sample_tags = count_tags(SAMPLE_FILE)
sample_tags
```




    {'member': 637,
     'nd': 32148,
     'node': 24689,
     'osm': 1,
     'relation': 65,
     'tag': 17134,
     'way': 3244}



## PROBLEMS WITH DATA
___________________________________________

After looking over the sample osm file, I came across a few potential problems that I'd like to change.  Although there doesn't seem to be very many abbreviated street names within the "addr:street" tag key, there are a few that can be changed to full street type names.  Also, within the same field, we can change all "N", "S", "E", or "W" to "North", "South", "East", or "West".

I will also check that all postal codes start with "53" and are 5-digit codes.  Also, phone number formats may not be consistent and will need to be checked against a regular expression.  

Also, since we will be writing the data into CSV files, we'll need to check for commas within the data.

1.  Change abbreviated name/street types to non-abbreviated types (St=Street,Dr=Drive,etc.)

2.  Change all abbreviated street directions (N, S, E, W) to non abbreviated directions (North, South, East, West.)

3.  Check area codes (53XXX area code.)

4.  Check for the same phone number format (+1-555-555-5555) across all phone data.

5.  Check for commas and replace with underscore



## Street Types


```python
from collections import defaultdict


def print_sorted_dict(d):
    keys = d.keys()
    keys = sorted(keys, key=lambda s: s.lower())
    for k in keys:
        v = d[k]
        print "%s: %d" % (k, v) 

```


```python
def count_occur(reg_x, data_name, df_dict):
    """Count occurences of certain values within tags"""
    m = reg_x.search(data_name)
    if m:
        data_group = m.group()
        df_dict[data_group] += 1
```

*I did more generic functions here so that they could be used to audit/clean both street types and street directions.*


```python
def audit_data(file_name, is_func, reg_x):
    osm_file = open(file_name, "r")
    df_dict = defaultdict(int)
    for event, elem in ET.iterparse(osm_file):
        if is_func(elem):
            count_occur(reg_x, elem.attrib['v'], df_dict)
    print_sorted_dict(df_dict)
        
```


```python
def is_street_name(elem):
    """Find street names within tags"""
    return (elem.tag == "tag") and (elem.attrib['k'] == "addr:street")
```


```python
#regular expression to find street type
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)
```


```python
audit_data(SAMPLE_FILE, is_street_name, street_type_re)
#audit_data(OSM_FILE, is_street_name, street_type_re)
```

    Ave: 2
    Avenue: 91
    Boulevard: 1
    Court: 4
    Drive: 7
    Lane: 9
    Place: 22
    Rd: 1
    Road: 10
    Street: 149
    Way: 4
    Wells: 1
    

It's interesting that "Wells" shows up as one of the street types.  I'm pretty sure that "Wells" is not a street type, so I searched for "Wells" by pulling up my sample file and using CTRL F to find the full name quickly.  The results showed "W. Wells", which I know is "Wells Street" in Milwaukee.  So, I will have to add "Street" to that value and change "W." to "West" in order for the value to show "West Wells Street".


```python
# %load street_types.py
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons", "Way", "Circle", "Trace"]


def audit_street_type(street_types, street_name):
    """Check street type in data against expected types"""
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

            
def audit_street(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types
```


```python
#What needs fixing?

st_types = audit_street(SAMPLE_FILE)
#st_types = audit_street(OSM_FILE)
pprint.pprint(dict(st_types))
```

    {'Ave': set(['W North Ave']),
     'Rd': set(['N Green Bay Rd']),
     'Wells': set(['W. Wells'])}
    


```python
# %load update_street_type.py
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


```


```python
change_name(st_types) #shows before and after update
```

    N Green Bay Rd => N Green Bay Road
    W North Ave => W North Avenue
    W. Wells => W. Wells Street
    

## Street Direction


```python
#regular expression for cardinal directions
street_direction_re = re.compile(r'^([nsew]{1}\.? )|(north|south|east|west){1}[ ]{1}', re.IGNORECASE)
```


```python
audit_data(SAMPLE_FILE, is_street_name, street_direction_re)
#audit_data(OSM_FILE, is_street_name, street_direction_re)
```

    East : 58
    N : 1
    North : 164
    South : 13
    W : 2
    W. : 1
    West : 58
    


```python
# %load street_directions.py
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
```


```python
#What needs fixing?

#st_directions = audit_direction(OSM_FILE)
st_directions = audit_direction(SAMPLE_FILE)

pprint.pprint(dict(st_directions))
```

    {'N ': set(['N Green Bay Rd']),
     'W ': set(['W North Ave']),
     'W. ': set(['W. Wells'])}
    


```python
# %load update_street_directions.py
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
```


```python
change_direction(st_directions) #show before and after update
```

    N Green Bay Rd => North Green Bay Rd
    W. Wells => West Wells
    W North Ave => West North Ave
    

## Postal Codes


```python
# %load postcodes.py
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


def audit_zip(file_name):
    osm_file = open(file_name, "r")
    for event, elem in ET.iterparse(osm_file):
        if is_postal_code(elem):
            count_postal_code(postal_codes, elem.attrib['v'])  
            
    osm_file.close()
    return postal_codes

```


```python
fix_pc = audit_zip(SAMPLE_FILE)
#fix_pc = audit_zip(OSM_FILE)

pprint.pprint(dict(fix_pc))
```

    {'Milwaukee WI, 53222': 1}
    


```python
# %load update_postcodes.py
def change_zip(zip_code):
    """Isolate first 5 digits in value attribute"""
    find_zip_re = re.compile(r'(53\d{3})')
    m = find_zip_re.search(zip_code)
    if m:
        new_zip = m.group()
        return new_zip
    else:
        return zip_code
    
def update_postal_codes(fix_pc):
    for zip_code in fix_pc.keys():
        print zip_code, "=>", change_zip(zip_code)
```


```python
update_postal_codes(fix_pc)
```

    Milwaukee WI, 53222 => 53222
    

The problem with this way of cleaning postal codes is that it cuts out the last 4 digits of some codes that utilize the ZIP+4 system.  This may put the postal service at a disadvantage when someone uses an address from OSM.  However, the majority of postcode values are only 5 digits.  So, for the sake of conformity, we'll make sure they're all 5 digits.

## Phone Numbers

Proper Usage from http://wiki.openstreetmap.org/wiki/Key:phone
<br>
phone=number where the number should be in international (ITU-T E.164) format
<br>
phone=+[country_code] [area_code] [local_number], following the ITU-T E.123 and the DIN 5008 pattern
<br>
(phone=+[country_code]-[area_code]-[local_number], following the RFC 3966/NANP pattern)


```python
# %load phone_numbers.py
phone_re = re.compile(r'\+1[\s-]\d{3}[\s-]\d{3}[\s-]\d{4}$')

def is_phone_number(elem):
    return (elem.tag == "tag") and (elem.attrib['k'] == "contact:phone")

def find_phone_numbers(phone_number):
    """Find phone numbers that need fixing"""
    m = phone_re.search(phone_number)
    if not m:
        return phone_number


def audit_phone(file_name):
    with open(file_name, "r") as osm_file:
        num_list = []
        for event, elem in ET.iterparse(osm_file):
            if is_phone_number(elem):
                contact_num = find_phone_numbers(elem.attrib['v'])
                if contact_num != None:
                    num_list.append(contact_num)
        return num_list
     
```


```python
num_list = audit_phone(SAMPLE_FILE)
#num_list = audit_phone(OSM_FILE)

num_list
```




    ['+1.414.291.3900',
     '+1.414.227.4039',
     '+1.414.327.0166',
     '+1.414.353.3212',
     '+1.414.352.9525',
     '+1.414.874.8400',
     '+1.414.902.4400']




```python
# %load update_phone.py
#change periods to dashes
def update_number(num):
    new_num = num.replace(".","-",3)
    return new_num

def change_numbers(num_list):
    for num in num_list:
        print num, "=>", update_number(num)
```


```python
change_numbers(num_list)
```

    +1.414.291.3900 => +1-414-291-3900
    +1.414.227.4039 => +1-414-227-4039
    +1.414.327.0166 => +1-414-327-0166
    +1.414.353.3212 => +1-414-353-3212
    +1.414.352.9525 => +1-414-352-9525
    +1.414.874.8400 => +1-414-874-8400
    +1.414.902.4400 => +1-414-902-4400
    

Although the sample shows only numbers with the irregular character ".", there may be other numbers that do not conform to the pattern I set in the regular expression.  These could be changed using another function to address individual irregularities if need be.   

## Commas


```python
#use this function when cleaning, before writing to csv

def check_comma(elem):
    "Check for commas in element and replace with underscore"
    if ',' in elem:
        elem = elem.replace(',', '_')
        return elem
    else:
        return elem
```


```python
# %load problem_char.py
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
```


```python
#Process map and print out Problem Characters in OSM_FILE

keys = process_map(OSM_FILE)
```

    service area
    name:Washington County Commuter Express
    name:Washington County Commuter Express
    name:Washington County Commuter Express
    


```python
pprint.pprint(keys)
```

    {'lower': 187930, 'lower_colon': 149320, 'other': 4884, 'problemchars': 4}
    

## Clean Data and Write to CSV


```python
# %load clean_to_csv.py
#Modified code from Data Wrangling "Preparing for Database SQL" quiz

import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET

import cerberus

import schema


OSM_FILE = "Milwaukee_dataset.bz2.osm"

NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""

    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements
    
    count = 0 #way node position
    
    for i in element:
        
        if i.tag == 'tag':
            
            clean_v = None  #cleaned values: street names, postal codes, and phone numbers
            tag_dict = {}
            tag_dict['id'] = element.get('id')
            key_elem = i.get('k')
            value_elem = i.get('v')
            
            if not PROBLEMCHARS.search(key_elem):
                
                #clean street name
                if key_elem == "addr:street":
                    clean_v = update_type(value_elem, mapping) #clean type
                    clean_v = update_direction(clean_v, d_mapping) #clean direction
                             
                #clean postcodes            
                if key_elem == "addr:postcode":
                    clean_v = change_zip(value_elem)
                    
                #clean phone numbers    
                if key_elem == "contact:phone":
                    clean_v = update_number(value_elem)
                
                if clean_v != None:
                    clean_v = check_comma(clean_v)
                    tag_dict['value'] = clean_v
                    
                else:
                    tag_dict['value'] = value_elem
                    
                if LOWER_COLON.search(key_elem):
                    key_type = key_elem.split(':')
                    
                    if len(key_type) > 2:
                        tag_dict['key'] = ':'.join(key_type[1:])
                        tag_dict['type'] = key_type[0]
                        
                    else:
                        tag_dict['key'] = key_type[1]
                        tag_dict['type'] = key_type[0]
                        
                else:
                    tag_dict['key'] = key_elem
                    tag_dict['type'] = default_tag_type
            
                
            tags.append(tag_dict)
            
        if i.tag == 'nd':
            node_dict = {}
            node_dict['id'] = element.get('id')
            node_dict['node_id'] = i.get('ref')
            node_dict['position'] = count
            count += 1
            way_nodes.append(node_dict)
        
    
    if element.tag == 'node':
        for i in node_attr_fields:
            node_attribs[i] = element.get(i)
        return {'node': node_attribs, 'node_tags': tags}
        
    elif element.tag == 'way':
        for i in way_attr_fields:
            way_attribs[i] = element.get(i)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
```


```python
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
            
def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field, error_string))
        
        
class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
            
            
```


```python
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODE_TAGS_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
```


```python
#Clean and Write from OSM_FILE (Validate using SAMPLE_FILE)

#process_map(SAMPLE_FILE, validate=True)
#process_map(OSM_FILE, validate= False)
```

## STATISTICS OF DATASET

**File Sizes**

```
OSM_FILE .............  115 MB (120,673,495 bytes)
SAMPLE_FILE .......... 5.67 MB (5,950,406 bytes)
milw_osm.db .......... 60.0 MB (62,936,064 bytes)
nodes.csv ............ 39.8 MB (41,784,324 bytes)
nodes_tags.csv ....... 2.24 MB (2,350,587 bytes)
ways.csv ............. 3.80 MB (3,987,210 bytes)
ways_nodes.csv ....... 15.3 MB (16,146,938 bytes)
ways_tags.csv ........ 9.51 MB (9,972,938 bytes)
```

**Import CSVs into milw_osm.db**


```sqlite3
.mode csv
.import nodes.csv nodes
.import nodes_tags.csv nodes_tags
.import ways.csv ways
.import ways_nodes.csv ways_nodes
.import ways_tags.csv ways_tags
```

**Query Number of Nodes and Ways**


```sqlite3
SELECT count(*) FROM nodes;
493767
```


```sqlite3
SELECT count(*) FROM ways;
64879
```


**Number of Unique Users**

```sqlite3
SELECT COUNT(DISTINCT(user)) FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways);
485
```


**Count number of alternate names recorded**

```sqlite3
SELECT COUNT(*) FROM (SELECT key FROM nodes_tags UNION ALL SELECT key FROM ways_tags) WHERE key="alt_name";
213
```


**Places with alternate names in Milwaukee (Limit 10)**

It's interesting to see what "alternate names" are used to describe some of the businesses/buildings/streets in the Milwaukee area, although some of them seem to be the actual legal business name.

```sqlite 
SELECT value FROM (SELECT key,value FROM nodes_tags UNION ALL SELECT key,value FROM ways_tags) WHERE key="alt_name" LIMIT 10; 

"Milwaukee County Mental Health Complex"                                                        
"STD Clinic"                                                                                    
"Kinko's"                                                                                       
"The Polish Moon"                                                                               
"Riverwest grocery Cooperative"                                                                 
"Wisconsin Housing and Economic Development Authority"                                          
TWC                                                                                             
"Milwaukee's Original Haus Party"                                                             
"Irish Fest"                                                                                    
"Thomas A. Greene Memorial Museum"

```

**Are there any areas in Milwaukee that allow access to horse riders?**

```sqlite3
 SELECT value,COUNT(*) FROM (SELECT key,value FROM nodes_tags UNION ALL SELECT key,value FROM ways_tags) WHERE key="horse" GROUP BY value;
 
 no,331
 unknown,4
 yes,1
```
I wonder what that 1 area in Milwaukee is?  I'm guessing it's at the lakefront.


## ADDITIONAL IMPROVEMENTS
______________________________________________________

-  Clean up more of the phone numbers that are not in the correct format
-  Check county and take out any that are not Milwaukee County
-  Check for valid websites

**PHONE NUMBERS**: If all phone numbers are in the correct format, they can be used by developers/users for auto dialing purposes.  However, not everyone will want the chosen format for one reason or another.  Can't please 'em all!
```sqlite3
SELECT value FROM (SELECT key,value FROM nodes_tags UNION ALL SELECT key,value FROM ways_tags) WHERE key="phone" LIMIT 10;

"+1-(414) 604-7800"
"(414) 875-4500"
"+1-(414) 294-1200"
+1-414-393-4900
"+1-(414) 902-9500"
+1-414-267-0700
"+1-(414) 578-5100"
"+1-(414) 393-4800"
+1-414-463-3878
+1-414-267-0500
```

**COUNTY**: Some counties listed may not be listed as Milwaukee County, although the zipcode may start with "53".  We can get rid of these values completely or keep them in for continued reference.  The counties listed may be surrounding areas with important landmarks that may help someone navigating the Milwaukee area, so it may be best to keep them in the dataset.

```sqlite3
SELECT value FROM (SELECT key,value FROM nodes_tags UNION ALL SELECT key,value FROM ways_tags) WHERE key="county" AND value!="Milwaukee, WI" LIMIT 10; 

"Milwaukee, WI;Waukesha, WI"
"Milwaukee, WI; Waukesha, WI"
"Washington, WI"
"Washington, WI"
"Washington, WI"
"Washington, WI"
"Washington, WI"
"Washington, WI"
"Washington, WI"
"Washington, WI"
```

**VALID WEBSITE**: Some websites may not be valid and therefore unuseable to those that are trying to contact local businesses/individuals.  However, if we get rid of all invalid web addrs programmatically using a specific 'http' format, we may get rid of some that could have otherwise been deciphered manually and converted to a valid web address.

```sqlite3
SELECT value FROM (SELECT key,value FROM nodes_tags UNION ALL SELECT key,value FROM ways_tags) WHERE key="website" AND value NOT LIKE 'http%' LIMIT 20;

www.millertimepub.com
www.waterstreetbrewery.com
www.elsas.com
www.louiseswisconsin.com
www.coastrestaurant.com/
www.thecheesecakefactory.com
www.uwcu.org
mabaensch.com
riverwestcoop.org
trulyspokencycles.net
outpostnaturalfoods.coop
elreyfoods.publishpath.com
chickenpalacewi.com
aldi.us
advanceautoparts.com
napaonline.com
walgreens.com
bk.com
radioshack.com
nationalace.com     
```
