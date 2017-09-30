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


